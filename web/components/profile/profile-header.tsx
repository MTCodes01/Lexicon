"use client";

import { useAuthStore } from "@/lib/auth-store";
import { useState, useRef, useEffect } from "react";
import { Camera, Edit2, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { apiClient } from "@/lib/api-client";

export function ProfileHeader() {
  const { user, fetchUser } = useAuthStore();
  const [isUploading, setIsUploading] = useState(false);
  const [isUploadingBanner, setIsUploadingBanner] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [bannerUrl, setBannerUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const bannerInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Load avatar and banner directly from user data
    if (user?.avatar_url) {
      setAvatarUrl(user.avatar_url);
    } else {
      setAvatarUrl(null);
    }

    if (user?.banner_url) {
      setBannerUrl(user.banner_url);
    } else {
      setBannerUrl(null);
    }
  }, [user]);

  if (!user) return null;

  const getInitials = () => {
    if (user.full_name) {
      const names = user.full_name.split(" ");
      if (names.length >= 2) {
        return `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase();
      }
      return user.full_name[0].toUpperCase();
    }
    return user.username?.[0]?.toUpperCase() || user.email[0].toUpperCase();
  };

  const getMemberSince = () => {
    if (user.created_at) {
      const createdDate = new Date(user.created_at);
      const now = new Date();
      const diffTime = Math.abs(now.getTime() - createdDate.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays < 1) return "Today";
      if (diffDays === 1) return "Yesterday";
      if (diffDays < 30) return `${diffDays} days ago`;
      if (diffDays < 365) {
        const months = Math.floor(diffDays / 30);
        return `${months} ${months === 1 ? 'month' : 'months'} ago`;
      }
      const years = Math.floor(diffDays / 365);
      return `${years} ${years === 1 ? 'year' : 'years'} ago`;
    }
    return "Recently";
  };

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith("image/")) {
      toast.error("Please upload an image file");
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error("Image size should be less than 5MB");
      return;
    }

    try {
      setIsUploading(true);
      const formData = new FormData();
      formData.append("file", file);

      await apiClient.post("/api/v1/auth/me/avatar", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      await fetchUser(); // Refresh user data to get new URL
      toast.success("Profile photo updated successfully!");
    } catch (error) {
      console.error("Upload error:", error);
      toast.error("Failed to upload image");
    } finally {
      setIsUploading(false);
    }
  };

  const handleBannerUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith("image/")) {
      toast.error("Please upload an image file");
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error("Banner size should be less than 10MB");
      return;
    }

    try {
      setIsUploadingBanner(true);
      const formData = new FormData();
      formData.append("file", file);

      await apiClient.post("/api/v1/auth/me/banner", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      await fetchUser(); // Refresh user data
      toast.success("Banner updated successfully!");
    } catch (error) {
      console.error("Banner upload error:", error);
      toast.error("Failed to upload banner");
    } finally {
      setIsUploadingBanner(false);
    }
  };

  return (
    <div className="relative mb-8 group/banner">
      {/* Banner Section */}
      <div className="h-48 md:h-64 rounded-xl overflow-hidden bg-gradient-to-r from-blue-600 to-purple-600 relative shadow-md">
        {bannerUrl && (
          <img 
            src={bannerUrl} 
            alt="Profile Banner" 
            className="w-full h-full object-cover"
          />
        )}
        <div className="absolute inset-0 bg-black/10 group-hover/banner:bg-black/30 transition-colors" />
        
        <button
          onClick={() => bannerInputRef.current?.click()}
          className="absolute top-4 right-4 p-2 bg-black/40 hover:bg-black/60 text-white rounded-lg opacity-0 group-hover/banner:opacity-100 transition-opacity backdrop-blur-sm"
          disabled={isUploadingBanner}
        >
          {isUploadingBanner ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Camera className="h-5 w-5" />
          )}
        </button>
        <input
          type="file"
          ref={bannerInputRef}
          className="hidden"
          accept="image/*"
          onChange={handleBannerUpload}
        />
      </div>

      {/* Profile Info Section */}
      <div className="px-6 md:px-10">
        <div className="flex flex-col md:flex-row gap-6 items-start relative z-10">
          {/* Avatar Group */}
          <div className="-mt-12 md:-mt-16 relative group shrink-0">
            <div className="h-24 w-24 md:h-32 md:w-32 rounded-full border-4 border-background bg-muted overflow-hidden relative shadow-xl">
              {avatarUrl ? (
                <img src={avatarUrl} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary to-purple-600">
                  <span className="text-3xl md:text-4xl font-bold text-white">
                    {getInitials()}
                  </span>
                </div>
              )}
            </div>
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="absolute bottom-0 right-0 p-1.5 md:p-2 bg-primary text-primary-foreground rounded-full shadow-lg hover:scale-110 transition-transform cursor-pointer z-20"
              disabled={isUploading}
            >
              {isUploading ? (
                <Loader2 className="h-3 w-3 md:h-4 md:w-4 animate-spin" />
              ) : (
                <Camera className="h-3 w-3 md:h-4 md:w-4" />
              )}
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
            />
          </div>

          {/* Text Info */}
          <div className="flex-1 space-y-1 pt-2 md:pt-4">
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">
              {user.full_name || user.username}
            </h1>
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm md:text-base text-muted-foreground">
              <span>{user.email}</span>
              <span className="hidden md:inline">•</span>
              <span>Joined {getMemberSince()}</span>
              {user.mfa_enabled && (
                <>
                  <span className="hidden md:inline">•</span>
                  <span className="text-green-500 flex items-center gap-1 font-medium bg-green-500/10 px-2 py-0.5 rounded-full">
                    MFA Secured
                  </span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
