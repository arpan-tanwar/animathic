import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu } from "lucide-react";
import {
  SignedIn,
  SignedOut,
  UserButton,
  SignInButton,
} from "@clerk/clerk-react";

import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";
import { cn } from "@/lib/utils";

interface NavLink {
  name: string;
  href: string;
  external?: boolean;
}

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const navLinks: NavLink[] = [
    { name: "Home", href: "/" },
    { name: "How it Works", href: "/how-it-works" },
    { name: "Examples", href: "/examples" },
  ];

  return (
    <header
      className="sticky top-0 z-40 w-full border-b backdrop-blur-md"
      style={{ backgroundColor: "rgba(14,20,32,0.7)" }}
    >
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <Link
            to="/"
            className="group flex items-center gap-2 transition-opacity hover:opacity-90"
          >
            <div className="relative">
              <div
                className="absolute -inset-1 rounded-xl opacity-20 blur-sm group-hover:opacity-30"
                style={{
                  background: "linear-gradient(135deg, #2563EB, #7C3AED)",
                }}
              />
              <div
                className="relative h-8 w-8 rounded-xl flex items-center justify-center"
                style={{
                  background: "linear-gradient(135deg, #2563EB, #7C3AED)",
                }}
              >
                <div className="text-white font-bold text-sm">A</div>
              </div>
            </div>
            <span className="hidden font-semibold sm:inline-block text-lg tracking-tight">
              Animathic
            </span>
          </Link>
        </div>

        {/* Desktop Nav */}
        <nav className="hidden items-center gap-6 md:flex">
          {navLinks.map((link) =>
            link.external ? (
              <a
                key={link.name}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className={cn(
                  "text-sm font-medium transition-colors hover:text-primary",
                  location.pathname === link.href
                    ? "text-primary"
                    : "text-muted-foreground"
                )}
              >
                {link.name}
              </a>
            ) : (
              <Link
                key={link.name}
                to={link.href}
                className={cn(
                  "text-sm font-medium transition-colors hover:text-primary",
                  location.pathname === link.href
                    ? "text-primary"
                    : "text-muted-foreground"
                )}
              >
                {link.name}
              </Link>
            )
          )}
        </nav>

        <div className="flex items-center gap-2">
          <ThemeToggle />

          <SignedOut>
            <SignInButton mode="modal">
              <Button size="sm" variant="default">
                Log In
              </Button>
            </SignInButton>
          </SignedOut>

          <SignedIn>
            <Link to="/dashboard">
              <Button
                variant="ghost"
                size="sm"
                className={cn(
                  "mr-2",
                  location.pathname === "/dashboard" ? "bg-accent" : ""
                )}
              >
                Dashboard
              </Button>
            </Link>
            <UserButton afterSignOutUrl="/" />
          </SignedIn>

          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle menu</span>
          </Button>
        </div>
      </div>

      {/* Mobile Nav */}
      {mobileMenuOpen && (
        <div className="md:hidden">
          <div className="flex flex-col space-y-3 p-4 border-t">
            {navLinks.map((link) =>
              link.external ? (
                <a
                  key={link.name}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={cn(
                    "px-2 py-1 text-sm font-medium rounded-md transition-colors",
                    location.pathname === link.href
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:bg-accent/50"
                  )}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {link.name}
                </a>
              ) : (
                <Link
                  key={link.name}
                  to={link.href}
                  className={cn(
                    "px-2 py-1 text-sm font-medium rounded-md transition-colors",
                    location.pathname === link.href
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:bg-accent/50"
                  )}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {link.name}
                </Link>
              )
            )}
            <SignedIn>
              <Link
                to="/dashboard"
                className={cn(
                  "px-2 py-1 text-sm font-medium rounded-md transition-colors",
                  location.pathname === "/dashboard"
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:bg-accent/50"
                )}
                onClick={() => setMobileMenuOpen(false)}
              >
                Dashboard
              </Link>
            </SignedIn>
          </div>
        </div>
      )}
    </header>
  );
}
