# BlogPlatform Frontend 🎨

This is the sleek, responsive, and highly interactive frontend for the BlogPlatform. It focuses on providing a premium user experience with real-time updates and seamless navigation.

### 🔴 Live Demo
- **Frontend:** [https://blog.sujalshekhar.com/](https://blog.sujalshekhar.com/)
- **Backend API:** [https://blog-platform-md24.onrender.com/docs](https://blog-platform-md24.onrender.com/docs)

---

## 🛠️ Technology Stack & Rationale

We chose a modern React stack to ensure a highly responsive, maintainable, and visually stunning application.

- **React 18 & Vite:** React provides a robust component-based architecture, while Vite offers a blazing-fast development server and optimized production builds, far outpacing legacy bundlers like Webpack.
- **TypeScript:** Enforces strict type safety across the application, catching bugs at compile-time rather than run-time. It seamlessly integrates with our backend's Pydantic schemas.
- **React Query (TanStack Query v5):** Handles all asynchronous data fetching, caching, synchronization, and background updates. It eliminates the need for complex Redux boilerplate and handles loading/error states out of the box.
- **Tailwind CSS:** A utility-first CSS framework that allows for rapid UI development directly within JSX, ensuring consistent styling without bloated CSS files.
- **Shadcn UI & Radix Primitives:** Provides beautifully designed, accessible, and customizable UI components (Modals, Dropdowns, Buttons). Unlike traditional component libraries, Shadcn allows us to own the component code directly in our repository.
- **React Router DOM v6:** Handles client-side routing, enabling a snappy Single Page Application (SPA) experience without full page reloads.
- **React Hook Form & Zod:** Used together for building performant forms with strict, schema-based validation.

---

## ✨ Key Implementation Details

### 1. Strict-Mode Safe WebSockets
React 18's Strict Mode intentionally mounts, unmounts, and remounts components to detect side-effect bugs. This usually breaks WebSockets by causing race conditions (closing sockets before they connect, destroying references). 
We built a custom `useWebSocket` hook that strictly binds event listeners to their specific socket instances, ensuring rock-solid real-time chat even in development mode.

### 2. Infinite Scrolling Chat
To handle popular blogs with thousands of comments, we implemented cursor-based pagination combined with React Query's `useInfiniteQuery`. As the user scrolls up in the chat box, the application seamlessly fetches older messages in chunks without lagging the DOM.

### 3. Real-Time SSE Notifications
We integrated a global Server-Sent Events (SSE) listener in the root of the application. Whenever an action occurs (e.g., an Admin approves a blog), the backend pushes an event down the SSE stream. The frontend instantly catches this and triggers a toast notification for the user, completely eliminating the need for inefficient long-polling.

---

## 📂 Architecture & Directory Structure

```
frontend/
├── src/
│   ├── api/            # Axios client setup and interceptors (auto-injects JWT)
│   ├── components/     # Global & Reusable UI components (Shadcn)
│   ├── features/       # Feature-sliced modules (Auth, Blog, Chat, Features)
│   ├── hooks/          # Custom React hooks (e.g., useWebSocket)
│   ├── pages/          # Top-level Page components mapped to routes
│   ├── providers/      # Global Context Providers (AuthContext, ThemeContext)
│   └── lib/            # Utility functions (Tailwind merge, date formatters)
├── tailwind.config.js  # Tailwind design tokens and theme settings
└── vite.config.ts      # Vite config (Handles proxying to backend)
```

---

## 🔌 API Proxying

To avoid complex CORS (Cross-Origin Resource Sharing) issues during local development, we configure Vite to proxy all requests starting with `/api` directly to the FastAPI backend.

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      ws: true, // Crucial for proxying WebSocket traffic!
    }
  }
}
```

---

## 🚀 Quick Start & Setup

### 1. Prerequisites
- Node.js (v18+)
- Ensure the Backend API is running locally on `127.0.0.1:8000`.

### 2. Install Dependencies
```bash
cd frontend
npm install
```

### 3. Environment Variables (For Vercel Deployment)
If deploying to a different domain than your backend (e.g., Vercel + Render), you must provide the backend API URL:
Create a `.env` file in the frontend root (or configure in Vercel settings):
```env
VITE_API_URL=https://blog-platform-md24.onrender.com/api/v1
```
*(Leave empty for local Docker proxying).*

### 4. Run the Development Server
```bash
npm run dev
```
The application will launch and be available at `http://localhost:5173`.
