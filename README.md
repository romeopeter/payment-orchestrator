# Kurudu 💳

A scalable, API-first monorepo (backend + frontend) for orchestrating multi-gateway payments across **Paystack**, **Flutterwave**, and **Moniepoint**.

This project provides a unified interface for payment initialization, verification, OTP handling, and webhook management designed to make multi-gateway operations seamless, reliable, and developer-friendly.

---

## Features

- **Unified API Interface:** Interact with multiple gateways (Paystack, Moniepoint) through a consistent set of endpoints.
- **Gateway Abstraction Layer:** Easily extend to new providers by subclassing the `PaymentsService`.
- **Secure Authentication:** Email + password authentication with JWT-protected routes.
- **Transactions Management:** Centralized transaction model with unique references and metadata tracking.
- **Webhook Resilience:** Queue-based webhook retry system using **Celery + Redis**.
- **OTP Handling:** Endpoints for submitting OTPs (for Paystack no-redirect flows).
- **Metrics & Logging:** Per-gateway metrics for success/failure rates and response times.
- **API Documentation:** OpenAPI 3.0 via Swagger UI (`/apidocs`).

---

## Tech Stack

| Layer       | Tech                                  |
| ----------- | ------------------------------------- |
| Framework   | Flask                                 |
| Auth        | JWT (PyJWT)                           |
| ORM         | SQLAlchemy                            |
| Database    | SQLite (dev), PostgreSQL/MySQL (prod) |
| API Docs    | Flasgger (Swagger UI)                 |
| Environment | python-dotenv                         |

---

## 🔧 Environment Variables

Create a `.env` file based on `.env.example`:

```bash
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///app.db

# Paystack
PAYSTACK_SECRET_KEY=sk_test_xxxxxxxxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxxxxxxxx
PAYSTACK_BASE_URL=https://api.paystack.co

# Moniepoint (if applicable)
MONIEPOINT_SECRET_KEY=sk_test_xxxxxxxxxx
MONIEPOINT_BASE_URL=https://sandbox-api.moniepoint.com

# Celery / Redis
REDIS_URL=redis://localhost:6379/0
```

## Clone the repository

`git clone https://github.com/duowork/payment-orchestration-backend.git`

`cd payment-orchestration-backend`

## Create a virtual environment

`python3 -m venv venv`
`source venv/bin/activate`

## Install dependencies

`pip install -r requirements.txt`

<!-- ## Run database migrations (if using Alembic)
`flask db upgrade` -->

## Start the Flask app

`flask run`

<!--
## Endpoint implementation

| Method | Endpoint               | Description                              | Auth |
| ------ | ---------------------- | ---------------------------------------- | ---- |
| POST   | `/auth/register`       | Register new user                        | ✅    |
| POST   | `/auth/login`          | Login and get JWT                        | ✅    |
| POST   | `/transactions`        | Create transaction                       | ❌    |
| GET    | `/transactions`        | List user transactions                   | ❌    |
| POST   | `/payments/initialize` | Initialize payment (Paystack/Moniepoint) | ❌    |
| POST   | `/payments/verify`     | Verify payment                           | ✅    |
| POST   | `/payments/submit_otp` | Submit OTP (Paystack)                    | ✅    |
| POST   | `/webhooks/<gateway_name>`   | Handle Paystack webhook                  | ❌    |

Interactive API docs:
👉 `http://localhost:5000/apidocs`

## Celery Worker Setup
Start Celery for webhook retry & background jobs:
`celery -A celery_worker.celery worker --loglevel=info`

## Logging & Metrics
Logs are structured per transaction and gateway.
Metrics (success rate, latency, failure rate) are automatically captured and can be visualized later (Prometheus/Grafana integration ready).

## Testing
pytest --maxfail=1 --disable-warnings -q

## Docker

```bash
docker build -t payment-orchestration-backend .
docker run -p 5000:5000 --env-file .env payment-orchestration-backend
```
-->

## Extending Gateway

1. Create a new file in payments/ (e.g., flutterwave.py).
2. Subclass `PaymentsService` and implement:
   - `initialize_charge()`
   - `verify_payment()`
   - `handle_webhook()`

```python
class FlutterwaveService(PaymentsService):
    def initialize_charge(self, data): ...
    def verify_payment(self, reference): ...
    def handle_webhook(self, payload): ...

```

<!--
## Roadmap

 - Paystack integration ✅
 - Moniepoint integration ✅
 - Unified API interface ✅
 - OTP & Webhook flow
 - Metrics and logging
 - Prometheus metrics exporter
 - Admin dashboard for transaction insights


## Author

Built by Romeo Peter — software developer & Product Strategist.<br />
Abuja, Nigeria <br />
[duowork.tech](duowork.tech) <br />
-->
