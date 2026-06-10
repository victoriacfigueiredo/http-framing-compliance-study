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

HAProxy forwarded the request headers to the backend before the complete request body had been received.

The backend attempted to read the remaining bytes specified by the `Content-Length` header but encountered a connection reset before the body could be completed.

As a result, the incomplete message was not successfully processed.

### Compliance Status

**Partially Observable**

### Notes

The observed behavior differs from Nginx. While the incomplete request was not successfully processed, HAProxy streamed the request headers to the backend before body completion.

Further investigation would be required to determine whether this behavior is fully consistent with the intended interpretation of RFC 9112 in reverse-proxy deployments.

---

## Summary

| Implementation | Response    | Backend Reached    | Compliance           |
| -------------- | ----------- | ------------------ | -------------------- |
| Nginx          | No Response | No                 | Compliant            |
| HAProxy        | No Response | Yes (Headers Only) | Partially Observable |

---

## Key Observation

The evaluated implementations adopt different strategies when handling incomplete request bodies.

Nginx blocks the incomplete request before it reaches the backend application, whereas HAProxy forwards the request headers immediately and relies on the backend connection state to detect that the body was not fully transmitted.

Although neither implementation successfully processes the incomplete request, the difference highlights distinct forwarding behaviors that may influence backend error handling and request-processing semantics.
