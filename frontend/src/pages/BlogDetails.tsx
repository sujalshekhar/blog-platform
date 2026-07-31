import { useParams, useNavigate, Link } from "react-router-dom";
import { useBlog, blogsApi } from "@/features/blogs/api";
import { BlogChat } from "@/components/BlogChat";
import { useAuth } from "@/providers/AuthProvider";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Loader2, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

export const BlogDetails = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const blogId = id ? parseInt(id) : 0;
  const { data: blog, isLoading, error } = useBlog(blogId);

  // Optimistic Updates Mutations
  const submitMutation = useMutation({
    mutationFn: () => blogsApi.submitBlog(blogId),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ["blogs", blogId] });
      const previousBlog = queryClient.getQueryData(["blogs", blogId]);
      queryClient.setQueryData(["blogs", blogId], (old: any) => ({ ...old, status: "PENDING" }));
      return { previousBlog };
    },
    onError: (err, newBlog, context) => {
      queryClient.setQueryData(["blogs", blogId], context?.previousBlog);
      toast.error("Failed to submit blog");
    },
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["blogs"] }),
    onSuccess: () => toast.success("Blog submitted for approval"),
  });

  const approveMutation = useMutation({
    mutationFn: () => blogsApi.approveBlog(blogId),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ["blogs", blogId] });
      const previousBlog = queryClient.getQueryData(["blogs", blogId]);
      queryClient.setQueryData(["blogs", blogId], (old: any) => ({ ...old, status: "APPROVED" }));
      return { previousBlog };
    },
    onError: (err, newBlog, context) => {
      queryClient.setQueryData(["blogs", blogId], context?.previousBlog);
      toast.error("Failed to approve blog");
    },
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["blogs"] }),
    onSuccess: () => toast.success("Blog approved"),
  });

  const rejectMutation = useMutation({
    mutationFn: () => blogsApi.rejectBlog(blogId),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ["blogs", blogId] });
      const previousBlog = queryClient.getQueryData(["blogs", blogId]);
      queryClient.setQueryData(["blogs", blogId], (old: any) => ({ ...old, status: "REJECTED" }));
      return { previousBlog };
    },
    onError: (err, newBlog, context) => {
      queryClient.setQueryData(["blogs", blogId], context?.previousBlog);
      toast.error("Failed to reject blog");
    },
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["blogs"] }),
    onSuccess: () => toast.success("Blog rejected"),
  });

  const deleteMutation = useMutation({
    mutationFn: () => blogsApi.deleteBlog(blogId),
    onSuccess: () => {
      toast.success("Blog deleted successfully");
      queryClient.invalidateQueries({ queryKey: ["blogs"] });
      navigate("/my-blogs");
    },
    onError: () => toast.error("Failed to delete blog"),
  });

  if (isLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || !blog) {
    return (
      <div className="text-center text-red-500 py-8">
        Failed to load the blog or it does not exist.
      </div>
    );
  }

  const isAuthor = user?.id === blog.author_id;
  const isModerator = user?.role === "ADMIN" || user?.role === "APPROVER";

  return (
    <div className="max-w-4xl mx-auto space-y-12 pb-24">
      <Button variant="ghost" onClick={() => navigate(-1)} className="mb-4 hover:bg-secondary/50 rounded-full transition-all">
        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Articles
      </Button>

      {blog.cover_image_url && (
        <div className="w-full h-[350px] md:h-[500px] rounded-3xl overflow-hidden mb-12 shadow-2xl shadow-primary/10 relative group">
          <div className="absolute inset-0 bg-black/5 group-hover:bg-transparent transition-colors duration-500 z-10 pointer-events-none"></div>
          <img src={blog.cover_image_url} alt={blog.title} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" />
        </div>
      )}

      <div className="space-y-8">
        <div className="flex items-center gap-4">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tighter lg:text-7xl leading-tight text-foreground">{blog.title}</h1>
        </div>
        
        <div className="flex flex-wrap items-center justify-between text-muted-foreground border-b border-border/40 pb-8 gap-4">
          <div className="flex items-center gap-4 text-sm font-medium">
            <span className="flex items-center gap-2 bg-secondary/30 px-3 py-1.5 rounded-full text-foreground/80">
              <div className="h-6 w-6 rounded-full bg-primary/20 flex items-center justify-center text-primary text-xs font-bold">
                 {blog.author?.first_name?.charAt(0) || 'A'}
              </div>
              {blog.author ? `${blog.author.first_name} ${blog.author.last_name || ''}` : `Author #${blog.author_id}`}
            </span>
            <span>•</span>
            <span className="uppercase tracking-widest text-xs opacity-70">{new Date(blog.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</span>
            <Badge variant={blog.status === "APPROVED" ? "default" : blog.status === "REJECTED" ? "destructive" : "secondary"} className="ml-2">
              {blog.status}
            </Badge>
          </div>
          
          <div className="flex items-center gap-2">
            {(isAuthor || isModerator) && (
              <Button size="sm" variant="outline" asChild>
                <Link to={`/blogs/${blog.blog_group_id}/history`}>History</Link>
              </Button>
            )}
            {isAuthor && blog.status === "DRAFT" && (
              <Button size="sm" onClick={() => submitMutation.mutate()} disabled={submitMutation.isPending}>
                {submitMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Submit for Approval"}
              </Button>
            )}
            {isAuthor && (
              <Button size="sm" variant="outline" asChild>
                <Link to={`/blogs/${blog.blog_group_id}/edit`}>Edit</Link>
              </Button>
            )}
            
            {isModerator && blog.status === "PENDING" && (
              <>
                <Button size="sm" onClick={() => approveMutation.mutate()} disabled={approveMutation.isPending}>
                  Approve
                </Button>
                <Button size="sm" variant="destructive" onClick={() => rejectMutation.mutate()} disabled={rejectMutation.isPending}>
                  Reject
                </Button>
              </>
            )}

            {(isAuthor || isModerator) && (
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button size="sm" variant="destructive">Delete</Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                    <AlertDialogDescription>
                      This will soft-delete the blog and all its versions. It cannot be recovered from the UI.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={() => deleteMutation.mutate()}>
                      {deleteMutation.isPending ? "Deleting..." : "Delete"}
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            )}
          </div>
        </div>
      </div>

      <div 
        className="prose prose-slate dark:prose-invert prose-lg md:prose-xl max-w-none prose-headings:font-bold prose-headings:tracking-tight prose-a:text-primary hover:prose-a:text-primary/80 prose-img:rounded-2xl prose-img:shadow-lg prose-p:leading-relaxed"
        dangerouslySetInnerHTML={{ __html: blog.content }} 
      />

      {blog.status === "APPROVED" && (
        <BlogChat blogGroupId={blog.blog_group_id} />
      )}
    </div>
  );
};
