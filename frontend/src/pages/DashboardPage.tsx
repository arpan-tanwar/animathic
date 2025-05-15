import React, { useState, useEffect } from "react";
import { useUser, useAuth } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-hot-toast";
import { Loader2 } from "lucide-react";
import VideoGallery from "../components/VideoGallery";
import { API_BASE_URL } from "../config";

const DashboardPage = () => {
  const { isLoaded: isUserLoaded, isSignedIn } = useUser();
  const { getToken } = useAuth();
  const navigate = useNavigate();
  const [isVerifying, setIsVerifying] = useState(true);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    const verifySession = async () => {
      if (!isUserLoaded) return;

      if (!isSignedIn) {
        navigate("/");
        return;
      }

      try {
        setIsVerifying(true);
        const token = await getToken();

        if (!token) {
          throw new Error("No authentication token available");
        }

        const response = await fetch(`${API_BASE_URL}/api/verify-session`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Session verification failed");
        }

        setRetryCount(0); // Reset retry count on successful verification
      } catch (error) {
        console.error("Error verifying session:", error);
        if (retryCount < 3) {
          // Retry up to 3 times with exponential backoff
          const delay = Math.pow(2, retryCount) * 1000;
          setTimeout(() => {
            setRetryCount((prev) => prev + 1);
            verifySession();
          }, delay);
        } else {
          toast.error("Failed to verify session. Please try signing in again.");
          navigate("/");
        }
      } finally {
        setIsVerifying(false);
      }
    };

    verifySession();
  }, [isUserLoaded, isSignedIn, navigate, retryCount, getToken]);

  if (!isUserLoaded || isVerifying) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isSignedIn) {
    return null; // Will be redirected by the useEffect
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Your Videos</h1>
      <VideoGallery />
    </div>
  );
};

export default DashboardPage;
