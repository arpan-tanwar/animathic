import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useUser } from "@clerk/clerk-react";
import axios from "axios";
import { toast } from "react-hot-toast";
import { Button } from "../components/ui/button";
import { ArrowLeft, Loader2, Check, Download } from "lucide-react";

const API_BASE_URL = "http://localhost:8000";

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
  const [videoUrl, setVideoUrl] = useState<string>("");
  const [jobId, setJobId] = useState<string | null>(null);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(
    null
  );

  const steps = [
    "Parsing your prompt...",
    "Generating Manim script...",
    "Rendering animation...",
    "Finalizing video...",
  ];

  useEffect(() => {
    if (!user) {
      toast.error("Please sign in to generate videos");
      navigate("/sign-in");
      return;
    }

    const promptFromState = location.state?.prompt;
    if (!promptFromState) {
      toast.error("No prompt provided");
      navigate("/dashboard");
      return;
    }

    setPrompt(promptFromState);
    startGeneration(promptFromState);

    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [location.state, navigate, user]);

  const startGeneration = async (promptText: string) => {
    if (!user) return;

    try {
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
            setVideoUrl(statusResponse.data.video_url || "");
            toast.success("Your animation is ready!");
          } else if (statusResponse.data.status === "failed") {
            clearInterval(interval);
            toast.error(
              statusResponse.data.error || "Failed to generate animation"
            );
            navigate("/dashboard");
          } else {
            // Update step based on status
            if (currentStep < 2) {
              setCurrentStep((prev) => prev + 1);
            }
          }
        } catch (error) {
          console.error("Error checking status:", error);
          clearInterval(interval);
          toast.error("Error checking generation status");
          navigate("/dashboard");
        }
      }, 2000);

      setPollingInterval(interval);
    } catch (error) {
      console.error("Error starting generation:", error);
      toast.error("Failed to start generation");
      navigate("/dashboard");
    }
  };

  const handleDownload = async () => {
    if (videoUrl) {
      try {
        // Show loading toast
        const loadingToast = toast.loading("Preparing download...");

        // Fetch the video file
        const response = await axios.get(videoUrl, {
          responseType: "blob",
        });

        // Create blob from the response
        const blob = new Blob([response.data as BlobPart], {
          type: "video/mp4",
        });

        // Create object URL
        const url = window.URL.createObjectURL(blob);

        // Create filename from the prompt (first 30 chars) and timestamp
        const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
        const filename = `${prompt
          .slice(0, 30)
          .replace(/[^a-z0-9]/gi, "_")
          .toLowerCase()}_${timestamp}.mp4`;

        // Create and click download link
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();

        // Cleanup
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        // Update toast
        toast.dismiss(loadingToast);
        toast.success("Download started!");
      } catch (error) {
        console.error("Error downloading video:", error);
        toast.error("Failed to download video");
      }
    } else {
      toast.error("No video available to download");
    }
  };

  return (
    <main className="container py-8 px-4 max-w-4xl mx-auto">
      <Button
        variant="ghost"
        onClick={() => navigate("/dashboard")}
        className="mb-8"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to Dashboard
      </Button>

      <h1 className="text-3xl font-bold text-center mb-6">
        {isComplete
          ? "Your Animation is Ready"
          : "Your Animation is Generating..."}
      </h1>

      {!isComplete ? (
        <div className="space-y-8">
          <div className="bg-card border rounded-lg p-6">
            <div className="space-y-4">
              {steps.map((step, index) => (
                <div
                  key={index}
                  className={`flex items-center gap-4 ${
                    index < currentStep
                      ? "text-primary"
                      : index === currentStep
                      ? "text-foreground"
                      : "text-muted-foreground"
                  }`}
                >
                  <div
                    className={`h-8 w-8 rounded-full flex items-center justify-center ${
                      index < currentStep
                        ? "bg-primary text-primary-foreground"
                        : index === currentStep
                        ? "bg-primary/20 text-primary"
                        : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {index < currentStep ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <span>{index + 1}</span>
                    )}
                  </div>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-8">
          <div className="bg-card border rounded-lg p-4 shadow-sm">
            <div className="aspect-video bg-black/20 rounded flex items-center justify-center">
              <video
                src={videoUrl}
                controls
                className="max-h-full rounded"
                onError={(e) => {
                  console.error("Error loading video:", e);
                  toast.error("Error loading video. Please try again.");
                }}
              />
            </div>
            <div className="mt-4 flex flex-wrap gap-3 justify-center">
              <Button onClick={handleDownload} className="gap-2">
                <Download className="h-4 w-4" />
                Download MP4
              </Button>
              <Button variant="outline" onClick={() => navigate("/dashboard")}>
                Back to Dashboard
              </Button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
};

export default GeneratePage;
