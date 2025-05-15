import React, { useState, useEffect } from "react";
import { useUser } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";
import VideoGallery from "../components/VideoGallery";
import { Button } from "../components/ui/button";
import { RefreshCw } from "lucide-react";
import { PromptInput } from "../components/PromptInput";

const DashboardPage = () => {
  const { user, isLoaded, isSignedIn } = useUser();
  const navigate = useNavigate();
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setLastRefresh(new Date());
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  // Handle authentication state changes
  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      navigate("/sign-in", { replace: true });
    }
  }, [isLoaded, isSignedIn, navigate]);

  const handleGenerate = (promptText: string) => {
    if (!isSignedIn) {
      navigate("/sign-in", { replace: true });
      return;
    }
    navigate("/generate", { state: { prompt: promptText } });
  };

  // Show loading state while Clerk is initializing
  if (!isLoaded) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-2 border-t-primary border-r-transparent border-b-primary border-l-transparent"></div>
      </div>
    );
  }

  // Don't render anything if not signed in (navigation will handle redirect)
  if (!isSignedIn) {
    return null;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">
            Welcome, {user?.firstName || "User"}!
          </h1>
          <p className="text-muted-foreground">
            Manage your animations and create new ones
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => setLastRefresh(new Date())}
          className="flex items-center gap-2"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
      </div>

      <div className="space-y-8">
        <section className="bg-card border rounded-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Create New Animation</h2>
          <PromptInput onSubmit={handleGenerate} />
        </section>

        <section>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold">Your Animations</h2>
            <p className="text-sm text-muted-foreground">
              Last updated: {lastRefresh.toLocaleTimeString()}
            </p>
          </div>
          <VideoGallery key={lastRefresh.toISOString()} />
        </section>
      </div>
    </div>
  );
};

export default DashboardPage;
