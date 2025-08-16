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
          <div className={`transition-all duration-700 ${mounted ? "animate-slide-up" : "opacity-0"}`}>
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
        <div className={`transition-all duration-700 animate-delay-200 ${mounted ? "animate-fade-in" : "opacity-0"}`}>
          {/* Stats cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="surface-primary rounded-2xl p-6 border border-subtle">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-xl bg-accent-primary/10 flex items-center justify-center">
                  <Video className="w-5 h-5 text-accent-primary" />
                </div>
                <div>
                  <p className="text-sm text-muted">Total Animations</p>
                  <p className="text-2xl font-bold text-primary">0</p>
                </div>
              </div>
            </div>
            
            <div className="surface-primary rounded-2xl p-6 border border-subtle">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-xl bg-green-500/10 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-green-400" />
                </div>
                <div>
                  <p className="text-sm text-muted">This Month</p>
                  <p className="text-2xl font-bold text-primary">0</p>
                </div>
              </div>
            </div>
            
            <div className="surface-primary rounded-2xl p-6 border border-subtle">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center">
                  <Video className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <p className="text-sm text-muted">Total Views</p>
                  <p className="text-2xl font-bold text-primary">0</p>
                </div>
              </div>
            </div>
          </div>

          {/* Videos section */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-primary">Your Animations</h2>
            </div>
            
            <VideoGallery />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;