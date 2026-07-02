# Blog Platform API

A production-ready REST API for a blog platform built with Django and Django REST Framework.

## Live Demo
- API: (https://blogplatform-production-d602.up.railway.app/api)
- Swagger Docs: (https://blogplatform-production-d602.up.railway.app/api/docs/#/)

## Features
- JWT authentication
- Role based permissions (author-only edit/delete)
- Categories and tags with auto-formatting
- Optimized database queries (select_related, prefetch_related)
- Pagination
- Advanced filtering (category, tag, author, date range, search)
- Background email notifications via Celery
- Redis caching
- Comprehensive test suite
- CI/CD with GitHub Actions
- Dockerized for easy setup
- Cloudinary integration for image storage
- Swagger API documentation

## Tech Stack
- Python, Django, Django REST Framework
- PostgreSQL
- Redis + Celery
- Docker
- GitHub Actions (CI/CD)
- Cloudinary
- JWT Authentication

## Setup (Docker)
```bash
git clone https://github.com/lfgsammy/blogplatform.git
cd blogplatform
docker-compose up --build
```

## Setup (Local)
```bash
git clone https://github.com/lfgsammy/blogplatform.git
cd blogplatform
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Running Tests
```bash
python manage.py test posts
```

## Blogplatform Rules
- Only post authors can edit or delete their own posts
- Categories and tags are auto-formatted to title case
- A post cannot have more than 5 tags
- Duplicate tags are rejected
- Authors get email notifications when their posts receive comments or likes
- Posts are cached for 5 minutes to reduce database load

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register/ | Register new user |
| POST | /api/auth/login/ | Login, get JWT tokens |
| POST | /api/auth/refresh/ | Refresh access token |

### Posts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/posts/ | List posts (filterable, searchable, paginated) |
| POST | /api/posts/ | Create a post |
| GET | /api/posts/{id}/ | Get single post |
| PUT | /api/posts/{id}/ | Update post (author only) |
| DELETE | /api/posts/{id}/ | Delete post (author only) |

### Categories & Tags
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/categories/ | List categories |
| POST | /api/categories/ | Create category |
| GET | /api/categories/{slug}/ | Get category with its posts |
| GET | /api/tags/ | List tags |

### Comments & Likes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/posts/{id}/comments/ | List comments |
| POST | /api/posts/{id}/comments/ | Add comment |
| DELETE | /api/posts/{post_id}/comments/{id}/ | Delete comment (author only) |
| POST | /api/posts/{id}/like/ | Like a post |
| DELETE | /api/posts/{id}/like/ | Unlike a post |

## Filtering Examples
```
GET /api/posts/?category=technology
GET /api/posts/?tag=django
GET /api/posts/?search=python
GET /api/posts/?author=john
GET /api/posts/?created_after=2026-01-01&created_before=2026-12-31
GET /api/posts/?ordering=-created_at
```
