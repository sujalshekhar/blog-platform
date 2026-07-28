import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/providers/AuthProvider";
import { PlusCircle, FileText, LayoutList } from "lucide-react";

export const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back, {user?.first_name}!</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Create New</CardTitle>
            <PlusCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Write Blog</div>
            <p className="text-xs text-muted-foreground mt-1">Start a new draft</p>
            <Button asChild className="mt-4 w-full" size="sm">
              <Link to="/blogs/new">Create Blog</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">My Blogs</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">View Published</div>
            <p className="text-xs text-muted-foreground mt-1">Manage your active posts</p>
            <Button asChild className="mt-4 w-full" variant="secondary" size="sm">
              <Link to="/my-blogs">Go to My Blogs</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Public List</CardTitle>
            <LayoutList className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Read Others</div>
            <p className="text-xs text-muted-foreground mt-1">Explore all published blogs</p>
            <Button asChild className="mt-4 w-full" variant="outline" size="sm">
              <Link to="/blogs">Explore</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
