import { useState, useEffect } from "react";
import { PromptInput } from "@/components/PromptInput";
import { ArrowRight, Play, Sparkles, Zap, Users, Star } from "lucide-react";
import { Link } from "react-router-dom";

export default function LandingPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const features = [
    {
      icon: <Sparkles className="w-5 h-5" />,
      title: "AI-Powered",
      description: "Advanced AI converts your ideas into beautiful mathematical animations"
    },
    {
      icon: <Zap className="w-5 h-5" />,
      title: "Lightning Fast",
      description: "Generate professional-quality videos in minutes, not hours"
    },
    {
      icon: <Users className="w-5 h-5" />,
      title: "Educator Friendly",
      description: "Perfect for teachers, students, and content creators"
    }
  ];

  const stats = [
    { value: "10K+", label: "Animations Created" },
    { value: "500+", label: "Happy Educators" },
    { value: "99.9%", label: "Uptime" }
  ];

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background gradient mesh */}
      <div className="absolute inset-0 gradient-mesh opacity-40" />
      
      {/* Hero Section */}
      <section className="relative pt-20 pb-16 lg:pt-32 lg:pb-24">
        <div className="container-narrow">
          <div className="text-center space-y-8 max-w-4xl mx-auto">
            {/* Hero badge */}
            <div className={`inline-flex items-center gap-2 surface-primary rounded-full px-4 py-2 text-sm font-medium transition-all duration-700 ${mounted ? "animate-fade-in" : "opacity-0"}`}>
              <Star className="w-4 h-4 text-yellow-400" />
              <span className="text-secondary">Trusted by 500+ educators worldwide</span>
            </div>
            
            {/* Hero headline */}
            <div className="space-y-6">
              <h1 className={`text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight transition-all duration-700 ${mounted ? "animate-slide-up" : "opacity-0"}`}>
                Create stunning{" "}
                <span className="text-gradient-primary">mathematical animations</span>{" "}
                with AI
        </h1>

              <p className={`text-lg sm:text-xl text-secondary max-w-2xl mx-auto leading-relaxed transition-all duration-700 animate-delay-200 ${mounted ? "animate-slide-up" : "opacity-0"}`}>
                Transform complex mathematical concepts into beautiful, engaging animations. 
                No coding required – just describe your idea and watch it come to life.
              </p>
            </div>

            {/* CTA Section */}
            <div className={`space-y-6 transition-all duration-700 animate-delay-300 ${mounted ? "animate-slide-up" : "opacity-0"}`}>
              <PromptInput />
              
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 text-sm text-muted">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-400"></div>
                  <span>Free to try</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                  <span>No credit card required</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-purple-400"></div>
                  <span>Export as MP4</span>
                </div>
              </div>
            </div>

            {/* Demo video placeholder */}
            <div className={`relative mt-12 transition-all duration-700 animate-delay-500 ${mounted ? "animate-scale-up" : "opacity-0"}`}>
              <div className="relative mx-auto max-w-4xl">
                <div className="aspect-video rounded-2xl bg-gradient-to-br from-surface-secondary to-surface-tertiary border border-emphasis p-8 flex items-center justify-center group cursor-pointer hover-lift hover-scale transition-all duration-300">
                  <div className="text-center space-y-4">
                    <div className="w-16 h-16 rounded-full bg-accent-primary/20 flex items-center justify-center mx-auto group-hover:bg-accent-primary/30 hover-glow transition-all duration-300 animate-pulse-glow">
                      <Play className="w-8 h-8 text-accent-primary ml-1 group-hover:scale-110 transition-transform duration-300" />
                    </div>
                    <div>
                      <p className="text-lg font-medium text-primary group-hover:text-accent-primary transition-colors duration-300">Watch Demo</p>
                      <p className="text-sm text-secondary">See Animathic in action</p>
                    </div>
                  </div>
                </div>
                
                {/* Floating elements with enhanced animations */}
                <div className="absolute -top-4 -right-4 w-8 h-8 rounded-full bg-accent-primary/20 animate-float hover-glow"></div>
                <div className="absolute -bottom-4 -left-4 w-6 h-6 rounded-full bg-accent-tertiary/20 animate-float hover-glow" style={{ animationDelay: "1s" }}></div>
                <div className="absolute top-1/2 -left-8 w-4 h-4 rounded-full bg-accent-secondary/15 animate-float" style={{ animationDelay: "2s" }}></div>
                <div className="absolute top-1/4 -right-8 w-5 h-5 rounded-full bg-accent-quaternary/15 animate-float" style={{ animationDelay: "0.5s" }}></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 lg:py-24 relative">
        <div className="container-narrow">
          <div className="text-center space-y-12">
            <div className="space-y-4">
              <h2 className="text-3xl lg:text-4xl font-bold text-primary">
                Why choose Animathic?
              </h2>
              <p className="text-lg text-secondary max-w-2xl mx-auto">
                Built specifically for educators and students who want to create 
                professional mathematical content without the complexity.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className={`surface-primary rounded-2xl p-6 lg:p-8 text-center space-y-4 hover-lift hover-scale transition-all duration-700 ${mounted ? "animate-slide-up" : "opacity-0"}`}
                  style={{ animationDelay: `${(index + 2) * 100}ms` }}
                >
                  <div className="w-12 h-12 rounded-xl bg-accent-primary/10 flex items-center justify-center mx-auto text-accent-primary hover-glow transition-all duration-300">
                    {feature.icon}
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold text-primary">{feature.title}</h3>
                    <p className="text-secondary leading-relaxed">{feature.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 relative">
        <div className="container-narrow">
          <div className="surface-primary rounded-2xl p-8 lg:p-12">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
              {stats.map((stat, index) => (
                <div
                  key={index}
                  className={`space-y-2 transition-all duration-700 ${mounted ? "animate-fade-in" : "opacity-0"}`}
                  style={{ animationDelay: `${(index + 5) * 100}ms` }}
                >
                  <div className="text-3xl lg:text-4xl font-bold text-gradient-primary">
                    {stat.value}
                  </div>
                  <div className="text-secondary">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 lg:py-24 relative">
        <div className="container-narrow">
          <div className="text-center space-y-8 max-w-3xl mx-auto">
            <div className="space-y-4">
              <h2 className="text-3xl lg:text-4xl font-bold text-primary">
                Ready to bring your math to life?
              </h2>
              <p className="text-lg text-secondary">
                Join thousands of educators creating engaging mathematical content with AI.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/examples"
                className="btn-primary inline-flex items-center gap-2 interactive"
              >
                <span>View Examples</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              
              <Link
                to="/how-it-works"
                className="btn-ghost inline-flex items-center gap-2"
              >
                <span>How it works</span>
              </Link>
            </div>
          </div>
        </div>
      </section>
      </div>
  );
}