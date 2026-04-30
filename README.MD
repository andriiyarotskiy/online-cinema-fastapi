# 🎬 Online Cinema — Backend

A production-ready REST API for an online cinema platform built with **FastAPI**, **PostgreSQL**, **Celery**, and **Redis**. Deployed on **AWS EC2** with **Nginx** as a reverse proxy and **AWS S3** for profile photo storage.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- Docker & Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/andriiyarotskiy/online-cinema-fastapi
cd online-cinema-fastapi
```

### 2. Set up Python environment with Poetry

```bash
# Make sure Python 3.11 is active (e.g. via pyenv or system install)
python3.11 --version

# Configure Poetry to create .venv inside the project
poetry config virtualenvs.in-project true
# Install dependencies into a virtual environment
poetry env use python3.11
poetry install
# Activate the virtual environment
source .venv/bin/activate

```

### 3. Configure environment variables

```bash
cp .env.sample .env.dev
```

### 4. Start all services

```bash
docker compose -f docker-compose-dev.yml up --build
```

### 5. Create initial admin user

```bash
docker exec -it backend_cinema python create_initial_admin.py --email admin@admin.com
```


The API will be available at `http://127.0.0.1:8000/docs/`.

---

## 🌐 Live Demo

| Resource | URL |
|---|---|
| API (Swagger UI) | http://15.216.207.59/docs |
| Email service (MailHog) | http://15.216.207.59:8025 |

### Accessing the API docs

Swagger UI is protected by HTTP Basic Auth:

```
Username: admin
Password: Awk78Jwamsh12
```

### Test account (Moderator)

```
Email:    moderator@mail.com
Password: StrongPassword123!
```

Login via `POST /accounts/login/` to receive JWT tokens, then use the `access_token` as a Bearer token in the `Authorization` header.

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL |
| Async tasks | Celery + Redis |
| Email (dev) | MailHog |
| File storage | AWS S3 |
| Containerization | Docker + Docker Compose |
| Dependency management | Poetry |
| Reverse proxy | Nginx |
| CI/CD | GitHub Actions → AWS EC2 |

---

## ✅ Implemented Features

### Authentication & Accounts
- Email/password registration with activation link (24h expiry)
- Account activation and token resend
- JWT login (access + refresh token pair)
- Token refresh and logout (refresh token revocation)
- Password change (old password required)
- Password reset via email link
- Role-based access: **User**, **Moderator**, **Admin**
- Admins can change user roles and manually activate accounts
- Celery Beat: periodic cleanup of expired tokens

### User Profiles
- Create/update profile with first name, last name, gender, date of birth, bio
- Avatar upload stored in **AWS S3** (presigned URLs for private access)

### Movies (Theater)
- Full CRUD for movies (Moderator/Admin only)
- List movies with filtering, sorting, and search
- Star ratings and like/dislike voting
- Favorites list per user
- Comments with nested replies and likes
- Comment notifications

### Catalog Entities
- Genres — CRUD + usage statistics
- Stars (actors) — CRUD
- Directors — CRUD

### Infrastructure
- Fully containerized via Docker Compose
- Poetry-managed dependencies (`pyproject.toml`)
- GitHub Actions CI: linting (flake8/black), type checks (mypy), tests (pytest)
- Automatic deployment to AWS EC2 on merge to main
- Swagger/OpenAPI docs with HTTP Basic Auth protection

---

## 📡 API Endpoints Overview

### Accounts
```
POST   /accounts/register/
POST   /accounts/activate/
POST   /accounts/login/
POST   /accounts/refresh/
POST   /accounts/password-reset/request/
POST   /accounts/reset-password/complete/
PATCH  /accounts/users/{user_id}/role/
```

### Profiles
```
POST   /profiles/users/{user_id}/profile/
```

### Movies
```
GET    /theater/movies/
POST   /theater/movies/
GET    /theater/movies/{movie_id}/
PUT    /theater/movies/{movie_id}/
DELETE /theater/movies/{movie_id}/
POST   /theater/movies/{movie_id}/vote/
POST   /theater/movies/{movie_id}/rate/
POST   /theater/movies/{movie_id}/comments/
GET    /theater/movies/{movie_id}/comments/
POST   /theater/movies/{movie_id}/comments/{comment_id}/reply/
POST   /theater/movies/{movie_id}/comments/{comment_id}/like/
GET    /theater/movies/comments/notifications/
POST   /theater/favorites/movies/{movie_id}/
DELETE /theater/favorites/movies/{movie_id}/
GET    /theater/favorites/movies/
```

### Genres / Stars / Directors
```
GET|POST|DELETE        /theater/genres/
PUT                    /theater/genres/{genre_id}/
GET                    /theater/genres/stats/

GET|POST|DELETE        /theater/stars/
PUT                    /theater/stars/{star_id}/

GET|POST|DELETE        /theater/directors/
PUT                    /theater/directors/{director_id}/
```

---