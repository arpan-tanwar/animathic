import { useState, useEffect } from "react";
import { MessageSquare, Brain, Video, Download, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export default function HowItWorksPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const steps = [
    {
      icon: <MessageSquare className="w-6 h-6" />,
      title: "Describe Your Idea",
      description: "Simply type what mathematical concept you want to visualize. Be as specific or creative as you like - our AI understands natural language.",
      example: "Animate a sine wave emerging from a rotating unit circle",
      color: "from-blue-500 to-cyan-500"
    },
    {
      icon: <Brain className="w-6 h-6" />,
      title: "AI Processing",
      description: "Our advanced AI analyzes your prompt and converts it into Manim code - the same animation system used by 3Blue1Brown for world-class mathematical content.",
      example: "Code generation, mathematical parsing, visual planning",
      color: "from-purple-500 to-pink-500"
    },
    {
      icon: <Video className="w-6 h-6" />,
      title: "Video Rendering",
      description: "The generated Manim script is executed in our cloud infrastructure to create a high-quality MP4 video with smooth, professional animations.",
      example: "HD rendering, optimized output, multiple formats",
      color: "from-green-500 to-emerald-500"
    },
    {
      icon: <Download className="w-6 h-6" />,
      title: "Download & Share",
      description: "Get your finished animation ready for presentations, teaching materials, or social media. Perfect for engaging your audience with complex concepts.",
      example: "MP4 download, embed codes, sharing options",
      color: "from-orange-500 to-red-500"
    }
  ];

  const features = [
    {
      title: "Natural Language Processing",
      description: "No coding required - just describe what you want to see"
    },
    {
      title: "Professional Quality",
      description: "Powered by Manim, the industry standard for mathematical animations"
    },
    {
      title: "Lightning Fast",
      description: "Generate complex animations in minutes, not hours"
    },
    {
      title: "Educator Focused",
      description: "Built specifically for teaching and learning scenarios"
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="pt-20 pb-16 lg:pt-28 lg:pb-20 relative">
        <div className="absolute inset-0 gradient-mesh opacity-30" />
        
        <div className="container-narrow relative">
          <div className="text-center space-y-6 max-w-3xl mx-auto">
            <h1 className={`text-4xl lg:text-5xl font-bold tracking-tight transition-all duration-700 ${mounted ? "animate-slide-up" : "opacity-0"}`}>
              How <span className="text-gradient-primary">Animathic</span> Works
            </h1>
            
            <p className={`text-lg text-secondary leading-relaxed transition-all duration-700 animate-delay-200 ${mounted ? "animate-slide-up" : "opacity-0"}`}>
              Transform your mathematical ideas into stunning animations in four simple steps. 
              No coding experience required - just describe what you want to visualize.
            </p>
          </div>
        </div>
      </section>

      {/* Steps Section */}
      <section className="py-16 lg:py-24">
        <div className="container-narrow">
          <div className="space-y-16">
            {steps.map((step, index) => (
              <div
                key={index}
                className={`transition-all duration-700 ${mounted ? "animate-fade-in" : "opacity-0"}`}
                style={{ animationDelay: `${(index + 1) * 200}ms` }}
              >
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
                  {/* Content */}
                  <div className={`lg:col-span-6 space-y-6 ${index % 2 === 1 ? "lg:order-2" : ""}`}>
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-2xl bg-gradient-to-r ${step.color} flex items-center justify-center text-white shadow-lg`}>
                        {step.icon}
                      </div>
                      <div className="text-sm font-medium text-muted">
                        Step {index + 1}
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <h2 className="text-2xl lg:text-3xl font-bold text-primary">
                        {step.title}
                      </h2>
                      
                      <p className="text-lg text-secondary leading-relaxed">
                        {step.description}
                      </p>
                      
                      <div className="surface-primary rounded-xl p-4 border border-subtle">
                        <p className="text-sm text-muted mb-1">Example:</p>
                        <p className="text-sm text-primary font-medium">{step.example}</p>
                      </div>
                    </div>
                  </div>

                  {/* Visual */}
                  <div className={`lg:col-span-6 ${index % 2 === 1 ? "lg:order-1" : ""}`}>
                    <div className="aspect-video rounded-2xl bg-gradient-to-br from-surface-secondary to-surface-tertiary border border-emphasis p-8 flex items-center justify-center">
                      <div className="text-center space-y-4">
                        <div className={`w-16 h-16 rounded-full bg-gradient-to-r ${step.color} flex items-center justify-center mx-auto text-white shadow-xl`}>
                          {step.icon}
                        </div>
                        <div className="space-y-2">
                          <p className="text-lg font-semibold text-primary">{step.title}</p>
                          <p className="text-sm text-secondary">Interactive demo coming soon</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Connector line (except for last step) */}
                {index < steps.length - 1 && (
                  <div className="flex justify-center py-8">
                    <div className="w-px h-12 bg-gradient-to-b from-border-emphasis to-transparent"></div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 lg:py-24 bg-surface-primary/30">
        <div className="container-narrow">
          <div className="text-center space-y-12">
            <div className="space-y-4">
              <h2 className="text-3xl lg:text-4xl font-bold text-primary">
                Why Choose Animathic?
              </h2>
              <p className="text-lg text-secondary max-w-2xl mx-auto">
                Built from the ground up to make mathematical visualization accessible to everyone.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className={`surface-primary rounded-2xl p-6 lg:p-8 space-y-3 interactive transition-all duration-700 ${mounted ? "animate-scale-up" : "opacity-0"}`}
                  style={{ animationDelay: `${(index + 5) * 100}ms` }}
                >
                  <h3 className="text-lg font-semibold text-primary">{feature.title}</h3>
                  <p className="text-secondary">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Manim Explanation */}
      <section className="py-16 lg:py-24">
        <div className="container-narrow">
          <div className="surface-primary rounded-3xl p-8 lg:p-12 space-y-8">
            <div className="text-center space-y-4">
              <h2 className="text-3xl lg:text-4xl font-bold text-primary">
                Powered by Manim
              </h2>
              <p className="text-lg text-secondary max-w-3xl mx-auto leading-relaxed">
                Manim is the mathematical animation engine created by Grant Sanderson (3Blue1Brown) 
                to produce the stunning visualizations in his educational videos. By combining AI with Manim, 
                we make this powerful tool accessible to everyone.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
              <div className="space-y-3">
                <div className="text-2xl font-bold text-gradient-primary">50M+</div>
                <div className="text-sm text-secondary">Views on 3Blue1Brown videos</div>
              </div>
              <div className="space-y-3">
                <div className="text-2xl font-bold text-gradient-primary">100K+</div>
                <div className="text-sm text-secondary">GitHub stars</div>
              </div>
              <div className="space-y-3">
                <div className="text-2xl font-bold text-gradient-primary">Industry</div>
                <div className="text-sm text-secondary">Standard for math visualization</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 lg:py-24">
        <div className="container-narrow">
          <div className="text-center space-y-8 max-w-3xl mx-auto">
            <div className="space-y-4">
              <h2 className="text-3xl lg:text-4xl font-bold text-primary">
                Ready to Get Started?
              </h2>
              <p className="text-lg text-secondary">
                Join thousands of educators creating engaging mathematical content with AI.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/generate"
                className="btn-primary inline-flex items-center gap-2 interactive"
              >
                <span>Start Creating</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              
              <Link
                to="/examples"
                className="btn-ghost inline-flex items-center gap-2"
              >
                <span>View Examples</span>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}