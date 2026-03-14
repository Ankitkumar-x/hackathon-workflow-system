# Configurable Workflow Decision Engine

## Overview
This project is a **configurable workflow decision platform** built using Python (FastAPI).  
It processes incoming requests, evaluates configurable rules, and determines outcomes such as **approve, reject, or manual review**.

The system demonstrates how rule-driven workflows can be implemented for applications such as:

- Loan approval
- Fraud detection
- Insurance claim validation
- Job application screening

The workflow logic is defined in a configuration file (`workflow.json`), so business rules can be modified without changing the application code.

---

## Architecture

Client
↓
FastAPI Workflow Engine
↓
Rule Evaluation
↓
Decision (Approve / Reject / Manual Review)
↓
Database (SQLite)

Optional external dependency:

FastAPI → doc-verifier service

---

## Technologies Used

- Python
- FastAPI
- SQLAlchemy
- SQLite
- JSON Logic (for rule evaluation)

---

## Project Structure


## Workflow Configuration

The workflow rules are defined in `configs/workflow.json`.

Example configuration:

{
  "loan_approval": {
    "steps": [
      {
        "name": "check_credit_score",
        "condition": "credit_score >= 700",
        "action": "approve"
      },
      {
        "name": "low_credit_score",
        "condition": "credit_score < 700",
        "action": "reject"
      }
    ]
  }
}

## Database Schema

The system uses SQLite to persist workflow requests.

### requests table

| Column | Description |
|------|-------------|
| id | Unique request identifier (UUID) |
| workflow | Workflow name |
| payload | Input request payload |
| status | Request processing status |
| created_at | Timestamp when request was created |

### idempotency_keys table

Stores idempotency keys to prevent duplicate request processing.

### audit_logs table

Stores workflow execution events for debugging and audit purposes.


## Architecture

The system follows a modular architecture:

Client
↓
FastAPI REST API
↓
Workflow Engine
↓
Rule Evaluation (workflow.json)
↓
Decision Result
↓
Database Storage (SQLite)

The workflow engine reads rules from a configuration file and applies them to incoming requests.
