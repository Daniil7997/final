# Team Management

## Description
This is a REST API for managing tasks, meetings, and evaluations in a team system.

## Tech Stack

- Python 3.14.2
- FastAPI
- PostgreSQL
- SQLAlchemy (async)
- Alembic
- Docker / Docker Compose
- Pytest

## Features

- User authentication (JWT)
- Task management
- Meetings scheduling
- Evaluations system
- Comments on tasks
- Calendar endpoint

## Installation

`git clone https://github.com/Daniil7997/final`

`cd team_management`


## Environment Variables

Create `.env` file:

### Standard
#### APP

- PRIVATE_KEY_HEX=<hex-encoded_private_key>

        - must be valid hex string
        - used in bytes.fromhex
        - example: a3f5c91b2d...

#### POSTGRESQL
- DB_HOST=db
- DB_PORT=5432
- DB_USER=postgres
- DB_PASSWORD=<your_db_password>
- DB_NAME=TeamManagement
- IS_TEST_DB=False


#### REDIS
- REDIS_HOST=redis
- REDIS_PASSWORD=<your_redis_password>
- REDIS_PORT=6379

### Test overrides

- DB_NAME=TestTeamManagement
- IS_TEST_DB=True

        DB_NAME must contain "test"
        IS_TEST_DB=True (used only in test environment)


## Run with Docker
### Standard:
`docker-compose up`

### Dev (reload mode):
`docker-compose -f compose_dev.yaml up`

### CI (tests, type checks):
`docker-compose -f compose_test.yaml --env-file .env.test up`
