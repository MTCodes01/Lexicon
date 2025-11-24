"use client";

import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import { useAuthStore } from "@/lib/auth-store";
import { Button } from "@/components/ui/button";
import { Bell, Moon, Sun, User, LogOut, Settings } from "lucide-react";
import { useState, useRef, useEffect } from "react";

export function TopBar() {
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const { user, logout } = useAuthStore();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [profileImage, setProfileImage] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // Load profile image from user data or localStorage
  useEffect(() => {
    // First try to get from user data (from backend)
    if (user?.avatar_url) {
      setProfileImage(user.avatar_url);
    } else if (typeof window !== "undefined") {
      const savedImage = localStorage.getItem("profile_image");
      if (savedImage) {
        setProfileImage(savedImage);
      }

      // Listen for profile image updates
      const handleImageUpdate = () => {
        const updatedImage = localStorage.getItem("profile_image");
        setProfileImage(updatedImage);
      };

      window.addEventListener("profile_image_updated", handleImageUpdate);
      window.addEventListener("storage", handleImageUpdate);

      return () => {
        window.removeEventListener("profile_image_updated", handleImageUpdate);
        window.removeEventListener("storage", handleImageUpdate);
      };
    }
  }, [user]);

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  const getInitials = () => {
    if (!user) return "U";
    if (user.full_name) {
      const names = user.full_name.split(" ");
      if (names.length >= 2) {
        return `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase();
      }
      return user.full_name[0].toUpperCase();
    }
    return user.username?.[0]?.toUpperCase() || user.email?.[0]?.toUpperCase() || "U";
  };

  return (
    <header className="flex h-16 items-center justify-between border-b bg-card px-6">
      {/* Search / Breadcrumb */}
      <div className="flex-1">
        <h2 className="text-lg font-semibold">Dashboard</h2>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        {/* Theme Toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          title="Toggle theme"
        >
          <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
        </Button>

        {/* Notifications */}
        <Button variant="ghost" size="icon" title="Notifications">
          <Bell className="h-5 w-5" />
        </Button>

        {/* User Menu */}
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 rounded-md px-3 py-2 hover:bg-accent transition-colors"
          >
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center overflow-hidden ring-2 ring-background shadow-md">
              {profileImage ? (
                <img 
                  src={profileImage} 
                  alt="Profile" 
                  className="w-full h-full object-cover"
                />
              ) : (
                <span className="text-primary-foreground font-medium text-sm">
                  {getInitials()}
                </span>
              )}
            </div>
            <div className="hidden md:block text-left">
              <p className="text-sm font-medium">
                {user?.full_name || user?.username || "User"}
              </p>
              <p className="text-xs text-muted-foreground">{user?.email}</p>
            </div>
          </button>

          {/* Dropdown Menu */}
          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-56 rounded-md border bg-popover p-1 shadow-lg z-50">
              <button
                onClick={() => {
                  router.push("/dashboard/profile");
                  setShowUserMenu(false);
                }}
                className="flex w-full items-center gap-2 rounded-sm px-3 py-2 text-sm hover:bg-accent transition-colors"
              >
                <User className="h-4 w-4" />
                <span>Profile</span>
              </button>
              <button
                onClick={() => {
                  router.push("/dashboard/settings");
                  setShowUserMenu(false);
                }}
                className="flex w-full items-center gap-2 rounded-sm px-3 py-2 text-sm hover:bg-accent transition-colors"
              >
                <Settings className="h-4 w-4" />
                <span>Settings</span>
              </button>
              <div className="my-1 h-px bg-border" />
              <button
                onClick={handleLogout}
                className="flex w-full items-center gap-2 rounded-sm px-3 py-2 text-sm text-destructive hover:bg-accent transition-colors"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
