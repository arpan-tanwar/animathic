import React, { useState, useEffect, useCallback } from "react";
import { useUser, useAuth } from "@clerk/clerk-react";
import axios from "axios";
import { toast } from "react-hot-toast";
import { Button } from "./ui/button";
import { Trash2, Loader2, Download, RefreshCw } from "lucide-react";
import { API_BASE_URL } from "../config";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "./ui/alert-dialog";

interface Video {
  id: string;
  video_url: string;
  prompt: string;
  created_at: string;
  status: string;
}

const VideoGallery = () => {
  const { user, isLoaded: isUserLoaded, isSignedIn } = useUser();
  const { getToken } = useAuth();
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [videoErrors, setVideoErrors] = useState<Record<string, boolean>>({});
  const [retryCount, setRetryCount] = useState(0);

  const fetchVideos = useCallback(async () => {
    if (!user || !isUserLoaded || !isSignedIn) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const token = await getToken();

      if (!token) {
        throw new Error("No authentication token available");
      }

      console.log("Fetching videos for user:", user.id);
      const response = await axios.get<Video[]>(`${API_BASE_URL}/api/videos`, {
        headers: {
          "user-id": user.id,
          Authorization: `Bearer ${token}`,
        },
      });
      console.log("Received videos:", response.data);

      // Sort videos by created_at in descending order (newest first)
      const sortedVideos = response.data.sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setVideos(sortedVideos);
      setRetryCount(0); // Reset retry count on successful fetch
    } catch (error: any) {
      console.error("Error fetching videos:", error);
      if (error.response?.status === 401) {
        toast.error("Please sign in to view your videos");
      } else if (retryCount < 3) {
        // Retry up to 3 times with exponential backoff
        const delay = Math.pow(2, retryCount) * 1000;
        setTimeout(() => {
          setRetryCount((prev) => prev + 1);
          fetchVideos();
        }, delay);
      } else {
        toast.error("Failed to load videos. Please try refreshing the page.");
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [user, isUserLoaded, isSignedIn, retryCount, getToken]);

  // Fetch videos when component mounts or when user/auth state changes
  useEffect(() => {
    let mounted = true;

    const loadVideos = async () => {
      if (isUserLoaded && mounted) {
        await fetchVideos();
      }
    };

    loadVideos();

    return () => {
      mounted = false;
    };
  }, [fetchVideos, isUserLoaded]);

  const handleRefresh = () => {
    setRefreshing(true);
    setRetryCount(0); // Reset retry count on manual refresh
    fetchVideos();
  };

  const handleDelete = async (videoId: string) => {
    if (!user || !isSignedIn) return;

    try {
      setDeletingId(videoId);
      const token = await getToken();

      if (!token) {
        throw new Error("No authentication token available");
      }

      await axios.delete(`${API_BASE_URL}/api/videos/${videoId}`, {
        headers: {
          "user-id": user.id,
          Authorization: `Bearer ${token}`,
        },
      });
      setVideos((prev) => prev.filter((v) => v.id !== videoId));
      toast.success("Video deleted successfully");
    } catch (error: any) {
      console.error("Error deleting video:", error);
      if (error.response?.status === 401) {
        toast.error("Please sign in to delete videos");
      } else {
        toast.error("Failed to delete video");
      }
    } finally {
      setDeletingId(null);
    }
  };

  const handleDownload = async (videoUrl: string, prompt: string) => {
    if (!isSignedIn) {
      toast.error("Please sign in to download videos");
      return;
    }

    try {
      const loadingToast = toast.loading("Preparing download...");
      const token = await getToken();

      if (!token) {
        throw new Error("No authentication token available");
      }

      const response = await axios.get(videoUrl, {
        responseType: "blob",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const blob = new Blob([response.data as BlobPart], { type: "video/mp4" });
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

  const handleVideoError = (videoId: string) => {
    setVideoErrors((prev) => ({ ...prev, [videoId]: true }));
    toast.error("Error loading video. Please try refreshing the page.");
  };

  if (!isUserLoaded) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isSignedIn) {
    return (
      <div className="text-center py-12 bg-card border rounded-lg">
        <p className="text-muted-foreground">
          Please sign in to view your videos
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {videos.length === 0 ? (
        <div className="text-center py-12 bg-card border rounded-lg">
          <p className="text-muted-foreground">
            No videos yet. Create your first animation!
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map((video) => (
            <div
              key={video.id}
              className="bg-card border rounded-lg overflow-hidden shadow-sm"
            >
              <div className="aspect-video bg-black/20 relative">
                {videoErrors[video.id] ? (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                    <p className="text-white text-sm">Error loading video</p>
                  </div>
                ) : (
                  <video
                    src={video.video_url}
                    controls
                    className="w-full h-full object-contain"
                    onError={() => handleVideoError(video.id)}
                  />
                )}
              </div>
              <div className="p-4">
                <p className="text-sm text-muted-foreground mb-2">
                  {new Date(video.created_at).toLocaleString()}
                </p>
                <p className="font-medium mb-4 line-clamp-2">{video.prompt}</p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={() =>
                      handleDownload(video.video_url, video.prompt)
                    }
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button
                        variant="destructive"
                        size="sm"
                        className="flex-1"
                        disabled={deletingId === video.id}
                      >
                        {deletingId === video.id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <>
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </>
                        )}
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Delete Video</AlertDialogTitle>
                        <AlertDialogDescription>
                          Are you sure you want to delete this video? This
                          action cannot be undone.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          onClick={() => handleDelete(video.id)}
                          className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        >
                          Delete
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default VideoGallery;
