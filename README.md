# Credit Approval System

A **Django + PostgreSQL + Redis + Celery** based backend system to simulate a real-world **credit approval and loan management workflow**.
The entire application is **fully dockerized** and can be started with a single command.

This project was built as a backend assignment with focus on:

* Clean code & separation of concerns
* Asynchronous background processing
* Business-rule–driven loan eligibility logic
* Production-style Docker setup

---

## 🚀 Tech Stack

* **Backend:** Django 4.2 + Django REST Framework
* **Database:** PostgreSQL 15
* **Async Tasks:** Celery + Redis
* **Containerization:** Docker & Docker Compose
* **Data Ingestion:** Pandas (Excel-based ingestion)

---

## 📦 Features

### 👤 Customer Management

* Register new customers
* Auto-calculate approved credit limit based on income
* Store and track current debt

### 💳 Loan Eligibility Engine

* Eligibility based on:

  * Customer income
  * Approved credit limit
  * Existing active loans
  * Repayment history
* Returns corrected interest rate if applicable

### 🏦 Loan Management

* Create loans for eligible customers
* View loan details
* View all loans for a customer

### ⚙️ Background Data Ingestion

* Bulk ingestion of **customers and loans from Excel files** using Celery
* Automatic recalculation of customer debt

---

## 🧠 Business Logic (Important)

### Approved Credit Limit

```
approved_limit = round((36 × monthly_income) / 100000) × 100000
```

### Loan Rejection Rules

A loan is rejected if **any** of the following are true:

* Current debt ≥ approved limit
* Too many active loans
* Poor EMI repayment history

This means **a newly registered user can be ineligible** if historical loan data already exists.

---

## 🐳 Dockerized Setup

### Services

* `web` – Django REST API
* `db` – PostgreSQL database
* `redis` – Message broker
* `celery` – Background worker

Everything runs via **one command**.

---

## ▶️ How to Run

### Prerequisites

* Docker
* Docker Compose

### Start the application

```bash
docker compose up --build
```

### Stop and reset everything (including DB)

```bash
docker compose down -v
```

---

## 🔗 API Endpoints

### 1️⃣ Register Customer

`POST /register`

```json
{
  "first_name": "Harshit",
  "last_name": "Singh",
  "age": 26,
  "monthly_income": 60000,
  "phone_number": 9876543210
}
```

---

### 2️⃣ Check Loan Eligibility

`POST /check-eligibility`

```json
{
  "customer_id": 1,
  "loan_amount": 500000,
  "interest_rate": 12,
  "tenure": 24
}
```

#### Sample Response (Rejected)

```json
{
  "customer_id": 1,
  "approval": false,
  "interest_rate": "12.00",
  "corrected_interest_rate": "12.00",
  "tenure": 24,
  "monthly_installment": "0.00"
}
```

---

### 3️⃣ Create Loan

`POST /create-loan`

```json
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 12,
  "tenure": 24
}
```

---

### 4️⃣ View Loan by ID

`GET /view-loan/<loan_id>`

---

### 5️⃣ View All Loans for Customer

`GET /view-loans/<customer_id>`

---

## 📊 Initial Data Ingestion

On startup:

* Customer data is ingested from Excel
* Loan data is ingested from Excel
* Customer debt is recalculated automatically

This is handled asynchronously using **Celery workers**.

---

## 🛡️ Data Integrity Guarantees

* **Primary keys are never manually inserted**
* PostgreSQL auto-increment sequences are preserved
* Prevents duplicate key & corruption issues

---

## 🧪 Testing Notes

* Unit tests were optional for this assignment
* API endpoints were manually tested using Postman / Thunder Client
* Edge cases (existing debt, rejection logic) are intentionally preserved

---

## 📁 Project Structure

```
credit_approval_system/
│── loans/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── tasks.py
│   └── management/commands/
│── credit_approval_system/
│   ├── settings.py
│   ├── urls.py
│── docker-compose.yml
│── Dockerfile
│── requirements.txt
│── README.md
```

---

## 📌 Key Design Decisions

* Used **Celery** for heavy data ingestion
* Used **PostgreSQL** for transactional integrity
* Strict separation between serializers, views, and business logic
* Designed eligibility logic to behave like a real credit system

---
