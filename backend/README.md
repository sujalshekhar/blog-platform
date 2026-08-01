# BlogPlatform Backend ⚙️

This is the event-driven FastAPI backend powering the BlogPlatform. It is built using scalable architecture patterns to ensure performance, maintainability, and data integrity.

### 🔴 Live API Docs
- **Swagger UI:** [https://blog-platform-md24.onrender.com/docs](https://blog-platform-md24.onrender.com/docs)
- **Frontend:** [https://blog.sujalshekhar.com/](https://blog.sujalshekhar.com/)

---

## 🛠️ Technology Stack & Rationale

We carefully selected our backend technologies to maximize developer velocity, type safety, and real-time capabilities.

- **FastAPI (Python 3.10+):** Chosen for its high performance and native async support. It provides automatic OpenAPI documentation generation and integrates with Pydantic for strict request validation and serialization.
- **SQLAlchemy (ORM):** Provides ORM capabilities for database interaction. It abstracts complex queries and integrates cleanly with our application-level transaction management.
- **PostgreSQL:** The primary relational database used for production and development, chosen for its strict data integrity and reliability.
- **Redis:** Utilized to cache blog detail retrieval. We implement a **Cache-Aside Pattern**—if Redis goes down, the application "fails open" and degrades gracefully to database queries without crashing. The cache is automatically invalidated whenever the active blog version changes.
- **WebSockets:** Used specifically for the Live Chat feature to enable real-time, bi-directional communication between users on a blog post.
- **Server-Sent Events (SSE):** Used for system notifications. Since notifications only flow one way (Server -> Client), SSE is far more lightweight and resource-efficient than WebSockets for this use case.

---

## 🏗️ Architecture Design Patterns

This backend strictly enforces clean architecture principles:

1. **Controller-Service-Repository Pattern:**
   - **Controllers (Routers):** Extremely thin. They solely handle receiving the HTTP request, validating the payload via Pydantic, and passing the data to the Service layer.
   - **Services:** Contain the primary business logic. They enforce rules, orchestrate multiple repositories, and own the transaction boundaries (commits and rollbacks).
   - **Repositories:** Encapsulate database access. They execute CRUD operations and may call `db.flush()` to execute SQL and retrieve generated IDs, but they *never commit* transactions.

2. **Single Transaction Principle:**
   - Related database operations (e.g., updating a feature request status AND dispatching notifications) are executed atomically. The service layer owns the transaction boundaries, ensuring that commits are only performed after all related repository operations succeed.

---

## 🏛️ Project Structure

```text
backend/
├── alembic/          # Database migrations
├── app/
│   ├── api/          # FastAPI routers (Controllers)
│   ├── core/         # Configuration, security utilities, and DB session management
│   ├── dependencies/ # FastAPI dependencies (e.g., authentication, RBAC)
│   ├── enums/        # String enums for statuses, roles, and types
│   ├── models/       # SQLAlchemy declarative models
│   ├── repositories/ # Database interaction layer
│   ├── schemas/      # Pydantic schemas for request/response validation
│   ├── services/     # Core business logic and transaction orchestration
│   ├── sse/          # Server-Sent Events management
│   └── websocket/    # WebSocket connection management for live chat
```

---

## 📡 API Endpoints Overview

The API is versioned under `/api/v1`. Below is a comprehensive list of the core endpoints.

### Authentication (`/auth`)
- `POST /auth/register`: Creates a new user account, hashes the password, and saves it to the DB.
- `POST /auth/login`: Validates credentials and returns an OAuth2 compatible JWT Bearer token.

### Blogs (`/blogs`)
- `POST /blogs/`: Creates a new draft blog. Generates a unique `blog_group_id` for version tracking. (Requires Auth)
- `GET /blogs/`: Retrieves all approved, active blogs. Supports search, filtering, and sorting. (Public)
- `GET /blogs/all`: Retrieves all active blogs regardless of status. (Requires Admin/Approver)
- `GET /blogs/my-blogs`: Retrieves all non-draft active blogs authored by the current user.
- `GET /blogs/my-drafts`: Retrieves all draft blogs authored by the current user.
- `GET /blogs/{blog_id}`: Retrieves the active version of a specific blog. Uses Redis caching.
- `PUT /blogs/{blog_id}`: Creates a *new* version of a blog and marks the old version as inactive (Strict Version Control).
- `DELETE /blogs/{blog_id}`: Soft-deletes a blog by marking all its versions as inactive.
- `POST /blogs/{blog_id}/submit`: Submits a draft for review. Changes status to PENDING and triggers SSE notifications to Admins via background tasks.
- `POST /blogs/{blog_id}/approve`: Approves a pending blog. Triggers SSE notification to the author. (Requires Admin/Approver)
- `POST /blogs/{blog_id}/reject`: Rejects a pending blog. Triggers SSE notification to the author. (Requires Admin/Approver)
- `GET /blogs/{blog_id}/history`: Retrieves the entire edit history (all versions) of a specific blog.

### Chat (`/chat`)
- `GET /chat/{blog_group_id}`: Retrieves the message history for a public blog's chat. Utilizes **cursor-based pagination** for high-performance, real-time scrolling.

### Feature Requests (`/feature-requests`)
- `POST /feature-requests/`: Submits a new feature request and atomically dispatches notifications to all Admins using bulk inserts.
- `GET /feature-requests/`: Lists feature requests. Admins see all; normal users only see their own.
- `PUT /feature-requests/{request_id}/status`: Updates the status of a feature request (e.g., In Progress, Completed) and atomically notifies the original requester.

### Notifications (`/notifications`)
- `GET /notifications/`: Retrieves the current user's notification history.
- `PUT /notifications/{notification_id}/read`: Marks a specific notification as read.

### Real-Time Infrastructure
- `GET /sse/stream`: The Server-Sent Events endpoint. Clients maintain an open connection here to receive live JSON payloads when notifications are dispatched.
- `WS /ws`: The WebSocket endpoint. Clients connect here with their JWT token to join blog-specific chat rooms and broadcast messages.

---

## 🔒 Security

Security is treated as a first-class citizen across the stack:
- **Stateless Authentication (JWT):** Sessions are managed statelessly using JSON Web Tokens.
- **Data Protection:** Passwords are never stored in plain text. `Passlib` is used with the **Bcrypt** algorithm to securely salt and hash passwords.
- **Role-Based Access Control (RBAC):** Access rights are strictly enforced on protected routes through FastAPI dependencies.
- **Input Validation:** Pydantic strictly validates and type-checks all incoming request payloads before any business logic executes.
- **Secrets Management:** Sensitive data (e.g., Database URLs, JWT secrets) are managed strictly via environment variables.
- **CORS Configuration:** Cross-Origin Resource Sharing is strictly configured to only allow requests from specific trusted front-end domains.

---

## 🧪 Testing

Backend testing relies on FastAPI's `TestClient` combined with `pytest`.

```bash
cd backend
pytest -v
```

---

## 🚢 Deployment

The current production deployment stack consists of:
- **Backend API:** Hosted on Render as a web service.
- **Database:** Managed PostgreSQL instance.
- **Cache:** Managed Redis instance.
- **Frontend:** Hosted on Vercel.

---

## 🚀 Quick Start & Setup

### 1. Prerequisites
- Python 3.10+
- PostgreSQL & Redis Server (Running locally)

### 2. Setup Virtual Environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the `backend` root directory to configure the database and external connections:
```env
# Database
DATABASE_URL=postgresql://blog_user:blog_password@localhost:5432/blog_db

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_TTL=3600

# Security (JWT)
JWT_SECRET=your_super_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
FRONTEND_URL=https://blog.sujalshekhar.com
```

### 5. Run the Server
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

### 6. Access Interactive API Docs
Visit: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to explore and test the endpoints directly from your browser!
