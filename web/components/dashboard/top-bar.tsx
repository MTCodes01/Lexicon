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
  const menuRef = useRef<HTMLDivElement>(null);

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
            <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-medium text-sm">
                {user?.full_name?.[0] || user?.username?.[0] || user?.email?.[0] || "U"}
              </span>
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
