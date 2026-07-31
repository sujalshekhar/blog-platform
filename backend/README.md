# BlogPlatform Backend ⚙️

This is the highly scalable, event-driven FastAPI backend powering the BlogPlatform. It is designed following strict enterprise patterns to ensure performance, maintainability, and data integrity.

### 🔴 Live API Docs
- **Swagger UI:** [https://blog-platform-md24.onrender.com/docs](https://blog-platform-md24.onrender.com/docs)
- **Frontend:** [https://blog.sujalshekhar.com/](https://blog.sujalshekhar.com/)

---

## 🛠️ Technology Stack & Rationale

We carefully selected our backend technologies to maximize developer velocity, type safety, and real-time capabilities.

- **FastAPI (Python 3.10+):** Chosen for its exceptional performance (thanks to Starlette and Pydantic) and native async support. It provides automatic interactive documentation (Swagger UI) and strict type validation out of the box, drastically reducing runtime errors.
- **SQLAlchemy (ORM):** Used for database interactions. It provides a powerful, database-agnostic way to handle complex queries, relationships, and transactions.
- **SQLite (Development) / PostgreSQL (Production):** The platform is configured to use SQLite for easy local development but is fully ready to be swapped to PostgreSQL for production deployments.
- **Redis (Caching):** Utilized to cache heavy read operations (like fetching active blogs). We implement a **Cache-Aside Pattern**—if Redis goes down, the application "fails open" and degrades gracefully to database queries without crashing.
- **WebSockets:** Used specifically for the Live Chat feature to enable real-time, bi-directional communication between users on a blog post.
- **Server-Sent Events (SSE):** Used for system notifications. Since notifications only flow one way (Server -> Client), SSE is far more lightweight and resource-efficient than WebSockets for this use case.
- **Passlib (Bcrypt) & Python-Jose:** Used for secure password hashing and stateless JWT (JSON Web Token) authentication.

---

## 🏗️ Architecture Design Patterns

This backend strictly enforces clean architecture principles:

1. **Controller-Service-Repository Pattern:**
   - **Controllers (Routers):** Extremely thin. They solely handle receiving the HTTP request, validating the payload via Pydantic, and passing the data to the Service layer.
   - **Services:** Contain 100% of the business logic. They enforce rules, orchestrate multiple repositories, and manage transaction boundaries.
   - **Repositories:** Contain 100% of the database logic. They execute CRUD operations but *do not commit* transactions, allowing the Service layer to compose multiple operations into a single transaction.

2. **Single ACID Transactions:**
   - Complex operations (e.g., updating a feature request status AND dispatching 10 notifications to admins) are wrapped in a single database transaction using `db.flush()` in the repository and `db.commit()` at the end of the Service method. If any part fails, the entire operation rolls back, preventing orphaned data.

---

## 📡 API Endpoints Overview

The API is versioned under `/api/v1`. Below is a comprehensive list of the core endpoints and how they function.

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

## 🚀 Quick Start & Setup

### 1. Prerequisites
- Python 3.10+
- Redis Server (Must be running locally on port `6379`)

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

# CORS Configuration (Required if Frontend is on a different domain like Vercel)
FRONTEND_URL=https://blog.sujalshekhar.com
```

### 5. Run the Server
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

### 5. Access Interactive API Docs
FastAPI automatically generates interactive Swagger documentation. 
Visit: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to explore and test the endpoints directly from your browser!
