import { useState } from "react";
import { useAuth } from "@/providers/AuthProvider";
import { 
  useFeatureRequests, 
  useCreateFeatureRequest, 
  useUpdateFeatureRequestStatus
} from "@/features/featureRequests/api";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export function FeatureRequests() {
  const { user } = useAuth();
  const { data: featureRequests = [], isLoading } = useFeatureRequests();
  const createMutation = useCreateFeatureRequest();
  const updateStatusMutation = useUpdateFeatureRequestStatus();

  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("3");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(
      { title, description, priority: parseInt(priority) },
      {
        onSuccess: () => {
          setOpen(false);
          setTitle("");
          setDescription("");
          setPriority("3");
        }
      }
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "PENDING":
        return "bg-orange-500/10 text-orange-600 hover:bg-orange-500/20";
      case "ACCEPTED":
        return "bg-blue-500/10 text-blue-600 hover:bg-blue-500/20";
      case "DECLINED":
        return "bg-red-500/10 text-red-600 hover:bg-red-500/20";
      case "COMPLETED":
        return "bg-green-500/10 text-green-600 hover:bg-green-500/20";
      default:
        return "bg-gray-500/10 text-gray-600 hover:bg-gray-500/20";
    }
  };

  if (isLoading) {
    return <div className="text-center p-8">Loading...</div>;
  }

  return (
    <div className="space-y-8 animate-fade-in-up">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Feature Requests</h1>
          <p className="text-muted-foreground mt-1">Vote and track upcoming platform features.</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="rounded-full">Request Feature</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Submit a Feature Request</DialogTitle>
              <DialogDescription>
                Describe the feature you'd like to see. Our admins will review it.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input 
                  id="title" 
                  value={title} 
                  onChange={(e) => setTitle(e.target.value)} 
                  required 
                  placeholder="e.g. Dark Mode Support"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea 
                  id="description" 
                  value={description} 
                  onChange={(e) => setDescription(e.target.value)} 
                  required 
                  placeholder="Explain why this feature is useful..."
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="priority">Priority (1 = High, 5 = Low)</Label>
                <Input 
                  id="priority" 
                  type="number" 
                  min="1" max="5" 
                  value={priority} 
                  onChange={(e) => setPriority(e.target.value)} 
                />
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? "Submitting..." : "Submit Request"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {featureRequests.map((fr) => (
          <Card key={fr.id} className="group overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm border-white/20">
            <CardHeader className="pb-3">
              <div className="flex justify-between items-start gap-4">
                <CardTitle className="text-lg line-clamp-1 group-hover:text-primary transition-colors">
                  {fr.title}
                </CardTitle>
                <Badge className={`${getStatusColor(fr.status)} border-0 shadow-sm shrink-0`}>
                  {fr.status}
                </Badge>
              </div>
              <CardDescription className="text-xs">
                Requested on {new Date(fr.created_at).toLocaleDateString()}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground line-clamp-3">
                {fr.description}
              </p>
            </CardContent>
            {user?.role === "ADMIN" && fr.status !== "COMPLETED" && fr.status !== "DECLINED" && (
              <CardFooter className="pt-3 border-t flex gap-2 justify-end bg-secondary/20">
                {fr.status === "PENDING" && (
                  <>
                    <Button variant="outline" size="sm" onClick={() => updateStatusMutation.mutate({ id: fr.id, status: "DECLINED" })} disabled={updateStatusMutation.isPending}>
                      Decline
                    </Button>
                    <Button size="sm" onClick={() => updateStatusMutation.mutate({ id: fr.id, status: "ACCEPTED" })} disabled={updateStatusMutation.isPending}>
                      Accept
                    </Button>
                  </>
                )}
                {fr.status === "ACCEPTED" && (
                  <Button size="sm" onClick={() => updateStatusMutation.mutate({ id: fr.id, status: "COMPLETED" })} disabled={updateStatusMutation.isPending} className="w-full">
                    Mark as Completed
                  </Button>
                )}
              </CardFooter>
            )}
          </Card>
        ))}
      </div>
      
      {featureRequests.length === 0 && (
        <div className="text-center p-12 border rounded-xl bg-muted/20 border-dashed">
          <h3 className="text-lg font-medium text-foreground">No Feature Requests</h3>
          <p className="text-muted-foreground mt-2">Be the first to suggest a new idea!</p>
        </div>
      )}
    </div>
  );
}
