"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import type { UserSession } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Monitor, Smartphone, Tablet, LogOut, MapPin, Clock } from "lucide-react";
import { formatDistance } from "date-fns";

export function SessionsManager() {
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [revoking, setRevoking] = useState<string | null>(null);

  const fetchSessions = async () => {
    try {
      const data = await apiClient.get<UserSession[]>("/api/v1/auth/me/sessions");
      setSessions(data);
    } catch (error) {
      toast.error("Failed to load sessions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleRevoke = async (sessionId: string) => {
    try {
      setRevoking(sessionId);
      await apiClient.delete(`/api/v1/auth/me/sessions/${sessionId}`);
      toast.success("Session revoked successfully");
      await fetchSessions();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to revoke session");
    } finally {
      setRevoking(null);
    }
  };

  const getDeviceIcon = (deviceInfo: string) => {
    const info = deviceInfo.toLowerCase();
    if (info.includes("mobile") || info.includes("android") || info.includes("iphone")) {
      return Smartphone;
    }
    if (info.includes("tablet") || info.includes("ipad")) {
      return Tablet;
    }
    return Monitor;
  };

  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-24 bg-muted animate-pulse rounded-lg" />
        ))}
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No active sessions found
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {sessions.map((session) => {
        const DeviceIcon = getDeviceIcon(session.device_info);
        
        return (
          <div
            key={session.id}
            className={`p-4 border rounded-lg ${
              session.is_current
                ? "border-primary bg-primary/5"
                : "border-border"
            }`}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-4 flex-1">
                <div className={`p-3 rounded-lg ${
                  session.is_current ? "bg-primary/10" : "bg-muted"
                }`}>
                  <DeviceIcon className={`h-5 w-5 ${
                    session.is_current ? "text-primary" : "text-muted-foreground"
                  }`} />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium truncate">
                      {session.device_info || "Unknown Device"}
                    </h4>
                    {session.is_current && (
                      <span className="px-2 py-0.5 bg-primary/20 text-primary text-xs font-medium rounded-full">
                        Current
                      </span>
                    )}
                  </div>
                  
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <MapPin className="h-3.5 w-3.5" />
                      <span>{session.ip_address}</span>
                    </div>
                    
                    {session.last_activity && (
                      <div className="flex items-center gap-1">
                        <Clock className="h-3.5 w-3.5" />
                        <span>
                          Active {formatDistance(new Date(session.last_activity), new Date(), { addSuffix: true })}
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <p className="text-xs text-muted-foreground mt-1">
                    Created {formatDistance(new Date(session.created_at), new Date(), { addSuffix: true })}
                  </p>
                </div>
              </div>

              {!session.is_current && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => handleRevoke(session.id)}
                  isLoading={revoking === session.id}
                >
                  <LogOut className="h-4 w-4 mr-1" />
                  Revoke
                </Button>
              )}
            </div>
          </div>
        );
      })}

      {sessions.filter(s => !s.is_current).length > 0 && (
        <div className="pt-4 border-t">
          <p className="text-sm text-muted-foreground mb-3">
            Revoke all other sessions except your current one
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={async () => {
              const otherSessions = sessions.filter(s => !s.is_current);
              for (const session of otherSessions) {
                await handleRevoke(session.id);
              }
            }}
          >
            Revoke All Other Sessions
          </Button>
        </div>
      )}
    </div>
  );
}
