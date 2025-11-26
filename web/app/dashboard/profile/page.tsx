"use client";

import { useState } from "react";
import { useAuthStore } from "@/lib/auth-store";
import { ProfileHeader } from "@/components/profile/profile-header";
import { StatsCards } from "@/components/profile/stats-cards";
import { ProfileEditForm } from "@/components/profile/profile-edit-form";
import { PasswordChangeForm } from "@/components/profile/password-change-form";
import { MFASetup } from "@/components/profile/mfa-setup";
import { SessionsManager } from "@/components/profile/sessions-manager";
import { Card } from "@/components/ui/card";

type Tab = "overview" | "edit" | "security" | "sessions";

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  const tabs = [
    { id: "overview" as Tab, label: "Overview", icon: "👤" },
    { id: "edit" as Tab, label: "Edit Profile", icon: "✏️" },
    { id: "security" as Tab, label: "Security", icon: "🔒" },
    { id: "sessions" as Tab, label: "Sessions", icon: "📱" },
  ];

  const { user } = useAuthStore();

  return (
    <div className="container max-w-6xl py-8 space-y-8">
      {/* Profile Header */}
      <ProfileHeader />

      {/* Tabs Navigation */}
      <div className="border-b">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center gap-2 px-1 py-4 border-b-2 font-medium text-sm transition-colors
                ${
                  activeTab === tab.id
                    ? "border-primary text-primary"
                    : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
                }
              `}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {activeTab === "overview" && (
          <div className="space-y-8">
            <StatsCards />
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">About You</h3>
                <button 
                  onClick={() => setActiveTab("edit")}
                  className="text-sm text-primary hover:underline"
                >
                  Edit
                </button>
              </div>
              <p className="text-muted-foreground whitespace-pre-wrap">
                {user?.bio || "Tell us a little about yourself... Click 'Edit' to add a bio."}
              </p>
            </Card>
          </div>
        )}

        {activeTab === "edit" && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-6">Edit Profile Information</h3>
            <ProfileEditForm />
          </Card>
        )}

        {activeTab === "security" && (
          <div className="space-y-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-6">Change Password</h3>
              <PasswordChangeForm />
            </Card>
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-6">Two-Factor Authentication</h3>
              <MFASetup />
            </Card>
          </div>
        )}

        {activeTab === "sessions" && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-6">Active Sessions</h3>
            <SessionsManager />
          </Card>
        )}
      </div>
    </div>
  );
}
