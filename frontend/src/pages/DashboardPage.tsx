import React from "react";
import { useUser } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";
import { Loader2 } from "lucide-react";
import VideoGallery from "../components/VideoGallery";

const DashboardPage = () => {
  const { isLoaded: isUserLoaded, isSignedIn } = useUser();
  const navigate = useNavigate();

  // Handle authentication state changes
  React.useEffect(() => {
    if (isUserLoaded && !isSignedIn) {
      navigate("/");
    }
  }, [isUserLoaded, isSignedIn, navigate]);

  if (!isUserLoaded) {
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
