import { Link } from "react-router-dom";
import { Sparkles, Github, Twitter, Mail, Heart } from "lucide-react";

export function Footer() {
  const currentYear = new Date().getFullYear();

  const socialLinks = [
    {
      name: "GitHub",
      href: "https://github.com/arpan-tanwar",
      icon: <Github className="w-5 h-5" />,
    },
    {
      name: "Twitter",
      href: "https://x.com/whyisarpan",
      icon: <Twitter className="w-5 h-5" />,
    },
    {
      name: "Email",
      href: "mailto:arpanatanwar.at@gmail.com",
      icon: <Mail className="w-5 h-5" />,
    },
  ];

  return (
    <footer className="border-t border-subtle bg-surface-primary/50 backdrop-blur-sm">
      <div className="container-wide">
        {/* Main footer content */}
        <div className="py-12 lg:py-16">
          <div className="flex flex-col items-center text-center space-y-8">
            {/* Brand section */}
            <div className="space-y-4">
              <div className="flex items-center justify-center gap-3">
                <div className="relative">
                  <div className="w-10 h-10 rounded-lg bg-gradient-primary flex items-center justify-center hover-glow transition-all duration-300">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <div className="absolute inset-0 rounded-lg bg-gradient-primary opacity-20 blur-sm"></div>
                </div>
                <span className="text-2xl font-bold text-gradient-primary">
                  Animathic
                </span>
              </div>

              <p className="text-secondary leading-relaxed max-w-md mx-auto">
                Create beautiful mathematical animations with AI. Transform
                complex concepts into engaging visual content.
              </p>
            </div>

            {/* Social links */}
            <div className="flex items-center justify-center gap-4">
              {socialLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="
                    w-12 h-12 rounded-xl bg-surface-secondary border border-subtle
                    flex items-center justify-center text-muted hover:text-primary
                    hover:border-emphasis transition-all duration-200 hover-lift hover-scale
                    focus-ring group
                  "
                  aria-label={link.name}
                >
                  <span className="group-hover:animate-bounce-soft">
                    {link.icon}
                  </span>
                </a>
              ))}
            </div>

            {/* Bottom section */}
            <div className="pt-8 border-t border-subtle w-full">
              <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-2 text-sm text-muted">
                  <span>
                    &copy; {currentYear} Animathic. All rights reserved.
                  </span>
                </div>

                <div className="flex items-center gap-2 text-sm text-muted">
                  <span>Made with</span>
                  <Heart className="w-4 h-4 text-red-400 fill-current animate-pulse-glow" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
