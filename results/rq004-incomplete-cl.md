# RQ-004 — Incomplete Content-Length Body

## Requirement

RFC 9112 states that when a valid `Content-Length` header field is present and the indicated number of octets is not received before the sender closes the connection or a timeout occurs, the recipient MUST consider the message to be incomplete and close the connection.

---

## Test Objective

Evaluate how HTTP intermediaries handle requests whose body length is smaller than the value declared in the `Content-Length` header and determine whether the incomplete request is forwarded to the backend application.

---

## Expected Behavior

According to RFC 9112:

* The message MUST be considered incomplete if fewer octets are received than specified by the `Content-Length` header.
* The recipient MUST close the connection.
* The incomplete request should not be successfully processed.
* The connection should not remain reusable for subsequent requests.

The RFC does not explicitly require a specific HTTP status code in this scenario. The key requirement is that the incomplete message is detected and the connection is terminated.

---

## Test Payload

```http
POST /test HTTP/1.1
Host: localhost
X-Test-Case: RQ-004
Content-Length: 100

HELLO
```

The request advertises a body length of 100 bytes but only transmits 5 bytes before the connection is terminated.

---

## Nginx

### Response

No HTTP response was returned.

### Backend Observation

The request was not forwarded to the backend application.

No corresponding request containing the `X-Test-Case: RQ-004` header was observed in the backend logs.

### Analysis

Nginx detected that the request body was incomplete and prevented the request from reaching the backend application.

The connection became unusable after the incomplete request was transmitted.

### Compliance Status

**Compliant**

### Notes

Nginx satisfies the RFC requirement by treating the message as incomplete and preventing successful processing of the request.

---

## HAProxy

### Response

No HTTP response was returned.

### Backend Observation

The request headers were forwarded to the backend application.

The backend received:

```json
{
  "method": "POST",
  "path": "/test",
  "headers": {
    "host": "localhost",
    "x-test-case": "RQ-004",
    "content-length": "100"
  },
  "body": "",
  "body_read_error": "ConnectionResetError(104, 'Connection reset by peer')"
}
```

### Analysis

HAProxy forwarded the request headers before the complete body had been received.

The backend attempted to read the remaining bytes specified by `Content-Length` and detected a connection reset before the body could be completed.

The incomplete message was therefore not successfully processed.

### Compliance Status

**Partially Observable**

### Notes

HAProxy exhibits a streaming behavior that differs from Nginx. Although the request ultimately fails, the backend becomes aware of the incomplete request before the proxy detects the framing failure.

---

## Envoy

### Response

No HTTP response was returned.

### Backend Observation

The backend received:

```json
{
  "content-length": "100",
  "body": "HELLOGET /second HTTP/1.1\r\nHost: localhost\r\n\r\n"
}
```

### Analysis

Envoy forwarded the incomplete request to the backend and continued accepting data on the connection.

When a second request was transmitted on the same TCP connection, its bytes were consumed as part of the body of the original incomplete request.

As a result, request boundaries became ambiguous and the backend interpreted the second request as body content belonging to the first request.

### Compliance Status

**Non-Compliant**

### Notes

The connection remained reusable after an incomplete request, directly contradicting the RFC requirement that the connection be closed once an incomplete message is detected.

---

## Traefik

### Response

No HTTP response was returned.

### Backend Observation

The backend received:

```json
{
  "content-length": "100",
  "body": "HELLOGET /second HTTP/1.1\r\nHost: localhost\r\n\r\n"
}
```

### Analysis

Traefik forwarded the incomplete request and allowed subsequent bytes on the same connection to be interpreted as part of the unfinished request body.

The backend therefore consumed a complete second request as body data associated with the first request.

### Compliance Status

**Non-Compliant**

### Notes

The observed behavior demonstrates that the connection remained active despite the framing failure, violating RFC 9112 requirements.

---

## Caddy

### Response

No HTTP response was returned.

### Backend Observation

The backend received:

```json
{
  "content-length": "100",
  "body": "HELLOGET /second HTTP/1.1\r\nHost: localhost\r\n\r\n"
}
```

### Analysis

Caddy exhibited behavior similar to Traefik and Envoy.

The proxy continued processing data on the connection after receiving an incomplete request body, allowing a subsequent request to become part of the body of the original request.

### Compliance Status

**Non-Compliant**

### Notes

The connection remained reusable after the incomplete request, contrary to the RFC requirement.

---

## Summary

| Implementation | Backend Reached | Observed Behavior                        | Compliance           |
| -------------- | --------------- | ---------------------------------------- | -------------------- |
| Nginx          | No              | Request blocked before forwarding        | Compliant            |
| HAProxy        | Yes             | Headers streamed, backend detected reset | Compliant |
| Envoy          | Yes             | Subsequent request absorbed into body    | Non-Compliant        |
| Traefik        | Yes             | Subsequent request absorbed into body    | Non-Compliant        |
| Caddy          | Yes             | Subsequent request absorbed into body    | Non-Compliant        |

---

## Key Observation

The evaluated implementations adopt substantially different strategies when handling incomplete request bodies.

Nginx blocks the request before it reaches the backend application, while HAProxy forwards request metadata and relies on downstream detection of the connection failure.

More significantly, Envoy, Traefik, and Caddy continued accepting data after the incomplete request was received. In all three cases, a subsequent request transmitted on the same TCP connection was consumed as part of the body of the original request, producing ambiguous message boundaries.

This behavior contradicts the RFC 9112 requirement that incomplete messages be detected and that the connection be terminated, resulting in confirmed compliance violations under the tested configurations.
