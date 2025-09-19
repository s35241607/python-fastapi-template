# Gemini Code Assistant Context

This document provides context for the Gemini Code Assistant to understand the project structure, conventions, and tasks.

## Project Overview

This project is a FastAPI-based ticket system. It follows a router > service > repository architecture and uses async PostgreSQL for database operations.

*   **Backend Framework:** FastAPI
*   **Database:** PostgreSQL (using `asyncpg` and `SQLAlchemy`)
*   **Dependency Management:** `uv`
*   **Linting and Formatting:** `ruff`
*   **Type Checking:** `mypy`

The project is organized into the following main directories:

*   `app`: Contains the core application logic, including routers, services, repositories, models, and schemas.
*   `tests`: Contains the project's tests.
*   `docs`: Contains project documentation.

## Building and Running

### 1. Environment Setup

1.  Copy `.env.example` to `.env` and update the `DATABASE_URL` and `SECRET_KEY`.
2.  Install dependencies using `uv`:

    ```bash
    uv sync
    ```

### 2. Database Initialization

Run the following command to create the database tables:

```bash
python init_db.py
```

### 3. Running the Application

To run the application in development mode with auto-reload, use the following command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Alternatively, you can use the simplified command:

```bash
python main.py
```

The application will be available at `http://localhost:8000`, and the API documentation can be accessed at `http://localhost:8000/docs`.

### 4. Running Tests

To run the test suite, use the following command:

```bash
pytest
```

## Development Conventions

*   **Coding Style:** The project uses `ruff` for linting and formatting. The configuration can be found in the `pyproject.toml` file.
*   **Type Checking:** The project uses `mypy` for static type checking. The configuration can be found in the `pyproject.toml` file.
*   **API Endpoints:** API endpoints are defined in the `app/routers` directory. The `README.md` file lists the following endpoints, which are likely defined in a file that is currently inaccessible:

    *   `POST /api/v1/tickets/`: Create a ticket and add an initial comment.
    *   `GET /api/v1/tickets/`: Get all tickets (including user and comments).
    *   `GET /api/v1/tickets/{ticket_id}`: Get a specific ticket's details.
    *   `PUT /api/v1/tickets/{ticket_id}/status`: Update a ticket's status.
    *   `DELETE /api/v1/tickets/{ticket_id}`: Delete a ticket and all its comments.
    *   `POST /api/v1/tickets/{ticket_id}/comments/`: Add a comment to a ticket.
