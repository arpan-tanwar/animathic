import React, { useState, useEffect, useCallback } from "react";
import { useUser, useAuth } from "@clerk/clerk-react";
import { Link } from "react-router-dom";
import axios from "axios";
import { toast } from "react-hot-toast";
import { Button } from "./ui/button";
import {
  Trash2,
  Loader2,
  Download,
  RefreshCw,
  Play,
  Calendar,
  AlertCircle,
} from "lucide-react";
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

      const response = await axios.get<Video[]>(`${API_BASE_URL}/api/videos`, {
        headers: {
          "user-id": user.id,
          Authorization: `Bearer ${token}`,
        },
      });

      // Sort videos by created_at in descending order (newest first)
      const sortedVideos = response.data.sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setVideos(sortedVideos);
      setRetryCount(0); // Reset retry count on successful fetch
    } catch (error: unknown) {
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

      // Check if this is a storage video (ID starts with "storage_")
      let deleteUrl = `${API_BASE_URL}/api/videos/${videoId}`;
      
      if (videoId.startsWith('storage_')) {
        // For storage videos, extract object_key from video_url
        const video = videos.find(v => v.id === videoId);
        if (video && video.video_url) {
          // Extract object_key from video_url like: /api/stream?bucket=animathic-media&key=user_id/filename.mp4
          const urlParams = new URLSearchParams(video.video_url.split('?')[1]);
          const objectKey = urlParams.get('key');
          if (objectKey) {
            deleteUrl += `?object_key=${encodeURIComponent(objectKey)}`;
          }
        }
      }

      await axios.delete(deleteUrl, {
        headers: {
          "user-id": user.id,
          Authorization: `Bearer ${token}`,
        },
      });
      setVideos((prev) => prev.filter((v) => v.id !== videoId));
      toast.success("Video deleted successfully");
    } catch (error: unknown) {
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

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (!isUserLoaded) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-accent-primary mx-auto" />
          <p className="text-secondary">Loading videos...</p>
        </div>
      </div>
    );
  }

  if (!isSignedIn) {
    return (
      <div className="text-center py-16 surface-primary rounded-2xl border border-subtle">
        <div className="space-y-4">
          <AlertCircle className="w-12 h-12 text-muted mx-auto" />
          <p className="text-secondary">Please sign in to view your videos</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-accent-primary mx-auto" />
          <p className="text-secondary">Loading your videos...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with refresh button */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h3 className="text-lg font-semibold text-primary">
            Recent Animations
          </h3>
          <p className="text-sm text-secondary">{videos.length} total videos</p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          disabled={refreshing}
          className="interactive focus-ring"
        >
          <RefreshCw
            className={`w-4 h-4 mr-2 ${refreshing ? "animate-spin" : ""}`}
          />
          Refresh
        </Button>
      </div>

      {videos.length === 0 ? (
        <div className="text-center py-16 surface-primary rounded-2xl border border-subtle">
          <div className="space-y-6 max-w-md mx-auto">
            <div className="w-16 h-16 rounded-full bg-accent-primary/10 flex items-center justify-center mx-auto">
              <Play className="w-8 h-8 text-accent-primary" />
            </div>

            <div className="space-y-2">
              <h3 className="text-lg font-semibold text-primary">
                No animations yet
              </h3>
              <p className="text-secondary">
                Create your first mathematical animation to get started!
              </p>
            </div>

            <Button asChild className="btn-primary interactive">
              <Link to="/generate">Create Animation</Link>
            </Button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map((video, index) => (
            <div
              key={video.id}
              className="surface-primary rounded-2xl overflow-hidden border border-subtle interactive group animate-scale-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              {/* Video preview */}
              <div className="aspect-video bg-surface-tertiary relative">
                {videoErrors[video.id] ? (
                  <div className="absolute inset-0 flex items-center justify-center bg-surface-secondary">
                    <div className="text-center space-y-2">
                      <AlertCircle className="w-8 h-8 text-muted mx-auto" />
                      <p className="text-sm text-secondary">
                        Error loading video
                      </p>
                    </div>
                  </div>
                ) : (
                  <video
                    src={video.video_url}
                    controls
                    className="w-full h-full object-contain bg-black/20"
                    onError={() => handleVideoError(video.id)}
                    preload="metadata"
                  />
                )}
              </div>

              {/* Content */}
              <div className="p-5 space-y-4">
                {/* Date */}
                <div className="flex items-center gap-2 text-xs text-muted">
                  <Calendar className="w-3 h-3" />
                  <span>{formatDate(video.created_at)}</span>
                </div>

                {/* Prompt */}
                <div className="space-y-2">
                  <p className="text-sm font-medium text-primary line-clamp-3 leading-relaxed">
                    {video.prompt}
                  </p>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 interactive focus-ring"
                    onClick={() =>
                      handleDownload(video.video_url, video.prompt)
                    }
                  >
                    <Download className="h-3 w-3 mr-2" />
                    Download
                  </Button>

                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button
                        variant="destructive"
                        size="sm"
                        disabled={deletingId === video.id}
                        className="interactive focus-ring"
                      >
                        {deletingId === video.id ? (
                          <Loader2 className="h-3 w-3 animate-spin" />
                        ) : (
                          <Trash2 className="h-3 w-3" />
                        )}
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent className="surface-elevated">
                      <AlertDialogHeader>
                        <AlertDialogTitle className="text-primary">
                          Delete Animation
                        </AlertDialogTitle>
                        <AlertDialogDescription className="text-secondary">
                          Are you sure you want to delete this animation? This
                          action cannot be undone.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel className="btn-ghost">
                          Cancel
                        </AlertDialogCancel>
                        <AlertDialogAction
                          onClick={() => handleDelete(video.id)}
                          className="bg-red-600 text-white hover:bg-red-700"
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
