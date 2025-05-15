import { useState, useEffect } from "react";

export default function HowItWorksPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const steps = [
    {
      title: "Input Your Prompt",
      description:
        "Describe the mathematical concept or visualization you want to create in natural language.",
    },
    {
      title: "AI Processing",
      description:
        "Our AI analyzes your prompt and converts it into Manim code - the same animation system used by 3Blue1Brown.",
    },
    {
      title: "Video Rendering",
      description:
        "The Manim code is executed to generate a high-quality MP4 video with smooth animations.",
    },
    {
      title: "Download & Share",
      description:
        "Get the final video. Perfect for presentations, teaching, or social media.",
    },
  ];

  return (
    <main className="flex flex-col items-center min-h-[calc(100vh-4rem)]">
      <div className="container max-w-4xl mx-auto py-12 px-4 sm:py-16 sm:px-6 lg:px-8">
        <div className="text-center space-y-6 mb-12">
          <h1
            className={`text-4xl font-bold tracking-tight sm:text-5xl transition-all duration-700 ${
              mounted ? "opacity-100 transform-none" : "opacity-0 translate-y-4"
            }`}
          >
            How It Works
          </h1>
          <p
            className={`mt-6 text-lg text-muted-foreground max-w-2xl mx-auto transition-all duration-700 delay-100 ${
              mounted ? "opacity-100 transform-none" : "opacity-0 translate-y-4"
            }`}
          >
            Animathic transforms your text descriptions into beautiful
            mathematical animations using advanced AI and the powerful Manim
            engine.
          </p>
        </div>

        <div className="mt-16 space-y-16">
          {steps.map((step, index) => (
            <div
              key={index}
              className={`flex flex-col md:flex-row gap-8 transition-all duration-700 ${
                mounted
                  ? "opacity-100 transform-none"
                  : "opacity-0 translate-y-4"
              }`}
              style={{ transitionDelay: `${(index + 2) * 100}ms` }}
            >
              <div className="flex-shrink-0 flex items-center justify-center">
                <div className="h-12 w-12 rounded-full bg-primary/10 text-primary flex items-center justify-center">
                  <span className="font-bold text-lg">{index + 1}</span>
                </div>
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-semibold mb-2">{step.title}</h2>
                <p className="text-muted-foreground">{step.description}</p>
              </div>
            </div>
          ))}
        </div>

        <div
          className={`mt-16 p-6 rounded-lg bg-accent/50 transition-all duration-700 delay-700 ${
            mounted ? "opacity-100 transform-none" : "opacity-0 translate-y-4"
          }`}
        >
          <h3 className="text-xl font-semibold mb-3">Why Manim?</h3>
          <p className="text-muted-foreground">
            Manim is a mathematical animation engine created by Grant Sanderson
            (3Blue1Brown) to explain math with beautiful, programmatic
            animations. By combining AI with Manim, we make this powerful tool
            accessible to everyone - no coding required.
          </p>
        </div>
      </div>
    </main>
  );
}
