import { useState } from "react";
import { useAllActiveBlogs } from "@/features/blogs/api";
import { BlogCard } from "@/components/blog/BlogCard";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Loader2, ChevronLeft, ChevronRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export const PendingApprovals = () => {
  const [page, setPage] = useState(1);
  const limit = 20; // larger limit since we filter locally
  const skip = (page - 1) * limit;

  const { data: blogs, isLoading, error } = useAllActiveBlogs(skip, limit);

  if (isLoading && page === 1) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-500 py-8">
        Failed to load pending approvals.
      </div>
    );
  }

  // Filter only pending blogs
  const pendingBlogs = blogs?.filter(b => b.status === "PENDING") || [];

  if (pendingBlogs.length === 0 && page === 1) {
    return (
      <div className="text-center py-16 space-y-4">
        <h2 className="text-2xl font-bold">No Pending Approvals</h2>
        <p className="text-muted-foreground">All caught up! No blogs require moderation right now.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Pending Approvals</h1>
          <p className="text-muted-foreground">Review and moderate user submitted blogs.</p>
        </div>
      </div>

      {pendingBlogs.length === 0 && page > 1 && (
        <div className="text-center py-8 text-muted-foreground">
          No pending approvals on this page.
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {pendingBlogs.map((blog) => (
          <div key={blog.id} className="[&>div]:border-yellow-200 dark:[&>div]:border-yellow-900 [&>div]:bg-yellow-50/50 dark:[&>div]:bg-yellow-900/10 h-full">
            <BlogCard 
              blog={blog}
              headerBadge={
                <Badge variant="secondary" className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100">
                  PENDING REVIEW
                </Badge>
              }
              footerActions={
                <Button asChild className="w-full">
                  <Link to={`/blogs/${blog.blog_group_id}`}>Review Blog</Link>
                </Button>
              }
            />
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between mt-8">
        <Button
          variant="outline"
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1 || isLoading}
        >
          <ChevronLeft className="mr-2 h-4 w-4" /> Previous
        </Button>
        <span className="text-sm text-muted-foreground">Page {page}</span>
        <Button
          variant="outline"
          onClick={() => setPage(p => p + 1)}
          disabled={!blogs || blogs.length < limit || isLoading}
        >
          Next <ChevronRight className="ml-2 h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};
