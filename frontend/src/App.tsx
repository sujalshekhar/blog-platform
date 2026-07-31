import { Routes, Route } from "react-router-dom";
import { ProtectedRoute, PublicRoute } from "./routes/ProtectedRoute";
import { AppLayout } from "./layouts/AppLayout";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";

import { Dashboard } from "./pages/Dashboard";
import { BlogList } from "./pages/BlogList";
import { MyBlogs } from "./pages/MyBlogs";
import { MyDrafts } from "./pages/MyDrafts";
import { CreateBlog } from "./pages/CreateBlog";
import { BlogDetails } from "./pages/BlogDetails";
import { EditBlog } from "./pages/EditBlog";
import { PendingApprovals } from "./pages/PendingApprovals";
import { BlogHistory } from "./pages/BlogHistory";
import { FeatureRequests } from "./pages/FeatureRequests";

const NotFound = () => <div className="text-center p-8 text-2xl font-bold">404 Not Found</div>;

export function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route element={<PublicRoute />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>

      {/* Protected routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/blogs" element={<BlogList />} />
          <Route path="/my-blogs" element={<MyBlogs />} />
          <Route path="/my-drafts" element={<MyDrafts />} />
          <Route path="/pending" element={<PendingApprovals />} />
          <Route path="/blogs/new" element={<CreateBlog />} />
          <Route path="/blogs/:id" element={<BlogDetails />} />
          <Route path="/blogs/:id/edit" element={<EditBlog />} />
          <Route path="/blogs/:id/history" element={<BlogHistory />} />
          <Route path="/features" element={<FeatureRequests />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;
