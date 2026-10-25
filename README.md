# BRMFB Backend API

A robust, secure, and scalable Django REST Framework (DRF) backend service built for the BRMFB banking and financial services platform, optimized for mobile application integration.

---

## 🚀 Features & Architecture

- **Django 5.1 & Django REST Framework (DRF):** Modern, RESTful API architecture with secure session/token authentication.
- **Python 3.14 Compatibility:** Fully patched and optimized for modern Python environments.
- **Modular App Design:** Organized into independent Django apps for maintainability and scalability:
  - `apps.identity`: User registration, login, and OTP verification.
  - `apps.accounts`: Customer account management and balances.
  - `apps.transactions`: Transaction history and statement logs.
  - `apps.beneficiaries`: Beneficiary management.
  - `apps.transfers`: Internal and external bank transfers with account verification.
  - `apps.payments`: Bill payments, airtime, data bundles, and QR merchant payments.
  - `apps.notifications`: In-app and push notification handling.
  - `apps.support`: Customer support ticketing system.
  - `apps.audit`: Security event auditing and logging.

---

## 📱 Mobile App Integration APIs (`/api/v1/`)

| Endpoint Category | Base Path | Key Methods | Description |
|-------------------|-----------|-------------|-------------|
| **Authentication** | `/api/v1/auth/` | `POST` | Register, Login, Request & Verify OTP |
| **Accounts** | `/api/v1/accounts/` | `GET` | List accounts and fetch account details |
| **Transactions** | `/api/v1/transactions/` | `GET` | Retrieve transaction statement history |
| **Beneficiaries** | `/api/v1/beneficiaries/` | `GET, POST, DELETE` | Manage saved transfer beneficiaries |
| **Transfers** | `/api/v1/transfers/` | `POST` | Verify recipient accounts and execute transfers |
| **Payments** | `/api/v1/payments/` | `POST` | Airtime, data, bill payments, and QR codes |
| **Notifications** | `/api/v1/notifications/` | `GET, POST` | Retrieve and mark notifications as read |
| **Support** | `/api/v1/support/` | `GET, POST, PATCH` | Manage customer support tickets |

---

## 🛠️ Getting Started

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Pip & Virtualenv

### Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/digitalpentech-art/brmfb-backend.git
   cd brmfb-backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements/development.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Update .env with your settings (SECRET_KEY, DB credentials, etc.)
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

---

## 🧪 Testing

Run the test suite using `pytest`:
```bash
pytest
```

---

## 🚢 Deployment

Configured for deployment via Render (`render.yaml`). Ensure production environment variables (`SECRET_KEY`, `DEBUG=False`, database URLs) are properly configured in your hosting platform.
