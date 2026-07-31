# BlogPlatform Pro 🚀

A modern, full-stack, enterprise-grade blogging platform designed with robust content moderation, version control, and real-time interactions.

### 🔴 Live Demo
- **Frontend (Vercel):** [https://blog.sujalshekhar.com/](https://blog.sujalshekhar.com/)
- **Backend API (Render):** [https://blog-platform-md24.onrender.com/docs](https://blog-platform-md24.onrender.com/docs)

## 🌟 Key Features

- **Role-Based Access Control (RBAC):** Distinct roles for `User`, `Approver`, and `Admin`.
- **Content Moderation Workflow:** Authors submit drafts -> Approvers/Admins review -> Approved blogs go live.
- **Strict Version Control:** Blogs are never overwritten. Every edit creates a new version, preserving complete history.
- **Real-Time Discussion (Chat):** Live commenting on approved blogs via **WebSockets**.
- **Instant Notifications:** Server-Sent Events (**SSE**) instantly notify authors of approvals and admins of new submissions.
- **Cache-Aside Architecture:** High-performance reads utilizing **Redis**.
- **Interactive Feature Board:** Users can request features, and admins can update statuses.

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** React 18 with Vite
- **Language:** TypeScript
- **Styling:** Tailwind CSS + Shadcn UI
- **State Management:** React Query (TanStack Query)
- **Routing:** React Router DOM

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **ORM:** SQLAlchemy (Async/Sync hybrid)
- **Database:** SQLite (development) / PostgreSQL (production ready)
- **Caching:** Redis
- **Real-Time:** WebSockets (Chat) & SSE (Notifications)
- **Security:** Passlib (Bcrypt) & Python-Jose (JWT)

---

## 🚀 Setup & Run (Local Development)

### 1. Prerequisites
- **Node.js** (v18+)
- **Python** (3.10+)
- **Redis Server** (Running locally on default port `6379`)

### 2. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
*Backend runs on `http://127.0.0.1:8000`*

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:5173`*

---

## 🧪 Testing

### Backend
Backend testing relies on FastAPI's `TestClient` combined with `pytest`.
```bash
cd backend
pytest -v
```

### Frontend
You can test components and hooks using standard Jest/React Testing Library setup.
```bash
cd frontend
npm run test
```

---

## 🚢 Deployment (Production)

To migrate from the local development environment to a robust production environment, follow these architectural guidelines:

1. **Database:** Replace the local SQLite database (`test.db`) with a managed **PostgreSQL** instance (e.g., AWS RDS, Supabase). Update the `DATABASE_URL` in your `.env` file.
2. **Caching:** Replace the local Redis instance with a managed Redis cluster (e.g., AWS ElastiCache, Upstash). Update the `REDIS_URL`.
3. **Backend Server:** Containerize the FastAPI backend using Docker. Run the container behind a reverse proxy (like Nginx) or deploy it to a container orchestration service (like AWS ECS, Google Cloud Run). Ensure you run it with a production-grade ASGI server like `gunicorn` with `uvicorn` workers.
4. **Frontend Assets:** Build the React application (`npm run build`). Deploy the static `dist` folder to a CDN or static hosting service (e.g., Vercel, AWS S3 + CloudFront).

---

## 📚 API Documentation & Workflows

### Swagger UI (`/docs`)
FastAPI automatically generates interactive OpenAPI documentation. Once the backend is running, visit:
**👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

From there, you can view the schemas, read endpoint descriptions, and test requests directly in your browser.

### Core Workflows
- **Auth Workflow:** Client requests `/auth/login` -> Server validates Bcrypt hash -> Returns JWT -> Client stores JWT and attaches it to the `Authorization: Bearer <token>` header for future requests.
- **Content Moderation Workflow:** User creates Draft -> User calls `/submit` -> Status becomes `PENDING` -> SSE Notification hits Admins -> Admin reviews and calls `/approve` -> Status becomes `APPROVED` -> SSE Notification hits User.

---

## 🔒 Security Notes & Secrets Management

Security is treated as a first-class citizen across the stack:

- **Data Protection (Passwords):** Raw passwords are never stored. We use `Passlib` with the **Bcrypt** algorithm to securely salt and hash passwords.
- **Stateless Authentication (JWT):** Sessions are managed statelessly via JSON Web Tokens signed with the `HS256` algorithm. The token contains the user's role (RBAC), allowing the API to verify permissions instantly without hitting the database.
- **Input Validation:** All incoming data is rigorously sanitized and type-checked via **Pydantic** schemas before it ever reaches the application logic. This heavily mitigates SQL Injection and XSS attacks.
- **Secrets Management:** Secrets (like the `SECRET_KEY` for JWT signing and Database URLs) are strictly managed via environment variables. In development, these are loaded via a `.env` file (which is added to `.gitignore`). In production, these should be injected via a secure secret manager (e.g., AWS Secrets Manager, GitHub Secrets).
- **CORS:** Cross-Origin Resource Sharing is strictly configured to only allow requests from specific trusted front-end domains.

---

## 🏗️ Architecture Design Patterns

This project enforces strict enterprise design patterns:
1. **Controller-Service-Repository Pattern:** Controllers handle routing, Services handle business logic and transactions, Repositories handle database interactions.
2. **Single ACID Transactions:** Complex operations (e.g., updating a blog status and dispatching 10 notifications) are committed atomically.
3. **Fail-Open Caching:** If Redis is down, the application gracefully degrades to database queries.
