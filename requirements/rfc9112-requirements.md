# RFC 9112 Requirements Catalog

## Scope

This catalog contains the RFC 9112 requirements selected for compliance evaluation. The focus is on HTTP/1.1 message framing, parsing behavior, request delimitation, and requirements historically associated with request smuggling and HTTP desynchronization vulnerabilities.

---

# RQ-001

**Title:** Invalid Content-Length Handling

**RFC Section:** RFC 9112 §6.3

**Normative Level:** MUST

**Security Relevance:**

* Message Framing
* Request Smuggling
* HTTP Desynchronization

**Requirement Summary:**
Messages containing an invalid Content-Length header field and no Transfer-Encoding must be treated as framing errors. Invalid requests must receive a 400 response and the connection must be closed.

**Expected Behavior:**
The implementation rejects malformed Content-Length values and terminates the connection.

---

# RQ-002

**Title:** Bare Carriage Return Handling

**RFC Section:** RFC 9112 §2.2

**Normative Level:** MUST / MUST NOT

**Security Relevance:**

* Parser Discrepancies
* Request Smuggling

**Requirement Summary:**
A sender must not generate bare CR characters outside message content. Recipients must reject or sanitize them before processing.

**Expected Behavior:**
Requests containing bare CR characters in protocol elements are rejected or safely normalized.

---

# RQ-003

**Title:** Whitespace Before First Header

**RFC Section:** RFC 9112 §2.2

**Normative Level:** MUST

**Security Relevance:**

* Parser Discrepancies
* Request Smuggling

**Requirement Summary:**
Whitespace between the start-line and the first header field must either cause rejection or be completely ignored.

**Expected Behavior:**
The implementation does not interpret whitespace-prefixed lines as valid headers.

---

# RQ-004

**Title:** Incomplete Content-Length Body

**RFC Section:** RFC 9112 §6.3

**Normative Level:** MUST

**Security Relevance:**

* Message Framing
* Connection Handling

**Requirement Summary:**
When fewer bytes than specified by Content-Length are received, the message must be treated as incomplete and the connection must be closed.

**Expected Behavior:**
Partial request bodies do not remain in buffers for future parsing.

---

# RQ-005

**Title:** Chunked Transfer Coding Support

**RFC Section:** RFC 9112 §7.1

**Normative Level:** MUST

**Security Relevance:**

* Message Framing

**Requirement Summary:**
Recipients must correctly parse and decode chunked transfer coding.

**Expected Behavior:**
Valid chunked messages are accepted and decoded correctly.

---

# RQ-006

**Title:** Large Chunk Size Handling

**RFC Section:** RFC 9112 §7.1

**Normative Level:** MUST

**Security Relevance:**

* Parser Robustness
* Integer Overflow Prevention

**Requirement Summary:**
Recipients must safely handle very large hexadecimal chunk sizes without integer overflow or precision loss.

**Expected Behavior:**
Large chunk-size values do not cause parsing failures or unexpected behavior.

---

# RQ-007

**Title:** Unknown Chunk Extensions

**RFC Section:** RFC 9112 §7.1.1

**Normative Level:** MUST

**Security Relevance:**

* Parsing Consistency

**Requirement Summary:**
Recipients must ignore unrecognized chunk extensions.

**Expected Behavior:**
Unknown chunk extensions do not affect request interpretation.

---

# RQ-008

**Title:** Invalid HTTP Message Grammar

**RFC Section:** RFC 9112 §2

**Normative Level:** SHOULD

**Security Relevance:**

* Request Smuggling
* Parser Robustness

**Requirement Summary:**
Messages that do not conform to HTTP grammar should receive a 400 response and the connection should be closed.

**Expected Behavior:**
Malformed requests are rejected consistently.

---

# RQ-009

**Title:** Host Header Validation

**RFC Section:** RFC 9112 §3.2

**Normative Level:** MUST

**Security Relevance:**

* Routing Integrity
* Request Smuggling

**Requirement Summary:**
Requests missing a Host header, containing multiple Host headers, or containing an invalid Host value must receive a 400 response.

**Expected Behavior:**
Only a single valid Host header is accepted.

---

# RQ-010

**Title:** Obsolete Line Folding (obs-fold)

**RFC Section:** RFC 9112 §5.2

**Normative Level:** MUST

**Security Relevance:**

* Request Smuggling
* Header Parsing

**Requirement Summary:**
Requests containing obs-fold outside message/http containers must either be rejected or normalized before processing.

**Expected Behavior:**
obs-fold cannot be used to manipulate header interpretation.

---

# RQ-011

**Title:** Unknown Transfer-Encoding

**RFC Section:** RFC 9112 §6.1

**Normative Level:** SHOULD

**Security Relevance:**

* Message Framing

**Requirement Summary:**
Servers receiving unsupported transfer codings should return 501 Not Implemented.

**Expected Behavior:**
Unsupported transfer codings are rejected.

---

# RQ-012

**Title:** Content-Length and Transfer-Encoding Conflict

**RFC Section:** RFC 9112 §6.3

**Normative Level:** MUST

**Security Relevance:**

* CL.TE
* TE.CL
* Request Smuggling
* HTTP Desynchronization

**Requirement Summary:**
When both Content-Length and Transfer-Encoding are present, the server may reject the request or process it according to Transfer-Encoding, but must close the connection afterwards.

**Expected Behavior:**
The connection is never reused after processing a CL+TE request.

---

# RQ-013

**Title:** Transfer-Encoding in HTTP/1.0

**RFC Section:** RFC 9112 §6.1

**Normative Level:** MUST

**Security Relevance:**

* Request Smuggling
* Message Framing

**Requirement Summary:**
HTTP/1.0 messages containing Transfer-Encoding must be treated as faulty framing and the connection must be closed.

**Expected Behavior:**
Transfer-Encoding is not accepted in HTTP/1.0 framing.

---

# RQ-014

**Title:** Transfer-Encoding Not Ending in Chunked

**RFC Section:** RFC 9112 §6.1

**Normative Level:** MUST

**Security Relevance:**

* Request Smuggling
* Message Framing

**Requirement Summary:**
If Transfer-Encoding is present and chunked is not the final encoding, the server must return 400 and close the connection.

**Expected Behavior:**
Requests with indeterminate message length are rejected.

---

# RQ-015

**Title:** Connection Close Semantics

**RFC Section:** RFC 9112 §9.6

**Normative Level:** MUST

**Security Relevance:**

* Connection Reuse
* Desynchronization Prevention

**Requirement Summary:**
When a Connection: close option is received or generated, the server must close the connection after the response and must not process additional requests on that connection.

**Expected Behavior:**
No further requests are processed after connection closure is initiated.

---

## Compliance Status Legend

| Status              | Meaning                                                        |
| ------------------- | -------------------------------------------------------------- |
| Compliant           | Behavior matches RFC requirements                              |
| Partially Compliant | Behavior generally follows RFC but differs in specific aspects |
| Non-Compliant       | Behavior contradicts RFC requirements                          |
| Stricter Than RFC   | Implementation is more restrictive than required               |
| Inconclusive        | Unable to determine compliance                                 |
| Not Applicable      | Requirement does not apply                                     |
