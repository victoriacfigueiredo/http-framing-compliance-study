# RQ-009 — Host Header Validation

## Requirement

RFC 9112 states that a server MUST respond with a `400 Bad Request` status code to any HTTP/1.1 request message that:

* lacks a `Host` header field;
* contains more than one `Host` header field;
* contains a `Host` header field with an invalid value.

This requirement is mandatory for all HTTP/1.1 requests.

---

## Test Objective

Evaluate whether HTTP intermediaries correctly enforce the HTTP/1.1 requirement for the presence of a valid `Host` header and reject requests that do not comply.

---

## Expected Behavior

According to RFC 9112:

* Every HTTP/1.1 request MUST contain exactly one valid `Host` header field.
* Requests lacking a `Host` header MUST be rejected.
* The server MUST respond with `400 Bad Request`.
* The request MUST NOT be forwarded to the backend application.

Any implementation that forwards or processes an HTTP/1.1 request without a `Host` header is considered non-compliant with the RFC requirement.

---

## Test Payload

```http
GET /test HTTP/1.1
X-Test-Case: RQ-009-MISSING-HOST
Connection: close
```

The request intentionally omits the `Host` header while remaining otherwise valid.

---

## Nginx

### Response

```http
HTTP/1.1 400 Bad Request
```

### Backend Observation

The request was not forwarded to the backend application.

No corresponding request containing the `X-Test-Case: RQ-009-MISSING-HOST` header was observed in the backend logs.

### Analysis

Nginx correctly identified the missing `Host` header and rejected the request before forwarding it to the backend.

### Compliance Status

**Compliant**

### Notes

Nginx follows the RFC 9112 requirement to reject HTTP/1.1 requests that lack a `Host` header field.

---

## HAProxy

### Response

```http
HTTP/1.0 200 OK
```

### Backend Observation

The request was forwarded to the backend application.

The backend received:

```json
{
  "method": "GET",
  "path": "/test",
  "request_version": "HTTP/1.1",
  "headers": {
    "x-test-case": "RQ-009-MISSING-HOST"
  },
  "body": "",
  "body_read_error": null
}
```

### Analysis

HAProxy forwarded an HTTP/1.1 request that did not contain a `Host` header field.

The backend confirmed that:

* the request version remained `HTTP/1.1`;
* no `Host` header was present;
* the request was successfully processed.

This behavior directly contradicts the RFC 9112 requirement that such requests MUST be rejected with `400 Bad Request`.

### Compliance Status

**Non-Compliant**

### Notes

The isolated validation confirmed that HAProxy neither rejected the request nor inserted a valid `Host` header before forwarding it downstream.

---

## Summary

| Implementation | Response        | Backend Reached | Compliance    |
| -------------- | --------------- | --------------- | ------------- |
| Nginx          | 400 Bad Request | No              | Compliant     |
| HAProxy        | 200 OK          | Yes             | Non-Compliant |

---

## Key Observation

A significant behavioral difference was observed between the evaluated implementations.

Nginx strictly enforces the RFC 9112 requirement for the presence of a `Host` header in HTTP/1.1 requests and rejects malformed requests before they reach the backend application.

In contrast, HAProxy forwards HTTP/1.1 requests that lack a `Host` header and allows them to be processed by the backend. The backend logs confirm that the request remained HTTP/1.1 and contained no `Host` header after forwarding.

This result constitutes a confirmed RFC 9112 compliance violation under the tested configuration and represents the strongest interoperability divergence identified during the evaluation.
