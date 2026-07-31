import { useState } from "react";
import { useMyDrafts } from "@/features/blogs/api";
import { BlogCard } from "@/components/blog/BlogCard";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Loader2, ChevronLeft, ChevronRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export const MyDrafts = () => {
  const [page, setPage] = useState(1);
  const limit = 9;
  const skip = (page - 1) * limit;

  const { data: blogs, isLoading, error } = useMyDrafts(skip, limit);

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
        Failed to load your drafts. Please try again later.
      </div>
    );
  }

  if ((!blogs || blogs.length === 0) && page === 1) {
    return (
      <div className="text-center py-16 space-y-4">
        <h2 className="text-2xl font-bold">No drafts found</h2>
        <Button asChild>
          <Link to="/blogs/new">Start a new draft</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">My Drafts</h1>
          <p className="text-muted-foreground">Work in progress that hasn't been submitted yet.</p>
        </div>
        <Button asChild>
          <Link to="/blogs/new">Write Blog</Link>
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {blogs?.map((blog) => (
          <BlogCard 
            key={blog.id}
            blog={blog}
            headerBadge={
              <Badge variant="outline">DRAFT</Badge>
            }
            footerActions={
              <div className="flex gap-2 w-full">
                <Button asChild variant="outline" className="flex-1">
                  <Link to={`/blogs/${blog.blog_group_id}`}>Preview</Link>
                </Button>
                <Button asChild variant="default" className="flex-1">
                  <Link to={`/blogs/${blog.blog_group_id}/edit`}>Edit</Link>
                </Button>
              </div>
            }
          />
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
