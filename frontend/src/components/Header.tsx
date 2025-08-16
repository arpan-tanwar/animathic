import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  UserButton,
} from "@clerk/clerk-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Menu, X, Sparkles, Play, BookOpen, Grid3x3 } from "lucide-react";
import { cn } from "@/lib/utils";

interface NavLink {
  name: string;
  href: string;
  icon?: React.ReactNode;
  external?: boolean;
}

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  const navLinks: NavLink[] = [
    {
      name: "Examples",
      href: "/examples",
      icon: <Grid3x3 className="w-4 h-4" />
    },
    {
      name: "How it Works",
      href: "/how-it-works", 
      icon: <BookOpen className="w-4 h-4" />
    },
    {
      name: "Generate",
      href: "/generate",
      icon: <Play className="w-4 h-4" />
    }
  ];

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const isActivePage = (href: string) => {
    return location.pathname === href;
  };

  return (
    <header className={cn(
      "sticky top-0 z-50 w-full transition-all duration-300",
      scrolled 
        ? "glass-effect shadow-lg" 
        : "bg-transparent"
    )}>
      <div className="container-wide">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <Link 
              to="/" 
              className="flex items-center gap-3 hover:opacity-80 hover-scale transition-all duration-200 focus-ring rounded-lg px-2 py-1"
            >
              <div className="relative">
                <div className="w-8 h-8 rounded-lg bg-gradient-primary flex items-center justify-center hover-glow transition-all duration-300">
                  <Sparkles className="w-5 h-5 text-white group-hover:animate-wiggle" />
                </div>
                <div className="absolute inset-0 rounded-lg bg-gradient-primary opacity-20 blur-sm"></div>
              </div>
              <span className="text-xl font-bold text-gradient-primary hover:scale-105 transition-transform duration-200">
                Animathic
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                to={link.href}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 focus-ring hover-lift",
                  isActivePage(link.href)
                    ? "text-primary bg-surface-secondary border border-subtle hover-scale"
                    : "text-secondary hover:text-primary hover:bg-surface-primary hover-scale"
                )}
              >
                {link.icon}
                <span>{link.name}</span>
              </Link>
            ))}
          </nav>

          {/* Desktop Actions */}
          <div className="hidden md:flex items-center gap-3">
            <SignedOut>
              <SignInButton>
                <Button variant="ghost" size="sm" className="text-secondary hover:text-primary">
                  Sign In
                </Button>
              </SignInButton>
              <Button 
                asChild 
                size="sm"
                className="btn-primary hover-lift hover-glow"
              >
                <Link to="/generate">
                  Get Started
                </Link>
              </Button>
            </SignedOut>
            
            <SignedIn>
              <Button 
                variant="ghost" 
                size="sm" 
                asChild
                className="text-secondary hover:text-primary"
              >
                <Link to="/dashboard">Dashboard</Link>
              </Button>
              <UserButton 
                appearance={{
                  elements: {
                    avatarBox: "w-8 h-8"
                  }
                }}
              />
            </SignedIn>
            
            <ThemeToggle />
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-secondary hover:text-primary"
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="md:hidden border-t border-subtle bg-surface-primary/95 backdrop-blur-lg">
          <div className="container-wide py-4">
            <nav className="space-y-2">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  to={link.href}
                  onClick={() => setIsMenuOpen(false)}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200",
                    isActivePage(link.href)
                      ? "text-primary bg-surface-secondary border border-subtle"
                      : "text-secondary hover:text-primary hover:bg-surface-secondary"
                  )}
                >
                  {link.icon}
                  <span>{link.name}</span>
                </Link>
              ))}
            </nav>

            {/* Mobile Actions */}
            <div className="pt-4 mt-4 border-t border-subtle space-y-3">
              <SignedOut>
                <SignInButton>
                  <Button 
                    variant="ghost" 
                    className="w-full justify-start text-secondary hover:text-primary"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Sign In
                  </Button>
                </SignInButton>
                <Button 
                  asChild 
                  className="w-full btn-primary"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <Link to="/generate">
                    Get Started
                  </Link>
                </Button>
              </SignedOut>
              
              <SignedIn>
                <Button 
                  variant="ghost" 
                  asChild
                  className="w-full justify-start text-secondary hover:text-primary"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <Link to="/dashboard">Dashboard</Link>
                </Button>
                <div className="flex items-center justify-between">
                  <UserButton 
                    appearance={{
                      elements: {
                        avatarBox: "w-8 h-8"
                      }
                    }}
                  />
                  <ThemeToggle />
                </div>
              </SignedIn>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}