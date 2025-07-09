
# PokeSocialAPI

A simulated social media platform powered by the [PokéAPI](https://pokeapi.co/), featuring asynchronous ingestion, resilient processing, and a cloud-ready architecture.

## Overview

This project was built to address a backend engineering challenge involving the ingestion, transformation, and reprocessing of data sourced from a third-party API, with a strong focus on:

- Reliability (retry logic, DLQ)
- Scalability (AWS-ready design)
- Observability (logs, SQS)
- Testability (Pytest coverage)

## Features

- Ingests "posts" (berries) and "comments" (flavors)
- Dynamically stores data into DynamoDB
- Resilient processing layer with retry and backoff using `tenacity`
- Dead Letter Queue implemented via AWS SQS (mocked by Localstack)
- DLQ Worker to retry failed items
- OpenSearch integration to index processed posts
- Automated tests with pytest and mocking

---

## Running Tests

You can run tests inside the Docker container:

```bash
docker compose exec poke-app pytest
```

Tests include:

- ✅ ProcessingService (success, failure, DLQ fallback)
- ✅ DLQ Worker reprocessing logic
- ✅ SocialMediaController integration
- ✅ Retry logic (with transient failures)

---

## 🛠️ How to Run Locally

1. **Clone the repository**

```bash
git clone git@github.com:sarasouza18/PokeApi.git
cd PokeApi
```

2. **Start the application with Docker Compose**

```bash
docker compose up --build
```

3. **To run DLQ reprocessing manually**

```bash
docker compose exec poke-app python app/infrastructure/workers/dlq_reprocessor.py
```

---

## Stack & Services

- **Language:** Python 3.9
- **Database:** DynamoDB
- **Queue:** AWS SQS (LocalStack)
- **Search Engine:** OpenSearch
- **Cache & Circuit Breaker (future-ready):** Redis
- **Retry Mechanism:** Tenacity
- **Tests:** Pytest + unittest.mock

---

## 🌩️ Cloud Architecture Suggestion

If deployed to AWS, the components would be:

| Component        | AWS Equivalent     |
|------------------|--------------------|
| Post/Comment DB  | DynamoDB           |
| DLQ              | SQS DLQ Queue      |
| Processing Logic | AWS Lambda         |
| Search Index     | Amazon OpenSearch  |
| DLQ Worker       | Fargate Task       |
| Scheduler (cron) | EventBridge (cron) |
| Logs             | CloudWatch Logs    |

---

## Performance Expectations

| Documents | Estimated Time |
|-----------|----------------|
| 100       | ~3 seconds     |
| 1,000,000 | ~8–12 minutes  |

Assumes parallel ingestion and optimized retries with async Lambda.

---

## Folder Structure

```
app/
├── domain/                  # Interfaces
├── infrastructure/
│   ├── external/            # ProcessingService, DLQ
│   ├── persistence/         # DynamoDB
│   ├── search/              # OpenSearch integration
│   └── workers/             # DLQ Reprocessor
├── controller/              # SocialMediaController
├── main.py                  # Entrypoint
tests/                       # Test suite
```

---

## Design Decisions

- **Why process after storing?** Ensures data persistence even when processing fails.
- **Why DLQ + Retry?** Fault-tolerance in high-throughput systems.
- **Why Fargate Worker?** Scalable containerized execution of reprocessing.

---

## Made with care by

**[Sara Souza](https://github.com/sarasouza18)**  
Tech speaker, software engineer & backend architecture enthusiast.
