import { useMyDrafts } from "@/features/blogs/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export const MyDrafts = () => {
  const { data: blogs, isLoading, error } = useMyDrafts();

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
        Failed to load your drafts. Please try again later.
      </div>
    );
  }

  if (!blogs || blogs.length === 0) {
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
        {blogs.map((blog) => (
          <Card key={blog.id} className="group overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-xl dark:hover:shadow-primary/5 flex flex-col">
            <CardHeader>
              <div className="flex justify-between items-start mb-2">
                <Badge variant="outline">DRAFT</Badge>
                <span className="text-xs text-muted-foreground">v{blog.version}</span>
              </div>
              <CardTitle className="line-clamp-2">{blog.title}</CardTitle>
              <CardDescription>
                Last edited {new Date(blog.updated_at).toLocaleDateString()}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <div 
                className="text-sm text-muted-foreground line-clamp-3"
                dangerouslySetInnerHTML={{ __html: blog.content }} 
              />
            </CardContent>
            <CardFooter className="gap-2">
              <Button asChild variant="outline" className="w-full">
                <Link to={`/blogs/${blog.blog_group_id}`}>Preview</Link>
              </Button>
              <Button asChild variant="default" className="w-full">
                <Link to={`/blogs/${blog.blog_group_id}/edit`}>Edit</Link>
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
};
