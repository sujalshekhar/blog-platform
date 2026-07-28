import { useApprovedBlogs } from "@/features/blogs/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Loader2 } from "lucide-react";

export const BlogList = () => {
  const { data: blogs, isLoading, error } = useApprovedBlogs();

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
        Failed to load blogs. Please try again later.
      </div>
    );
  }

  if (!blogs || blogs.length === 0) {
    return (
      <div className="text-center py-16">
        <h2 className="text-2xl font-bold mb-2">No blogs found</h2>
        <p className="text-muted-foreground">Check back later for new content.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">All Blogs</h1>
        <p className="text-muted-foreground">Read the latest published articles.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {blogs.map((blog) => (
          <Card key={blog.id} className="group overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-xl dark:hover:shadow-primary/5 flex flex-col cursor-pointer" onClick={() => navigate(`/blogs/${blog.blog_group_id}`)}>
            {blog.cover_image_url && (
              <div className="h-48 w-full overflow-hidden">
                <img 
                  src={blog.cover_image_url} 
                  alt={blog.title}
                  className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                />
              </div>
            )}
            <CardHeader>
              <CardTitle className="line-clamp-2">{blog.title}</CardTitle>
              <CardDescription>
                {new Date(blog.created_at).toLocaleDateString()}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              {/* Extracting some plain text from rich text if possible, or just a placeholder snippet */}
              <div 
                className="text-sm text-muted-foreground line-clamp-3"
                dangerouslySetInnerHTML={{ __html: blog.content }} 
              />
            </CardContent>
            <CardFooter>
              <Button asChild variant="secondary" className="w-full">
                <Link to={`/blogs/${blog.blog_group_id}`}>Read More</Link>
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
};
