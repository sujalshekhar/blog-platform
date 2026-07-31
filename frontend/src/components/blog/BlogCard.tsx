import React from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Blog } from "@/types";

export interface BlogCardProps {
  blog: Blog;
  /** Optional badge to display at the top of the card */
  headerBadge?: React.ReactNode;
  /** Custom actions to display in the footer instead of the default Link */
  footerActions?: React.ReactNode;
}

/**
 * A highly reusable card component for displaying blog summaries across various feeds.
 */
export const BlogCard: React.FC<BlogCardProps> = ({ blog, headerBadge, footerActions }) => {
  return (
    <Card className="group overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-xl dark:hover:shadow-primary/5 flex flex-col">
      <CardHeader>
        <div className="flex justify-between items-start mb-2">
          {headerBadge || <div />}
          <span className="text-xs text-muted-foreground">
            {blog.author ? `${blog.author.first_name} ${blog.author.last_name || ''}` : `Author #${blog.author_id}`}
          </span>
        </div>
        <CardTitle className="line-clamp-2">{blog.title}</CardTitle>
        <CardDescription>
          Updated {new Date(blog.updated_at).toLocaleDateString()}
        </CardDescription>
      </CardHeader>
      
      {blog.cover_image_url && (
        <div className="w-full h-48 overflow-hidden">
          <img 
            src={blog.cover_image_url} 
            alt={blog.title} 
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
        </div>
      )}
      
      <CardContent className="flex-1 mt-4">
        <div 
          className="text-sm text-muted-foreground line-clamp-3"
          dangerouslySetInnerHTML={{ __html: blog.content }} 
        />
      </CardContent>
      
      <CardFooter>
        {footerActions}
      </CardFooter>
    </Card>
  );
};
