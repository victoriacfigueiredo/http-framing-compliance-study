# HTTP Framing Compliance Study

A comparative study of RFC 9112 compliance in modern HTTP intermediaries.

## Overview

This repository contains the experimental framework, test cases, and results used to evaluate how different HTTP intermediaries implement selected message framing requirements defined in RFC 9112 (HTTP/1.1).

The study focuses on requirements related to:

* Message framing
* Content-Length handling
* Transfer-Encoding processing
* Connection management
* Request validation

These areas are particularly relevant because framing inconsistencies between intermediaries can lead to interoperability issues and security vulnerabilities such as HTTP Request Smuggling and desynchronization attacks.

## Research Question

To what extent do modern HTTP intermediaries comply with RFC 9112 message framing requirements?

## Scope

The evaluation currently focuses on:

* Nginx
* HAProxy

Planned implementations:

* Envoy
* Traefik

## Repository Structure

```text
.
├── backend
│   └── echo_server.py
│
├── client
│   ├── raw_client.py
│
├── docker
│   ├── haproxy
│   │   └── haproxy.cfg
│   └── nginx
│       └── nginx.conf
│
├── docs
│   └── research_scope.md
│
├── requirements
│   └── rfc9112-requirements.md
│
├── results
│   ├── compliance-matrix.csv
│   ├── compliance-matrix-detailed.csv
│   ├── rq004-incomplete-cl.md
│   └── rq009-no-host-header.md
│
├── tests
│   └── run_tests.py
│
├── docker-compose.yml
└── README.md
```


## Selected RFC Requirements

The study evaluates a subset of RFC 9112 requirements that directly affect HTTP message framing and request parsing.

Examples include:

* Invalid Content-Length handling
* Missing Host header validation
* Content-Length / Transfer-Encoding conflicts
* Chunked transfer coding processing
* Transfer-Encoding validation
* Connection close semantics

Each requirement is assigned a unique identifier (RQ-001 through RQ-015).

## Experimental Environment

The testbed consists of:

```text
Client
   |
   +----> Nginx
   |
   +----> HAProxy
             |
             v
        Backend Echo Server
```

The backend server records the exact request received, allowing the study to determine whether requests were modified, rejected, or forwarded by each intermediary.

## Running the Environment

Start the test environment:

```bash
sudo docker-compose up --build
```

Verify the services:

```bash
curl http://localhost:8080/test
curl http://localhost:8081/test
curl http://localhost:8082/test
```

## Running the Test Suite

Execute all automated compliance tests:

```bash
python3 tests/run_tests.py
```

Results will be written to:

```text
results/
```

## Findings

The study records:

* Compliant behavior
* Non-compliant behavior
* Divergent implementation choices
* Security-relevant observations

A notable example identified during testing was a Host header validation discrepancy between evaluated implementations.

## Disclaimer

This project is intended for research and educational purposes only.

The objective is to evaluate standards compliance and implementation behavior, not to exploit production systems.
