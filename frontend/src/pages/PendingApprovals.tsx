import { useAllActiveBlogs } from "@/features/blogs/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export const PendingApprovals = () => {
  const { data: blogs, isLoading, error } = useAllActiveBlogs();

  if (isLoading) {
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

  if (pendingBlogs.length === 0) {
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

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {pendingBlogs.map((blog) => (
          <Card key={blog.id} className="group overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-xl dark:hover:shadow-primary/5 flex flex-col border-yellow-200 dark:border-yellow-900 bg-yellow-50/50 dark:bg-yellow-900/10">
            <CardHeader>
              <div className="flex justify-between items-start mb-2">
                <Badge variant="secondary" className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100">
                  PENDING REVIEW
                </Badge>
                <span className="text-xs text-muted-foreground">{blog.author ? `${blog.author.first_name} ${blog.author.last_name || ''}` : `Author #${blog.author_id}`}</span>
              </div>
              <CardTitle className="line-clamp-2">{blog.title}</CardTitle>
              <CardDescription>
                Submitted {new Date(blog.updated_at).toLocaleDateString()}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <div 
                className="text-sm text-muted-foreground line-clamp-3"
                dangerouslySetInnerHTML={{ __html: blog.content }} 
              />
            </CardContent>
            <CardFooter>
              <Button asChild className="w-full">
                <Link to={`/blogs/${blog.blog_group_id}`}>Review Blog</Link>
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
};
