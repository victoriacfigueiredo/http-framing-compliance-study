# RQ-013 — Transfer-Encoding in HTTP/1.0

## Requirement

RFC 9112 defines `Transfer-Encoding` as an HTTP/1.1 message framing mechanism.

A sender MUST NOT send a request containing `Transfer-Encoding` unless it knows that the recipient supports HTTP/1.1 or later. Recipients that receive such requests are expected to treat the message as faulty framing information and avoid forwarding it unchanged.

---

## Test Objective

Evaluate how HTTP intermediaries handle HTTP/1.0 requests containing a `Transfer-Encoding: chunked` header and determine whether the request is rejected, normalized, or forwarded unchanged to the backend application.

---

## Expected Behavior

According to RFC 9112:

* `Transfer-Encoding` is not a valid framing mechanism for HTTP/1.0.
* The recipient should reject the request or normalize it before forwarding.
* The request should not be forwarded unchanged as an HTTP/1.0 message containing `Transfer-Encoding`.
* Message framing ambiguity must be prevented.

Any implementation that forwards an HTTP/1.0 request with `Transfer-Encoding` unchanged to the backend is considered non-compliant with the RFC requirements.

---

## Test Payload

```http
POST /test HTTP/1.0
Host: localhost
Transfer-Encoding: chunked

0

```

The request intentionally uses HTTP/1.0 while simultaneously declaring `Transfer-Encoding: chunked`.

---

## Nginx

### Response

```http
HTTP/1.1 400 Bad Request
```

### Backend Observation

The request was not forwarded to the backend application.

### Analysis

Nginx rejected the malformed request before forwarding it downstream.

### Compliance Status

**Compliant**

### Notes

Nginx follows a strict rejection strategy when receiving HTTP/1.0 requests containing unsupported framing information.

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
  "request_version": "HTTP/1.0",
  "headers": {
    "host": "localhost",
    "transfer-encoding": "chunked"
  },
  "body": "",
  "body_read_error": null
}
```

### Analysis

HAProxy forwarded the request unchanged to the backend.

The backend confirmed that:

* the request version remained `HTTP/1.0`;
* the `Transfer-Encoding: chunked` header remained present;
* the request was successfully processed.

This behavior preserves invalid framing semantics and directly contradicts the RFC expectation that such requests should be rejected or normalized before forwarding.

### Compliance Status

**Non-Compliant**

### Notes

The proxy neither rejected the request nor removed the invalid framing information before forwarding it downstream.

---

## Envoy

### Response

```http
HTTP/1.1 426 Upgrade Required
```

### Backend Observation

The request was not forwarded to the backend application.

### Analysis

Envoy rejected the request and required a protocol upgrade before processing.

### Compliance Status

**Compliant**

### Notes

Although Envoy uses a different status code than Nginx, it prevents the invalid request from reaching the backend application.

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
    "Content-Length": "0"
  },
  "body": "",
  "body_read_error": null
}
```

### Analysis

Traefik removed the `Transfer-Encoding` header and normalized the request before forwarding it.

The backend received a valid HTTP/1.1 request framed using `Content-Length: 0`.

### Compliance Status

**Compliant**

### Notes

Traefik follows a normalization strategy rather than rejecting the request outright.

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
    "Content-Length": "0",
    "Via": "1.0 Caddy"
  },
  "body": "",
  "body_read_error": null
}
```

### Analysis

Caddy removed the invalid `Transfer-Encoding` header and normalized the request before forwarding it.

The backend received a valid request framed using `Content-Length: 0`.

### Compliance Status

**Compliant**

### Notes

Caddy adopts a normalization strategy similar to Traefik.

---

## Summary

| Implementation | Backend Reached | Observed Behavior                                             | Compliance    |
| -------------- | --------------- | ------------------------------------------------------------- | ------------- |
| Nginx          | No              | Rejected request with 400 Bad Request                         | Compliant     |
| HAProxy        | Yes             | Forwarded HTTP/1.0 request with Transfer-Encoding unchanged   | Non-Compliant |
| Envoy          | No              | Rejected request with 426 Upgrade Required                    | Compliant     |
| Traefik        | Yes             | Removed Transfer-Encoding and normalized to Content-Length: 0 | Compliant     |
| Caddy          | Yes             | Removed Transfer-Encoding and normalized to Content-Length: 0 | Compliant     |

---

## Key Observation

The evaluated implementations adopt substantially different strategies when handling `Transfer-Encoding` in HTTP/1.0 requests.

Nginx and Envoy reject the request before it reaches the backend application. Traefik and Caddy normalize the request by removing the unsupported framing mechanism and forwarding a valid request downstream.

HAProxy, however, forwards the request unchanged while preserving both the HTTP/1.0 version and the `Transfer-Encoding: chunked` header. The backend logs confirm that the invalid framing information remained intact throughout the forwarding process.

This behavior constitutes a confirmed RFC 9112 compliance violation under the tested configuration and represents one of the most significant interoperability differences identified during the evaluation.
