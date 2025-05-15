import { useState, useEffect } from "react";
import { PromptInput } from "@/components/PromptInput";

export default function LandingPage() {
  const [mounted, setMounted] = useState(false);

  // Used for entrance animations
  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <main className="flex flex-col items-center justify-center min-h-[calc(90vh-4rem)] px-4">
      <div
        className={`max-w-4xl w-full text-center space-y-6 transition-all duration-700 ${
          mounted ? "opacity-100 transform-none" : "opacity-0 translate-y-4"
        }`}
      >
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight">
          Turn your ideas into
          <span className="text-gradient block mt-1">
            animated math with AI
          </span>
        </h1>

        <p className="text-lg text-muted-foreground max-w-2xl mx-auto mt-4">
          Describe your concept. <br /> Create beautiful math visualizations
          powered by AI.
        </p>

        <div
          className={`mt-8 transition-all duration-700 delay-300 ${
            mounted ? "opacity-100 transform-none" : "opacity-0 translate-y-4"
          }`}
        >
          <PromptInput />
        </div>
      </div>
    </main>
  );
}
