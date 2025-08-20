import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useUser } from "@clerk/clerk-react";
import axios from "axios";
import { toast } from "react-hot-toast";
import { Button } from "../components/ui/button";
import {
  ArrowLeft,
  Loader2,
  Check,
  Download,
  Play,
  Sparkles,
  Clock,
  AlertCircle,
} from "lucide-react";
import { API_BASE_URL } from "../config";
import { PromptInput } from "@/components/PromptInput";

interface GenerateResponse {
  id: string;
  video_url: string;
  metadata: {
    id: string;
    user_id: string;
    file_path: string;
    prompt: string;
    created_at: string;
    status: string;
  };
}

interface StatusResponse {
  status: string;
  video_url?: string;
  error?: string;
}

const GeneratePage = () => {
  const { user } = useUser();
  const location = useLocation();
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState<string>("");
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [isComplete, setIsComplete] = useState<boolean>(false);
  const [hasError, setHasError] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [videoUrl, setVideoUrl] = useState<string>("");
  const [jobId, setJobId] = useState<string | null>(null);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(
    null
  );
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [elapsedTime, setElapsedTime] = useState<string>("0:00");
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [showPromptInput, setShowPromptInput] = useState<boolean>(true);

  const steps = [
    {
      title: "Analyzing Prompt",
      description: "Understanding your mathematical concept and requirements",
      icon: <Sparkles className="w-5 h-5" />,
    },
    {
      title: "Generating Code",
      description: "Creating optimized Manim script for your animation",
      icon: <Check className="w-5 h-5" />,
    },
    {
      title: "Rendering Video",
      description: "Processing animation with high-quality output",
      icon: <Play className="w-5 h-5" />,
    },
    {
      title: "Finalizing",
      description: "Preparing your animation for download",
      icon: <Download className="w-5 h-5" />,
    },
  ];

  useEffect(() => {
    if (!user) {
      toast.error("Please sign in to generate videos");
      navigate("/");
      return;
    }

    // Check if prompt was passed via location state
    const promptFromState = location.state?.prompt;
    if (promptFromState) {
      setPrompt(promptFromState);
      setShowPromptInput(false);
      setStartTime(new Date());
      startGeneration(promptFromState);
    }
    // If no prompt, show the prompt input form

    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [location.state, navigate, user]);

  // Update elapsed time
  useEffect(() => {
    if (!startTime || isComplete || hasError) return;

    const timer = setInterval(() => {
      const elapsed = Date.now() - startTime.getTime();
      const minutes = Math.floor(elapsed / 60000);
      const seconds = Math.floor((elapsed % 60000) / 1000);
      setElapsedTime(`${minutes}:${seconds.toString().padStart(2, "0")}`);
    }, 1000);

    return () => clearInterval(timer);
  }, [startTime, isComplete, hasError]);

  const handlePromptSubmit = async (promptText: string) => {
    if (!promptText.trim()) {
      toast.error("Please enter a prompt");
      return;
    }

    setPrompt(promptText);
    setShowPromptInput(false);
    setStartTime(new Date());
    await startGeneration(promptText);
  };

  const startGeneration = async (promptText: string) => {
    if (!user) return;

    try {
      setHasError(false);
      setCurrentStep(0);
      setIsGenerating(true);

      // Step 1: Send the prompt to generate the video
      const response = await axios.post<GenerateResponse>(
        `${API_BASE_URL}/api/generate`,
        {
          prompt: promptText,
          user_id: user.id,
        },
        {
          headers: {
            "user-id": user.id,
          },
        }
      );

      setJobId(response.data.id);
      setCurrentStep(1);

      // Start polling for status
      const interval = setInterval(async () => {
        try {
          const statusResponse = await axios.get<StatusResponse>(
            `${API_BASE_URL}/api/status/${response.data.id}`,
            {
              headers: {
                "user-id": user.id,
              },
            }
          );

          if (statusResponse.data.status === "completed") {
            clearInterval(interval);
            setCurrentStep(3);
            setIsComplete(true);
            setIsGenerating(false);
            setVideoUrl(statusResponse.data.video_url || "");
            toast.success("Your animation is ready!");
          } else if (statusResponse.data.status === "failed") {
            clearInterval(interval);
            setHasError(true);
            setIsGenerating(false);
            setErrorMessage(statusResponse.data.error || "Generation failed");
            toast.error("Animation generation failed");
          } else {
            // Update step based on status
            if (currentStep < 2) {
              setCurrentStep((prev) => Math.min(prev + 1, 2));
            }
          }
        } catch (error) {
          console.error("Error checking status:", error);
          clearInterval(interval);
          setHasError(true);
          setIsGenerating(false);
          setErrorMessage("Connection error while checking status");
          toast.error("Error checking generation status");
        }
      }, 2000);

      setPollingInterval(interval);
    } catch (error) {
      console.error("Error starting generation:", error);
      setHasError(true);
      setIsGenerating(false);
      setErrorMessage("Failed to start generation");
      toast.error("Failed to start generation");
    }
  };

  const handleDownload = async () => {
    if (!videoUrl) {
      toast.error("No video available to download");
      return;
    }

    try {
      const loadingToast = toast.loading("Preparing download...");

      const response = await axios.get(videoUrl, {
        responseType: "blob",
      });

      const blob = new Blob([response.data as BlobPart], {
        type: "video/mp4",
      });

      const url = window.URL.createObjectURL(blob);
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      const filename = `${prompt
        .slice(0, 30)
        .replace(/[^a-z0-9]/gi, "_")
        .toLowerCase()}_${timestamp}.mp4`;

      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();

      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.dismiss(loadingToast);
      toast.success("Download started!");
    } catch (error) {
      console.error("Error downloading video:", error);
      toast.error("Failed to download video");
    }
  };

  const handleRetry = () => {
    setHasError(false);
    setErrorMessage("");
    setIsComplete(false);
    setCurrentStep(0);
    setStartTime(new Date());
    startGeneration(prompt);
  };

  const handleNewAnimation = () => {
    setPrompt("");
    setShowPromptInput(true);
    setIsComplete(false);
    setHasError(false);
    setIsGenerating(false);
    setCurrentStep(0);
    setJobId(null);
    setVideoUrl("");
  };

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Header */}
      <div className="border-b border-subtle bg-surface-primary/50">
        <div className="container-narrow py-6">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={() => navigate("/dashboard")}
              className="mb-4 interactive focus-ring"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
            {showPromptInput && (
              <Button
                onClick={() => {
                  const el = document.querySelector<HTMLButtonElement>(
                    'form button[type="submit"]'
                  );
                  el?.click();
                }}
                className="btn-primary interactive"
              >
                <Sparkles className="h-4 w-4 mr-2" /> Generate
              </Button>
            )}
          </div>

          <div className="space-y-2">
            <h1 className="text-3xl font-bold text-primary">
              {showPromptInput
                ? "Create New Animation"
                : isComplete
                ? "Animation Complete!"
                : hasError
                ? "Generation Failed"
                : "Creating Your Animation"}
            </h1>

            {!showPromptInput && (
              <div className="flex items-center gap-4 text-sm text-secondary">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  <span>Elapsed: {elapsedTime}</span>
                </div>
                {jobId && (
                  <div className="flex items-center gap-2">
                    <span>Job ID: {jobId.slice(0, 8)}...</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="container-narrow py-8">
        {showPromptInput ? (
          /* Prompt Input Form */
          <div className="space-y-8 max-w-4xl mx-auto">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-gradient-primary flex items-center justify-center mx-auto">
                <Sparkles className="w-8 h-8 text-white" />
              </div>

              <div className="space-y-2">
                <h2 className="text-2xl font-bold text-primary">
                  What would you like to create?
                </h2>
                <p className="text-secondary max-w-2xl mx-auto">
                  Describe your mathematical concept and we'll transform it into
                  a beautiful animation using AI and Manim.
                </p>
              </div>
            </div>

            <PromptInput
              onSubmit={handlePromptSubmit}
              placeholder="e.g., Create an animation showing how the derivative of x² becomes 2x using the limit definition"
            />

            <div className="text-center">
              <p className="text-sm text-muted">
                💡 <strong>Tip:</strong> Be specific about mathematical
                concepts, visual elements, and any step-by-step requirements for
                the best results.
              </p>
            </div>
          </div>
        ) : (
          <>
            {/* Prompt display */}
            <div className="surface-primary rounded-2xl p-6 border border-subtle mb-8">
              <h2 className="text-sm font-medium text-muted mb-2">
                Your Prompt:
              </h2>
              <p className="text-primary leading-relaxed">{prompt}</p>
            </div>

            {hasError ? (
              /* Error State */
              <div className="text-center space-y-6 max-w-2xl mx-auto">
                <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mx-auto">
                  <AlertCircle className="w-8 h-8 text-red-400" />
                </div>

                <div className="space-y-3">
                  <h2 className="text-2xl font-bold text-primary">
                    Generation Failed
                  </h2>
                  <p className="text-secondary">
                    {errorMessage ||
                      "Something went wrong while creating your animation."}
                  </p>
                </div>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                  <Button
                    onClick={handleRetry}
                    className="btn-primary interactive"
                  >
                    Try Again
                  </Button>

                  <Button
                    variant="outline"
                    onClick={handleNewAnimation}
                    className="interactive focus-ring"
                  >
                    New Animation
                  </Button>

                  <Button
                    variant="outline"
                    onClick={() => navigate("/dashboard")}
                    className="interactive focus-ring"
                  >
                    Back to Dashboard
                  </Button>
                </div>
              </div>
            ) : isComplete ? (
              /* Success State */
              <div className="space-y-8 max-w-4xl mx-auto">
                <div className="text-center space-y-4">
                  <div className="w-16 h-16 rounded-full bg-green-500/10 flex items-center justify-center mx-auto">
                    <Check className="w-8 h-8 text-green-400" />
                  </div>

                  <div className="space-y-2">
                    <h2 className="text-2xl font-bold text-primary">
                      Animation Ready!
                    </h2>
                    <p className="text-secondary">
                      Your mathematical animation has been generated
                      successfully.
                    </p>
                  </div>
                </div>

                {/* Video player */}
                <div className="surface-primary rounded-2xl p-6 border border-subtle">
                  <div className="aspect-video bg-surface-tertiary rounded-xl flex items-center justify-center overflow-hidden">
                    <video
                      src={videoUrl}
                      controls
                      className="w-full h-full object-contain"
                      onError={(e) => {
                        console.error("Error loading video:", e);
                        toast.error("Error loading video. Please try again.");
                      }}
                    />
                  </div>

                  <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-4">
                    <Button
                      onClick={handleDownload}
                      className="btn-primary interactive"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download MP4
                    </Button>

                    <Button
                      variant="outline"
                      onClick={handleNewAnimation}
                      className="interactive focus-ring"
                    >
                      New Animation
                    </Button>

                    <Button
                      variant="outline"
                      onClick={() => navigate("/dashboard")}
                      className="interactive focus-ring"
                    >
                      Back to Dashboard
                    </Button>
                  </div>
                </div>
              </div>
            ) : (
              /* Loading State */
              <div className="space-y-8 max-w-2xl mx-auto">
                <div className="surface-primary rounded-2xl p-8 border border-subtle">
                  <div className="space-y-6">
                    {steps.map((step, index) => (
                      <div
                        key={index}
                        className={`flex items-start gap-4 transition-all duration-300 ${
                          index < currentStep
                            ? "opacity-100"
                            : index === currentStep
                            ? "opacity-100"
                            : "opacity-50"
                        }`}
                      >
                        <div
                          className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 ${
                            index < currentStep
                              ? "bg-green-500/20 text-green-400"
                              : index === currentStep
                              ? "bg-accent-primary/20 text-accent-primary"
                              : "bg-surface-secondary text-muted"
                          }`}
                        >
                          {index < currentStep ? (
                            <Check className="h-5 w-5" />
                          ) : index === currentStep ? (
                            <Loader2 className="h-5 w-5 animate-spin" />
                          ) : (
                            <span className="text-sm font-semibold">
                              {index + 1}
                            </span>
                          )}
                        </div>

                        <div className="flex-1 space-y-1">
                          <h3
                            className={`font-medium ${
                              index <= currentStep
                                ? "text-primary"
                                : "text-muted"
                            }`}
                          >
                            {step.title}
                          </h3>
                          <p
                            className={`text-sm ${
                              index <= currentStep
                                ? "text-secondary"
                                : "text-muted"
                            }`}
                          >
                            {step.description}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Progress indicator */}
                <div className="text-center space-y-4">
                  <div className="w-full bg-surface-secondary rounded-full h-2 overflow-hidden">
                    <div
                      className="h-full bg-gradient-primary transition-all duration-500 ease-out"
                      style={{
                        width: `${((currentStep + 1) / steps.length) * 100}%`,
                      }}
                    />
                  </div>

                  <p className="text-sm text-secondary">
                    Please wait while we generate your animation. This may take
                    2-5 minutes.
                  </p>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default GeneratePage;
