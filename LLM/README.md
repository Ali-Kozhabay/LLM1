# 🎓 Intelligent LMS API

A **Learning Management System (LMS)** backend built with **FastAPI**, featuring secure user authentication, course management, and dynamic content handling.

## 🚀 Features

### 🔐 Authentication
- Register, login, and secure JWT-based auth
- Password hashing with `bcrypt` (`passlib`)
- Password reset and token verification

### 👤 User Management
- Read/update own profile
- View enrolled courses
- Protected routes with user authentication

### 📚 Course Management
- Create, publish, and fetch courses
- Admin/superuser access for moderation
- Purchase courses as a user

### 🧾 Content Handling
- Add and retrieve course content
- Authenticated content access only

### ⚙️ Developer Tools
- FastAPI auto-generated docs via Swagger/OpenAPI 3.1
- `.env` based config using `pydantic-settings`
- Health check endpoint: `/health`

---

## 🧠 Tech Stack

| Tool/Library      | Usage                          |
|------------------|---------------------------------|
| **FastAPI**       | Web framework                   |
| **Python 3.12**   | Core language                   |
| **SQLAlchemy**    | ORM for DB interaction          |
| **PostgreSQL**    | Relational database             |
| **python-jose**   | JWT token encoding/decoding     |
| **passlib**       | Password hashing (`bcrypt`)     |
| **Pydantic**      | Request/response validation     |
| **Uvicorn**       | ASGI server                     |

---

## 📁 Project Structure

