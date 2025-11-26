"use client";

import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Save, Loader2 } from "lucide-react";

export function PrivacySettings() {
  const [isLoading, setIsLoading] = useState(false);
  const [settings, setSettings] = useState({
    profile_visibility: "public",
    show_email: false,
    allow_indexing: true,
    show_activity: true,
  });

  const handleSave = async () => {
    try {
      setIsLoading(true);
      // API call would go here
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success("Privacy settings updated");
    } catch (error) {
      toast.error("Failed to update privacy settings");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Privacy & Security</h3>
        <p className="text-sm text-muted-foreground">
          Manage your privacy preferences and data visibility
        </p>
      </div>

      <div className="space-y-6">
        <div className="space-y-4">
          <div>
            <Label>Profile Visibility</Label>
            <p className="text-sm text-muted-foreground mb-3">
              Control who can see your profile
            </p>
            <div className="space-y-2">
              {[
                { value: "public", label: "Public", description: "Anyone can view your profile" },
                { value: "private", label: "Private", description: "Only you can view your profile" },
              ].map((option) => (
                <label
                  key={option.value}
                  className="flex items-center gap-3 p-3 rounded-md border cursor-pointer hover:bg-accent"
                >
                  <input
                    type="radio"
                    name="profile_visibility"
                    value={option.value}
                    checked={settings.profile_visibility === option.value}
                    onChange={(e) => setSettings({ ...settings, profile_visibility: e.target.value })}
                    className="h-4 w-4"
                  />
                  <div>
                    <div className="font-medium text-sm">{option.label}</div>
                    <div className="text-xs text-muted-foreground">{option.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="pt-4 border-t space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Show Email on Profile</Label>
                <p className="text-sm text-muted-foreground">
                  Display your email address on your public profile
                </p>
              </div>
              <Switch
                checked={settings.show_email}
                onCheckedChange={(checked) => setSettings({ ...settings, show_email: checked })}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Allow Search Engine Indexing</Label>
                <p className="text-sm text-muted-foreground">
                  Allow search engines to index your profile
                </p>
              </div>
              <Switch
                checked={settings.allow_indexing}
                onCheckedChange={(checked) => setSettings({ ...settings, allow_indexing: checked })}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Show Activity Status</Label>
                <p className="text-sm text-muted-foreground">
                  Let others see when you're active
                </p>
              </div>
              <Switch
                checked={settings.show_activity}
                onCheckedChange={(checked) => setSettings({ ...settings, show_activity: checked })}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="mr-2 h-4 w-4" />
              Save Changes
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
