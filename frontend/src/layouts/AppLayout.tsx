import { Link, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "@/providers/AuthProvider";
import { Button } from "@/components/ui/button";

export const AppLayout = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navigation = [
    { name: "Dashboard", href: "/" },
    { name: "All Blogs", href: "/blogs" },
    { name: "My Blogs", href: "/my-blogs" },
    { name: "My Drafts", href: "/my-drafts" },
    ...(user?.role === "ADMIN" || user?.role === "APPROVER"
      ? [{ name: "Pending Approvals", href: "/pending" }]
      : []),
  ];

  return (
    <div className="min-h-screen flex flex-col bg-transparent">
      <header className="sticky top-0 z-40 w-full border-b bg-white/70 backdrop-blur-lg dark:bg-slate-950/70 border-b-border/40 shadow-sm transition-all duration-300">
        <div className="container flex h-16 items-center justify-between px-4">
          <div className="flex gap-6 md:gap-10">
            <Link to="/" className="flex items-center space-x-2 group">
              <span className="inline-block font-extrabold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-400 group-hover:to-primary transition-all duration-500">BlogPlatform</span>
            </Link>
            <nav className="hidden md:flex gap-6">
              {navigation.map((item) => (
                <Link
                  key={item.href}
                  to={item.href}
                  className={`flex items-center text-sm font-medium transition-all duration-300 relative after:absolute after:-bottom-[21px] after:left-0 after:h-[2px] after:w-full after:origin-bottom-right after:scale-x-0 after:bg-primary after:transition-transform hover:after:origin-bottom-left hover:after:scale-x-100 hover:text-foreground ${
                    location.pathname === item.href
                      ? "text-foreground after:scale-x-100 after:origin-bottom-left"
                      : "text-foreground/60"
                  }`}
                >
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-muted-foreground hidden md:inline-block bg-secondary/50 px-3 py-1 rounded-full">
              {user?.first_name} {user?.last_name} <span className="opacity-60 ml-1">({user?.role})</span>
            </span>
            <Button variant="outline" size="sm" onClick={logout} className="rounded-full hover:bg-destructive hover:text-destructive-foreground transition-colors">
              Log out
            </Button>
          </div>
        </div>
      </header>
      <main className="flex-1 container mx-auto p-4 md:p-8 animate-fade-in-up">
        <Outlet />
      </main>
    </div>
  );
};
