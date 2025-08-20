import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Sparkles, Loader2 } from "lucide-react";
import { useUser } from "@clerk/clerk-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface PromptInputProps {
  initialValue?: string;
  onSubmit?: (prompt: string) => void;
  placeholder?: string;
  className?: string;
}

export function PromptInput({
  initialValue = "",
  onSubmit,
  placeholder = "e.g., Create an animation showing how the derivative of x² becomes 2x using the limit definition",
  className = "",
}: PromptInputProps) {
  const [prompt, setPrompt] = useState(initialValue);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const { isSignedIn } = useUser();
  const navigate = useNavigate();

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (isSubmitting) return;
    if (!prompt.trim()) {
      toast.error("Please enter a prompt to get started");
      return;
    }
    setIsSubmitting(true);
    try {
      if (onSubmit) {
        await onSubmit(prompt);
      } else if (isSignedIn) {
        navigate("/generate", { state: { prompt } });
      } else {
        toast.error("Please sign in to generate animations");
      }
    } catch (error) {
      toast.error("Something went wrong. Please try again.");
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const suggestions = [
    "Visualize the unit circle and sine wave",
    "Animate matrix transformation of a square",
    "Show the Pythagorean theorem proof",
    "Graph the quadratic formula step by step",
  ];

  return (
    <div className={`w-full max-w-3xl mx-auto ${className}`}>
      <form onSubmit={handleSubmit} className="relative group">
        <div
          className={`relative surface-primary rounded-2xl border-2 transition-all duration-300 ${
            isFocused
              ? "border-accent-primary shadow-lg glow-subtle"
              : "border-subtle hover:border-emphasis"
          }`}
        >
          <Textarea
            className={`
              min-h-[160px] w-full resize-none border-0 bg-transparent 
              p-6 pr-32 pb-20 text-base placeholder:text-muted focus:ring-0 focus:outline-none
              transition-all duration-300
            `}
            placeholder={placeholder}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            disabled={isSubmitting}
          />
          {/* In-box overlay submit button (all screen sizes) */}
          <div className="absolute bottom-4 right-4 z-10">
            <Button
              type="submit"
              className="btn-primary h-12 px-6 rounded-xl font-medium interactive focus-ring"
            >
              {isSubmitting ? (
                <div className="flex items-center gap-3 text-white">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Creating...</span>
                </div>
              ) : (
                <div className="flex items-center gap-3 text-white">
                  <Sparkles className="h-4 w-4" />
                  <span>Generate</span>
                  <ArrowRight className="h-4 w-4" />
                </div>
              )}
            </Button>
          </div>
        </div>
      </form>

      {/* Suggestion chips - show when focused and empty */}
      {isFocused && !prompt.trim() && (
        <div className="mt-4 space-y-3 animate-slide-up">
          <p className="text-sm text-muted font-medium">Try these examples:</p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                type="button"
                onClick={() => setPrompt(suggestion)}
                className="
                  px-4 py-2 text-sm rounded-xl
                  surface-secondary border border-subtle
                  text-secondary hover:text-primary
                  hover:border-emphasis
                  transition-all duration-200 interactive
                  focus-ring
                "
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Character count */}
      {prompt.length > 0 && (
        <div className="mt-2 text-right">
          <span
            className={`text-xs ${
              prompt.length > 500 ? "text-red-400" : "text-muted"
            }`}
          >
            {prompt.length}/500
          </span>
        </div>
      )}

      {/* Tips */}
      <div className="mt-6 space-y-2">
        <p className="text-xs text-muted text-center">
          💡 <strong>Tip:</strong> Be specific about what you want to visualize.
          Include mathematical concepts, visual elements, and any step-by-step
          requirements.
        </p>
      </div>
    </div>
  );
}
