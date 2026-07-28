import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import ReactQuill from "react-quill-new";
import "react-quill-new/dist/quill.snow.css";
import { blogsApi, useBlog } from "@/features/blogs/api";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { useQueryClient } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";

const blogSchema = z.object({
  title: z.string().min(1, { message: "Title is required" }).max(255),
  content: z.string().min(10, { message: "Content must be at least 10 characters" }),
  cover_image_url: z.string().url({ message: "Must be a valid URL" }).optional().or(z.literal("")),
});

export const EditBlog = () => {
  const { id } = useParams<{ id: string }>();
  const blogId = id ? parseInt(id) : 0;
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isSaving, setIsSaving] = useState(false);

  const { data: blog, isLoading, error } = useBlog(blogId);

  const form = useForm<z.infer<typeof blogSchema>>({
    resolver: zodResolver(blogSchema),
    defaultValues: { title: "", content: "", cover_image_url: "" },
  });

  // Populate form when blog loads
  useEffect(() => {
    if (blog) {
      form.reset({
        title: blog.title,
        content: blog.content,
        cover_image_url: blog.cover_image_url || "",
      });
    }
  }, [blog, form]);

  async function onSubmit(values: z.infer<typeof blogSchema>) {
    setIsSaving(true);
    try {
      const dataToSubmit = {
        ...values,
        cover_image_url: values.cover_image_url || undefined,
      };
      await blogsApi.updateBlog(blogId, dataToSubmit);
      toast.success("Blog updated successfully!");
      queryClient.invalidateQueries({ queryKey: ["blogs"] });
      navigate(`/blogs/${blogId}`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to update blog");
    } finally {
      setIsSaving(false);
    }
  }

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
        Failed to load blog for editing.
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Edit Blog</h1>
          <p className="text-muted-foreground">Updating version {blog.version}</p>
        </div>
      </div>

      <Card>
        <CardContent className="pt-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Title</FormLabel>
                    <FormControl>
                      <Input placeholder="An interesting title..." {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="cover_image_url"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Cover Image URL (Optional)</FormLabel>
                    <FormControl>
                      <Input placeholder="https://example.com/image.jpg" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="content"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Content</FormLabel>
                    <FormControl>
                      <div className="bg-white dark:bg-slate-950 text-black dark:text-white rounded-md">
                        <Controller
                          name="content"
                          control={form.control}
                          render={({ field }) => (
                            <ReactQuill
                              theme="snow"
                              value={field.value}
                              onChange={field.onChange}
                              className="h-64 mb-12"
                            />
                          )}
                        />
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex justify-end gap-4 mt-8">
                <Button type="button" variant="outline" onClick={() => navigate(-1)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isSaving}>
                  {isSaving ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
};
