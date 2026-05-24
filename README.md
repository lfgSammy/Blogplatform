# Blog Platform API

A REST API built with Django and Django REST Framework.

Base URL: https://your-app.railway.app/api

## Authentication
This API uses JWT authentication.
Include the access token in every request header:
Authorization: Bearer <access_token>

## Endpoints

### Auth
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /auth/register/ | Register new user | No |
| POST | /auth/login/ | Login, get tokens | No |
| POST | /auth/refresh/ | Refresh access token | No |

### Posts
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | /posts/ | Get all posts | No |
| POST | /posts/ | Create a post | Yes |
| GET | /posts/{id}/ | Get single post | No |
| PUT | /posts/{id}/ | Update post | Yes (author only) |
| DELETE | /posts/{id}/ | Delete post | Yes (author only) |

### Comments
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | /posts/{id}/comments/ | Get comments | No |
| POST | /posts/{id}/comments/ | Add comment | Yes |
| DELETE | /posts/{id}/comments/{id}/ | Delete comment | Yes (author only) |

### Likes
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /posts/{id}/like/ | Like a post | Yes |
| DELETE | /posts/{id}/like/ | Unlike a post | Yes |

## Request/Response Examples

### Register
Request:
{
    "username": "john",
    "email": "john@test.com",
    "password": "Test@1234"
}

Response:
{
    "access": "eyJ...",
    "refresh": "eyJ..."
}

### Create Post
Request:
{
    "title": "My First Post",
    "body": "Post content here",
    "status": "published"
}

Response:
{
    "id": 1,
    "title": "My First Post",
    "body": "Post content here",
    "status": "published",
    "author": {
        "id": 1,
        "username": "john"
    },
    "created_at": "2026-05-07T10:00:00Z"
}
