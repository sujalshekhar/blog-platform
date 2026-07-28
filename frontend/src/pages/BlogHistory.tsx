import { useParams, useNavigate } from "react-router-dom";
import { useBlogHistory } from "@/features/blogs/api";
import { Loader2, ArrowLeft, History } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export const BlogHistory = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const blogId = id ? parseInt(id) : 0;
  
  const { data: history, isLoading, error } = useBlogHistory(blogId);

  if (isLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || !history) {
    return (
      <div className="text-center text-red-500 py-8">
        Failed to load blog history.
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Button variant="ghost" onClick={() => navigate(-1)} className="mb-4">
        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Blog
      </Button>

      <div className="flex items-center gap-2 mb-6">
        <History className="h-6 w-6" />
        <h1 className="text-3xl font-bold tracking-tight">Version History</h1>
      </div>

      <div className="space-y-4">
        {history.map((version) => (
          <Card key={version.id} className={version.is_active_version ? "border-primary" : "opacity-80"}>
            <CardHeader>
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">Version {version.version}</Badge>
                  {version.is_active_version && (
                    <Badge variant="default" className="bg-green-600">Active</Badge>
                  )}
                  <Badge variant={version.status === "APPROVED" ? "default" : version.status === "REJECTED" ? "destructive" : "secondary"}>
                    {version.status}
                  </Badge>
                </div>
                <span className="text-sm text-muted-foreground">
                  {new Date(version.created_at).toLocaleString()}
                </span>
              </div>
              <CardTitle>{version.title}</CardTitle>
              {version.approved_by && (
                <CardDescription>
                  Moderated by User #{version.approved_by} on {new Date(version.approved_at!).toLocaleString()}
                </CardDescription>
              )}
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground p-4 bg-muted/50 rounded-md">
                <div 
                  className="line-clamp-4"
                  dangerouslySetInnerHTML={{ __html: version.content }} 
                />
              </div>
            </CardContent>
          </Card>
        ))}
        {history.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            No history found for this blog.
          </div>
        )}
      </div>
    </div>
  );
};
