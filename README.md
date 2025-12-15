# Helfy – Backend & Event Streaming Assignment

This project was created as part of a **technical assignment for the Helfy hiring process**.  
It demonstrates a modern backend architecture with a REST API, distributed database, and event streaming.

**importent notes:** 1. swagger runs on localhost:8000, for api tests. 2. login window on localhost:8080 3. this project ment for local runs and development, for remote runs, please add first your remote ip address for allowed host it the api settings.

**i've sent you a definition of done in the email with the git repo link**

---

## 🚀 Overview

The system exposes a REST API that handles user and order requests, persists data in a distributed SQL database, and streams database changes to Kafka using CDC (Change Data Capture).  
A Node.js consumer listens to these events for downstream processing and logging.

---

## 🧱 Technology Stack

### API
- **Django REST Framework**
- **Swagger / OpenAPI** for API documentation and testing

### Database
- **TiDB** (distributed MySQL-compatible database)

### Event Streaming
- **Apache Kafka**

### CDC (Change Data Capture)
- **TiCDC** – streams database changes from TiDB to Kafka topics

### Kafka Consumer
- **Node.js**
- **KafkaJS**

### Containerization
- **Docker**
- **Docker Compose**

---

## ▶️ First Run

Make sure Docker and Docker Compose are installed.

To start the entire system for the first time:

```bash
docker compose up --build
