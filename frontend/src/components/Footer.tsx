import { Link } from "react-router-dom";
import {
  Github,
  Sparkles,
  Code2,
  BookOpen,
  Twitter,
  Mail,
  Linkedin,
} from "lucide-react";

export function Footer() {
  const currentYear = new Date().getFullYear();

  const socialLinks = [
    { name: "GitHub", href: "https://github.com/arpan-tanwar", icon: Github },
    {
      name: "LinkedIn",
      href: "https://www.linkedin.com/in/arpan-tanwar/",
      icon: Linkedin,
    },
    { name: "Twitter", href: "https://x.com/whyisarpan", icon: Twitter },
    { name: "Contact", href: "mailto:arpantanwar.at@gmail.com", icon: Mail },
  ];

  return (
    <footer
      className="w-full border-t backdrop-blur-md"
      style={{ backgroundColor: "rgba(14,20,32,0.6)" }}
    >
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Left Section */}
          <div className="flex items-center gap-8">
            {/* Brand */}
            <Link
              to="/"
              className="group flex items-center gap-2 transition-all hover:opacity-80"
            >
              <div className="relative">
                <div
                  className="absolute -inset-1 rounded-full opacity-20 blur-sm group-hover:opacity-30 transition-opacity"
                  style={{
                    background: "linear-gradient(135deg, #2563EB, #7C3AED)",
                  }}
                ></div>
                <div
                  className="relative h-7 w-7 rounded-full flex items-center justify-center"
                  style={{
                    background: "linear-gradient(135deg, #2563EB, #7C3AED)",
                  }}
                >
                  <div className="text-white font-bold text-xs">A</div>
                </div>
              </div>
              <div className="flex flex-col">
                <span className="font-bold bg-gradient-to-r from-blue-500 to-indigo-600 bg-clip-text text-transparent text-xl">
                  Animathic
                </span>
              </div>
            </Link>

            {/* Divider */}
            <div className="hidden md:block h-4 w-px bg-border"></div>

            {/* Quick Links */}
            <div className="flex items-center gap-4">
              <Link
                to="/how-it-works"
                className="text-xs text-muted-foreground hover:text-primary transition-colors"
              >
                How it Works
              </Link>
              <span className="text-xs text-muted-foreground/60">•</span>
              <a
                href="https://docs.manim.community"
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-muted-foreground hover:text-primary transition-colors"
              >
                Documentation
              </a>
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-6">
            {/* Social Links */}
            <div className="flex items-center gap-4">
              {socialLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex items-center gap-1.5 text-xs text-muted-foreground hover:text-primary transition-colors"
                >
                  <link.icon className="h-4 w-4 group-hover:scale-110 transition-transform" />
                  <span className="sr-only">{link.name}</span>
                </a>
              ))}
            </div>

            {/* Divider */}
            <div className="hidden md:block h-4 w-px bg-border"></div>

            {/* Copyright */}
            <p className="text-xs text-muted-foreground">
              © {currentYear} Animathic
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
