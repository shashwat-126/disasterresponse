# Emergency & Disaster Response Platform

An AI-powered disaster response platform for incident reporting, AI-based severity assessment, multi-department coordination, resource management, and response tracking.

## Features
- Incident reporting for citizens and administrators
- AI-powered disaster severity assessment
- Risk and priority scoring
- Automatic department assignment
- Multi-department incident coordination
- Department-specific dashboards
- Action reports with proof attachments
- Resource request and allocation management
- Damage assessment updates
- Photo and video uploads
- GPS-based incident location capture
- Duplicate incident detection
- Notifications and workflow tracking
- Downloadable incident PDF reports
- Admin analytics and SLA monitoring
- Audit logging and CSV export
- Role-based access control
- Automated backend and ML testing
- Docker and Kubernetes deployment support

## System Architecture

```text
┌─────────────────────┐
│     React + Vite    │
│      Frontend       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      FastAPI        │
│       Backend       │
└──────┬────────┬─────┘
       │        │
       │        ▼
       │  ┌───────────────┐
       │  │  ML Service   │
       │  │ Random Forest │
       │  └───────────────┘
       │
       ▼
┌─────────────────────┐
│     PostgreSQL      │
│      Database       │
└─────────────────────┘
```

## Technology Stack

### Frontend
- React
- Vite
- JavaScript / TypeScript

### Backend
- FastAPI
- Python
- SQLAlchemy
- PostgreSQL
- JWT Authentication

### AI / ML
- Scikit-learn
- Random Forest Classifier
- Logistic Regression Baseline
- Rule-based Risk and Priority Assessment

### Infrastructure
- Docker
- Docker Compose
- Kubernetes
- Terraform

### Testing & CI
- Pytest
- Coverage
- Locust
- GitHub Actions

## Core Workflow

```text
Incident Report
      │
      ▼
AI Severity Assessment
      │
      ▼
Risk & Priority Calculation
      │
      ▼
Automatic Department Assignment
      │
      ▼
Department Acknowledgement
      │
      ▼
Response in Progress
      │
      ▼
Action Report + Proof
      │
      ▼
All Departments Completed
      │
      ▼
Incident Resolved
```
*Note: An incident can only be marked as RESOLVED after all assigned departments have completed their required action reports.*

## User Roles

### Citizen
- Register and log in
- Submit disaster reports
- Upload supporting media
- Capture incident location using GPS
- Track incident status
- Receive notifications
- Download incident reports

### Department Staff
- View incidents assigned to their department
- Acknowledge assignments
- Update response progress
- Submit action reports
- Upload proof files
- Submit damage assessments
- Request additional resources

### Administrator
- Manage incidents and departments
- Coordinate department assignments
- Approve resource requests
- Monitor response progress
- View analytics and SLA status
- Access audit logs
- Export incident data

## AI Assessment
The ML service provides:
- Severity classification
- Prediction confidence
- Risk score
- Response priority
- Estimated response time
- Secondary hazard identification
- Immediate recommendations
- Human-readable explanation
- Key assessment signals

The platform uses a trained Random Forest classifier with a Logistic Regression baseline for model comparison.

## Department Coordination
The platform supports coordinated response across departments such as:
- Fire
- Medical
- Police
- Emergency Response
- Food & Relief
- Electricity
- Water Supply
- Municipal Services
- Disaster Management Authority
- NGOs / Volunteers

Departments are automatically selected according to incident characteristics, with escalation rules for higher-severity incidents.

## Incident Lifecycle

```text
ASSIGNED
    ↓
ACKNOWLEDGED
    ↓
IN_PROGRESS
    ↓
COMPLETED
```
The overall incident can then move to **RESOLVED** after all assigned departments have completed their response activities.

## Project Structure

```text
disasteresponse/
├── backend/
│   ├── app/
│   ├── uploads/
│   └── requirements.txt
│
├── ml-service/
│   ├── app/
│   ├── artifacts/
│   ├── data/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── scripts/
│   ├── seed_departments.py
│   └── seed_users.py
│
├── tests/
│   ├── backend/
│   ├── ml/
│   └── load/
│
├── k8s/
├── terraform/
├── monitoring/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites
Make sure you have:
- Docker
- Docker Compose
- Git

### Run the Platform
```bash
git clone <repository-url>
cd disasteresponse

cp .env.example .env

docker compose up --build
```

### Access the Services

| Service | URL |
| :--- | :--- |
| **Frontend** | `http://localhost:5173` |
| **Backend API** | `http://localhost:8000` |
| **API Documentation** | `http://localhost:8000/docs` |
| **ML Service** | `http://localhost:8001` |
| **ML Health Check** | `http://localhost:8001/health` |

## Seed Data
The project includes scripts for creating:
- Departments
- Administrator users
- Department staff users

Example:
```bash
python scripts/seed_departments.py
python scripts/seed_users.py
```
> **Security:** Change default development credentials before using the platform outside a local development environment.

## Testing

Run backend and ML tests:
```bash
pytest tests/backend tests/ml
```

Run tests with coverage:
```bash
pytest tests/backend tests/ml --cov
```
Load testing configuration is available in: `tests/load/`

## Deployment
The repository contains starter infrastructure for:
- Docker-based local deployment
- Kubernetes deployment
- Terraform infrastructure
- Monitoring

For production deployment, configure:
- Secure environment variables and secrets
- HTTPS
- Persistent database storage
- Database backups
- Authentication security
- File storage
- Monitoring and logging

## API Documentation
After starting the backend, interactive API documentation is available at:  
`http://localhost:8000/docs`

## Project Goals

```text
Citizens
   ↓
AI Triage
   ↓
Response Departments
   ↓
Resource Coordination
   ↓
Incident Resolution
```
The platform aims to improve disaster-response coordination, incident visibility, resource management, and response tracking through a centralized AI-assisted system.