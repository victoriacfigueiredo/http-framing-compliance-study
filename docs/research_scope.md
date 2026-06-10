# Research Scope

Experimental Evaluation of RFC 9112 Message Framing Compliance in Modern HTTP Intermediaries

---

## Research Question

To what extent do modern HTTP intermediaries comply with RFC 9112 requirements related to HTTP/1.1 message framing, and how may implementation differences contribute to request smuggling and HTTP desynchronization risks?

---

## Motivation

HTTP Request Smuggling vulnerabilities frequently arise from inconsistencies in how different components interpret the boundaries of HTTP messages. Although RFC 9112 defines normative requirements for HTTP/1.1 message framing, real-world implementations may diverge from the specification due to legacy behavior, implementation decisions, or compatibility concerns.

Understanding how closely modern HTTP intermediaries follow RFC 9112 can help identify implementation gaps and provide insights into behaviors that may contribute to desynchronization vulnerabilities.

---

## Objectives

### Primary Objective

Evaluate the compliance of modern HTTP intermediaries with selected RFC 9112 requirements related to HTTP message framing.

### Secondary Objectives

* Identify behavioral differences among implementations.
* Determine which requirements are consistently enforced.
* Investigate deviations from RFC 9112.
* Analyze whether observed deviations are potentially relevant to request smuggling or HTTP desynchronization attacks.
* Create a reproducible compliance testing framework.

---

## Scope

This study focuses exclusively on HTTP/1.1 message framing requirements defined in RFC 9112.

The following topics are included:

* Content-Length handling
* Transfer-Encoding handling
* Message body delimitation
* Conflicting framing headers
* Multiple Content-Length headers
* Connection persistence and termination
* Parsing of malformed HTTP requests
* Requirements directly related to request boundary determination

---

## Out of Scope

The following topics are intentionally excluded from this study:

* TLS and HTTPS configuration
* Authentication and authorization mechanisms
* HTTP caching behavior
* Web application security vulnerabilities unrelated to framing
* HTTP/2-specific requirements
* HTTP/3-specific requirements
* Performance benchmarking
* Load testing

---

## Target Implementations

The initial evaluation will focus on:

1. Nginx
2. HAProxy

Additional implementations may be evaluated in future phases:

* Envoy
* Traefik
* Apache HTTP Server

---

## Methodology Overview

1. Extract normative requirements from RFC 9112.
2. Select requirements relevant to message framing.
3. Translate each requirement into one or more test cases.
4. Execute the tests against each intermediary.
5. Record observed behavior.
6. Determine compliance status.
7. Compare implementation behavior across products.
8. Analyze security implications of identified deviations.

---

## Expected Deliverables

* RFC 9112 requirement catalog
* HTTP test suite
* Docker-based testing environment
* Compliance matrix
* Experimental results
* Comparative analysis report

---

## Future Extensions

Potential future work includes:

* RFC 9113 (HTTP/2) compliance evaluation
* RFC 9931 compliance evaluation
* HTTP/2 to HTTP/1.1 downgrade scenarios
* Comparative studies involving additional intermediaries
