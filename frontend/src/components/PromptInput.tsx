
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { useUser } from "@clerk/clerk-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface PromptInputProps {
  initialValue?: string;
  onSubmit?: (prompt: string) => void;
}

export function PromptInput({ initialValue = "", onSubmit }: PromptInputProps) {
  const [prompt, setPrompt] = useState(initialValue);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { isSignedIn } = useUser();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      toast.error("Please enter a prompt");
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      if (onSubmit) {
        onSubmit(prompt);
      } else if (isSignedIn) {
        navigate("/generate", { state: { prompt } });
      } else {
        // Auth will be handled by Clerk in App.tsx with protected routes
        toast.error("Please sign in to generate animations");
      }
    } catch (error) {
      toast.error("Something went wrong. Please try again.");
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="relative">
        <Textarea
          className="min-h-[120px] p-4 text-base resize-none rounded-xl transition-all focus:ring-2 focus:ring-primary/30 focus:border-primary"
          placeholder="e.g., Animate a sine wave forming from a unit circle"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          disabled={isSubmitting}
        />
        <Button
          type="submit"
          className="absolute bottom-3 right-3 rounded-lg transition-all animate-fade-in hover:scale-105"
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <div className="flex items-center gap-2">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
              <span>Generating...</span>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <span>Generate</span>
              <ArrowRight className="h-4 w-4" />
            </div>
          )}
        </Button>
      </div>
    </form>
  );
}
