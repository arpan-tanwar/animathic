import { Link } from "react-router-dom";
import { Sparkles, Github, Twitter, Mail, Heart } from "lucide-react";

export function Footer() {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    product: [
      { name: "Examples", href: "/examples" },
      { name: "How it Works", href: "/how-it-works" },
      { name: "Generate", href: "/generate" },
      { name: "Pricing", href: "#" }
    ],
    company: [
      { name: "About", href: "#" },
      { name: "Blog", href: "#" },
      { name: "Careers", href: "#" },
      { name: "Contact", href: "#" }
    ],
    legal: [
      { name: "Privacy Policy", href: "#" },
      { name: "Terms of Service", href: "#" },
      { name: "Cookie Policy", href: "#" }
    ]
  };

  const socialLinks = [
    {
      name: "GitHub",
      href: "#",
      icon: <Github className="w-5 h-5" />
    },
    {
      name: "Twitter", 
      href: "#",
      icon: <Twitter className="w-5 h-5" />
    },
    {
      name: "Email",
      href: "mailto:hello@animathic.com",
      icon: <Mail className="w-5 h-5" />
    }
  ];

  return (
    <footer className="border-t border-subtle bg-surface-primary/50 backdrop-blur-sm">
      <div className="container-wide">
        {/* Main footer content */}
        <div className="py-12 lg:py-16">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-8 lg:gap-12">
            {/* Brand section */}
            <div className="lg:col-span-4 space-y-4">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-8 h-8 rounded-lg bg-gradient-primary flex items-center justify-center">
                    <Sparkles className="w-5 h-5 text-white" />
                  </div>
                  <div className="absolute inset-0 rounded-lg bg-gradient-primary opacity-20 blur-sm"></div>
                </div>
                <span className="text-xl font-bold text-gradient-primary">
                  Animathic
                </span>
              </div>
              
              <p className="text-secondary leading-relaxed max-w-md">
                Create beautiful mathematical animations with AI. 
                Transform complex concepts into engaging visual content 
                that students and educators love.
              </p>

              {/* Social links */}
              <div className="flex items-center gap-3 pt-2">
                {socialLinks.map((link) => (
                  <a
                    key={link.name}
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="
                      w-10 h-10 rounded-xl bg-surface-secondary border border-subtle
                      flex items-center justify-center text-muted hover:text-primary
                      hover:border-emphasis transition-all duration-200 interactive
                      focus-ring
                    "
                    aria-label={link.name}
                  >
                    {link.icon}
                  </a>
                ))}
              </div>
            </div>

            {/* Links sections */}
            <div className="lg:col-span-8">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-8">
                {/* Product */}
                <div className="space-y-4">
                  <h3 className="text-sm font-semibold text-primary">Product</h3>
                  <ul className="space-y-3">
                    {footerLinks.product.map((link) => (
                      <li key={link.name}>
                        <Link
                          to={link.href}
                          className="text-sm text-secondary hover:text-primary transition-colors duration-200 focus-ring rounded-md px-1 py-0.5"
                        >
                          {link.name}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Company */}
                <div className="space-y-4">
                  <h3 className="text-sm font-semibold text-primary">Company</h3>
                  <ul className="space-y-3">
                    {footerLinks.company.map((link) => (
                      <li key={link.name}>
                        <a
                          href={link.href}
                          className="text-sm text-secondary hover:text-primary transition-colors duration-200 focus-ring rounded-md px-1 py-0.5"
                        >
                          {link.name}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Legal */}
                <div className="space-y-4">
                  <h3 className="text-sm font-semibold text-primary">Legal</h3>
                  <ul className="space-y-3">
                    {footerLinks.legal.map((link) => (
                      <li key={link.name}>
                        <a
                          href={link.href}
                          className="text-sm text-secondary hover:text-primary transition-colors duration-200 focus-ring rounded-md px-1 py-0.5"
                        >
                          {link.name}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom section */}
        <div className="py-6 border-t border-subtle">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-sm text-muted">
              <span>&copy; {currentYear} Animathic. All rights reserved.</span>
            </div>
            
            <div className="flex items-center gap-2 text-sm text-muted">
              <span>Made with</span>
              <Heart className="w-4 h-4 text-red-400 fill-current" />
              <span>for educators worldwide</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}