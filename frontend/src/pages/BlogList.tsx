import { useState, useEffect } from "react";
import { useApprovedBlogs } from "@/features/blogs/api";
import { BlogCard } from "@/components/blog/BlogCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { Link, useNavigate } from "react-router-dom";
import { Loader2, ChevronLeft, ChevronRight, Search } from "lucide-react";

export const BlogList = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const limit = 9;
  const skip = (page - 1) * limit;

  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [blogType, setBlogType] = useState<string>("ALL");
  const [sortParam, setSortParam] = useState<string>("newest");

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(handler);
  }, [search]);

  const handleBlogTypeChange = (value: string) => {
    setBlogType(value);
    setPage(1);
  };

  const handleSortChange = (value: string) => {
    setSortParam(value);
    setPage(1);
  };

  let sort_by = "created_at";
  let sort_order = "desc";
  if (sortParam === "oldest") {
    sort_order = "asc";
  } else if (sortParam === "title_asc") {
    sort_by = "title";
    sort_order = "asc";
  } else if (sortParam === "title_desc") {
    sort_by = "title";
    sort_order = "desc";
  }

  const { data: blogs, isLoading, error } = useApprovedBlogs(
    skip, limit, debouncedSearch, blogType, sort_by, sort_order
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">All Blogs</h1>
        <p className="text-muted-foreground">Read the latest published articles.</p>
      </div>

      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search blogs..."
            className="pl-8"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Select value={blogType} onValueChange={handleBlogTypeChange}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Blog Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All Types</SelectItem>
            <SelectItem value="ARTICLE">Article</SelectItem>
            <SelectItem value="TUTORIAL">Tutorial</SelectItem>
            <SelectItem value="NEWS">News</SelectItem>
            <SelectItem value="OPINION">Opinion</SelectItem>
          </SelectContent>
        </Select>
        <Select value={sortParam} onValueChange={handleSortChange}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Sort By" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="newest">Newest First</SelectItem>
            <SelectItem value="oldest">Oldest First</SelectItem>
            <SelectItem value="title_asc">Title A-Z</SelectItem>
            <SelectItem value="title_desc">Title Z-A</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading && page === 1 ? (
        <div className="flex h-[50vh] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <div className="text-center text-red-500 py-8">
          Failed to load blogs. Please try again later.
        </div>
      ) : (!blogs || blogs.length === 0) ? (
        <div className="text-center py-16">
          <h2 className="text-2xl font-bold mb-2">No blogs found</h2>
          <p className="text-muted-foreground">Try adjusting your search or filters.</p>
        </div>
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {blogs.map((blog) => (
              <div key={blog.id} onClick={() => navigate(`/blogs/${blog.blog_group_id}`)} className="cursor-pointer">
                <BlogCard 
                  blog={blog}
                  footerActions={
                    <Button asChild variant="secondary" className="w-full">
                      <Link to={`/blogs/${blog.blog_group_id}`} onClick={e => e.stopPropagation()}>Read More</Link>
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
        </>
      )}
    </div>
  );
};
