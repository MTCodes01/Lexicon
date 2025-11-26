"use client";

import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Save, Loader2, Mail, Bell, Shield } from "lucide-react";

export function NotificationSettings() {
  const [isLoading, setIsLoading] = useState(false);
  const [settings, setSettings] = useState({
    email_notifications: true,
    task_reminders: true,
    task_updates: false,
    weekly_digest: true,
    monthly_report: false,
    security_alerts: true,
    login_alerts: true,
    marketing_emails: false,
  });

  const handleSave = async () => {
    try {
      setIsLoading(true);
      // API call would go here
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success("Notification preferences updated");
    } catch (error) {
      toast.error("Failed to update notification settings");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Notifications</h3>
        <p className="text-sm text-muted-foreground">
          Configure how and when you want to be notified
        </p>
      </div>

      <div className="space-y-6">
        {/* Email Notifications */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Mail className="h-5 w-5 text-muted-foreground" />
            <h4 className="font-medium">Email Notifications</h4>
          </div>
          
          <div className="space-y-4 pl-7">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>All Email Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Master toggle for all email notifications
                </p>
              </div>
              <Switch
                checked={settings.email_notifications}
                onCheckedChange={(checked) => setSettings({ ...settings, email_notifications: checked })}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Task Reminders</Label>
                <p className="text-sm text-muted-foreground">
                  Get reminded about upcoming task deadlines
                </p>
              </div>
              <Switch
                checked={settings.task_reminders}
                onCheckedChange={(checked) => setSettings({ ...settings, task_reminders: checked })}
                disabled={!settings.email_notifications}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Task Updates</Label>
                <p className="text-sm text-muted-foreground">
                  Notifications when tasks are updated or completed
                </p>
              </div>
              <Switch
                checked={settings.task_updates}
                onCheckedChange={(checked) => setSettings({ ...settings, task_updates: checked })}
                disabled={!settings.email_notifications}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Weekly Digest</Label>
                <p className="text-sm text-muted-foreground">
                  Weekly summary of your activity and tasks
                </p>
              </div>
              <Switch
                checked={settings.weekly_digest}
                onCheckedChange={(checked) => setSettings({ ...settings, weekly_digest: checked })}
                disabled={!settings.email_notifications}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Monthly Report</Label>
                <p className="text-sm text-muted-foreground">
                  Monthly analytics and insights report
                </p>
              </div>
              <Switch
                checked={settings.monthly_report}
                onCheckedChange={(checked) => setSettings({ ...settings, monthly_report: checked })}
                disabled={!settings.email_notifications}
              />
            </div>
          </div>
        </div>

        {/* Security Alerts */}
        <div className="space-y-4 pt-4 border-t">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-muted-foreground" />
            <h4 className="font-medium">Security Alerts</h4>
          </div>
          
          <div className="space-y-4 pl-7">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Security Alerts</Label>
                <p className="text-sm text-muted-foreground">
                  Get notified about suspicious activity on your account
                </p>
              </div>
              <Switch
                checked={settings.security_alerts}
                onCheckedChange={(checked) => setSettings({ ...settings, security_alerts: checked })}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Login Alerts</Label>
                <p className="text-sm text-muted-foreground">
                  Notify me of new logins to my account
                </p>
              </div>
              <Switch
                checked={settings.login_alerts}
                onCheckedChange={(checked) => setSettings({ ...settings, login_alerts: checked })}
                disabled={!settings.security_alerts}
              />
            </div>
          </div>
        </div>

        {/* Marketing */}
        <div className="space-y-4 pt-4 border-t">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-muted-foreground" />
            <h4 className="font-medium">Marketing</h4>
          </div>
          
          <div className="space-y-4 pl-7">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Product Updates & News</Label>
                <p className="text-sm text-muted-foreground">
                  Receive updates about new features and improvements
                </p>
              </div>
              <Switch
                checked={settings.marketing_emails}
                onCheckedChange={(checked) => setSettings({ ...settings, marketing_emails: checked })}
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
              Save Preferences
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
