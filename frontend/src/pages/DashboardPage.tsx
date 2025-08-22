import React, { useState, useEffect } from "react";
import { useUser } from "@clerk/clerk-react";
import { useNavigate, Link } from "react-router-dom";
import { Loader2, Plus, Video, Sparkles } from "lucide-react";
import VideoGallery from "../components/VideoGallery";
import { Button } from "@/components/ui/button";

const DashboardPage = () => {
  const { isLoaded: isUserLoaded, isSignedIn, user } = useUser();
  const navigate = useNavigate();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Handle authentication state changes
  React.useEffect(() => {
    if (isUserLoaded && !isSignedIn) {
      navigate("/");
    }
  }, [isUserLoaded, isSignedIn, navigate]);

  if (!isUserLoaded) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-accent-primary mx-auto" />
          <p className="text-secondary">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (!isSignedIn) {
    return null; // Will be redirected by the useEffect
  }

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Header */}
      <div className="border-b border-subtle bg-surface-primary/50">
        <div className="container-narrow py-8">
          <div
            className={`transition-all duration-700 ${
              mounted ? "animate-slide-up" : "opacity-0"
            }`}
          >
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold text-primary">
                  Welcome back{user?.firstName && `, ${user.firstName}`}!
                </h1>
                <p className="text-secondary">
                  Manage your mathematical animations and create new ones.
                </p>
              </div>

              <Button
                asChild
                className="btn-primary inline-flex items-center gap-2 interactive"
              >
                <Link to="/generate">
                  <Plus className="w-4 h-4" />
                  <span>New Animation</span>
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="container-narrow py-8">
        <div
          className={`transition-all duration-700 animate-delay-200 ${
            mounted ? "animate-fade-in" : "opacity-0"
          }`}
        >
          {/* Videos section */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-primary">
                Your Animations
              </h2>
            </div>

            <VideoGallery />
          </div>
        </div>
      </div>

      {/* Floating action button (always visible) */}
      <div className="fixed bottom-6 right-6 z-40">
        <Button
          asChild
          className="btn-primary rounded-full h-12 w-12 p-0 shadow-lg interactive focus-ring"
        >
          <Link to="/generate" aria-label="Create new animation">
            <Plus className="h-6 w-6" />
          </Link>
        </Button>
      </div>
    </div>
  );
};

export default DashboardPage;
