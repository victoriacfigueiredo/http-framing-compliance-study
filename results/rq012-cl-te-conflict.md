Segue no mesmo formato:

# RQ-012 — Content-Length and Transfer-Encoding Conflict

## Requirement

RFC 9112 states that when a request contains both `Content-Length` and `Transfer-Encoding`, the recipient MAY either reject the message or process it according to the `Transfer-Encoding` semantics.

However, regardless of the chosen processing strategy, the recipient MUST close the connection after responding to the request in order to prevent message framing ambiguities.

---

## Test Objective

Evaluate how HTTP intermediaries handle requests containing both `Content-Length` and `Transfer-Encoding` headers and verify whether the connection is correctly terminated after the response.

---

## Expected Behavior

According to RFC 9112:

* A request containing both `Content-Length` and `Transfer-Encoding` may either be rejected or processed according to `Transfer-Encoding`.
* If the request is processed, the conflicting `Content-Length` header should not be used for message framing.
* The recipient MUST close the connection after responding.
* No subsequent request should be processed on the same TCP connection.

Any implementation that keeps the connection reusable after processing a conflicting request is considered non-compliant with the RFC requirement.

---

## Test Payload

```http
POST /test HTTP/1.1
Host: localhost
X-Test-Case: RQ-012-CLTE-REUSE
Content-Length: 5
Transfer-Encoding: chunked

0

HELLO
```

After receiving the response, a second request was sent through the same TCP connection:

```http
GET /second HTTP/1.1
Host: localhost
```

---

## Nginx

### Response

```http
HTTP/1.1 400 Bad Request
Connection: close
```

### Backend Observation

The request was not forwarded to the backend application.

### Analysis

Nginx rejected the conflicting request before forwarding it and immediately closed the connection.

The second request could not be processed because the connection had already been terminated.

### Compliance Status

**Compliant**

### Notes

Nginx follows the rejection path explicitly permitted by RFC 9112 and correctly closes the connection after responding.

---

## HAProxy

### Response

```http
HTTP/1.0 200 OK
```

### Backend Observation

The backend received:

```json
{
  "method": "POST",
  "path": "/test",
  "headers": {
    "host": "localhost",
    "transfer-encoding": "chunked"
  },
  "body": ""
}
```

### Analysis

HAProxy processed the request according to the `Transfer-Encoding` semantics and removed the conflicting `Content-Length` header before forwarding it.

The connection was terminated after the response and the second request could not be processed.

### Compliance Status

**Compliant**

### Notes

HAProxy adopts a normalization strategy rather than rejection, but still satisfies the RFC requirement to close the connection afterward.

---

## Envoy

### Response

```http
HTTP/1.1 400 Bad Request
```

### Backend Observation

The request was not forwarded to the backend application.

### Analysis

Envoy rejected the conflicting framing information before backend processing and did not allow connection reuse.

### Compliance Status

**Compliant**

### Notes

Envoy behaved similarly to Nginx in the tested scenario.

---

## Traefik

### Response

```http
HTTP/1.1 200 OK
```

### Backend Observation

The backend received:

```json
{
  "method": "POST",
  "path": "/test",
  "request_version": "HTTP/1.1",
  "headers": {
    "Host": "localhost",
    "Transfer-Encoding": "chunked",
    "X-Test-Case": "RQ-012-CLTE-REUSE"
  }
}
```

After the second request was transmitted on the same TCP connection, the backend logged:

```http
HELLOGET /second HTTP/1.1
```

and returned:

```http
501 Not Implemented
Unsupported method ('HELLOGET')
```

### Analysis

Traefik processed the request according to `Transfer-Encoding` but failed to close the connection afterward.

Residual bytes from the original request body (`HELLO`) remained in the connection and were interpreted as part of the next request line, resulting in the malformed method `HELLOGET`.

This behavior directly contradicts the RFC 9112 requirement that the connection MUST be closed after processing a request containing both `Content-Length` and `Transfer-Encoding`.

### Compliance Status

**Non-Compliant**

### Notes

The isolated reuse test confirmed that Traefik allowed connection reuse after processing conflicting framing information.

---

## Caddy

### Response

```http
HTTP/1.1 200 OK
```

### Backend Observation

The backend received:

```json
{
  "method": "POST",
  "path": "/test",
  "request_version": "HTTP/1.1",
  "headers": {
    "Host": "localhost",
    "Transfer-Encoding": "chunked",
    "Via": "1.1 Caddy",
    "X-Test-Case": "RQ-012-CLTE-REUSE"
  }
}
```

After the second request was transmitted on the same TCP connection, the backend logged:

```http
HELLOGET /second HTTP/1.1
```

and returned:

```http
501 Not Implemented
Unsupported method ('HELLOGET')
```

### Analysis

Caddy processed the conflicting request but failed to terminate the connection afterward.

Residual bytes from the original request remained available for parsing and contaminated the next request, producing the malformed method `HELLOGET`.

This behavior violates the RFC requirement that the connection MUST be closed after responding.

### Compliance Status

**Non-Compliant**

### Notes

The isolated validation reproduced the issue consistently and demonstrated connection reuse despite conflicting framing information.

---

## Summary

| Implementation | Behavior                                                            | Connection Closed | Compliance    |
| -------------- | ------------------------------------------------------------------- | ----------------- | ------------- |
| Nginx          | Rejects request with 400 Bad Request                                | Yes               | Compliant     |
| HAProxy        | Processes according to Transfer-Encoding and removes Content-Length | Yes               | Compliant     |
| Envoy          | Rejects request with 400 Bad Request                                | Yes               | Compliant     |
| Traefik        | Processes request and allows connection reuse                       | No                | Non-Compliant |
| Caddy          | Processes request and allows connection reuse                       | No                | Non-Compliant |

---

## Key Observation

This requirement produced the strongest interoperability divergence observed during the evaluation.

Nginx and Envoy reject the conflicting request, while HAProxy normalizes and forwards it according to `Transfer-Encoding`. Although these implementations adopt different strategies, all correctly terminate the connection afterward and therefore comply with RFC 9112.

In contrast, both Traefik and Caddy process the request and keep the connection reusable. Residual bytes from the original request body remain available in the connection state and contaminate the next request, producing the malformed request line `HELLOGET /second HTTP/1.1`.

The observed behavior directly contradicts the RFC 9112 requirement that the connection MUST be closed after processing a request containing both `Content-Length` and `Transfer-Encoding`, resulting in confirmed compliance violations under the tested configurations.
