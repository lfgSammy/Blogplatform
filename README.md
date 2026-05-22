# Blog Platform API

A REST API built with Django and Django REST Framework.

## Features
- Token based authentication
- Post CRUD with author only permissions
- Nested comments with reply support
- Like/Unlike system with duplicate prevention

## Tech Stack
- Python
- Django
- Django REST Framework
- SQLite

## Setup
```bash
git clone  https://github.com/lfgSammy/Blogplatform.git
cd blog-platform-api
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## API Endpoints
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/auth/register/ | Register new user | No |
| POST | /api/auth/login/ | Login and get token | No |
| GET | /api/posts/ | Get all posts | No |
| POST | /api/posts/ | Create a post | Yes |
| GET | /api/posts/{id}/ | Get single post | No |
| PUT | /api/posts/{id}/ | Update post | Author only |
| DELETE | /api/posts/{id}/ | Delete post | Author only |
| GET | /api/posts/{id}/comments/ | Get comments | No |
| POST | /api/posts/{id}/comments/ | Add comment | Yes |
| DELETE | /api/posts/{id}/comments/{id}/ | Delete comment | Author only |
| POST | /api/posts/{id}/like/ | Like a post | Yes |
| DELETE | /api/posts/{id}/like/ | Unlike a post | Yes |
