"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import type { UserStats } from "@/lib/types";
import { Users, Calendar, Shield, Clock, TrendingUp } from "lucide-react";

function useAnimatedValue(targetValue: number, duration: number = 1000) {
  const [currentValue, setCurrentValue] = useState(0);

  useEffect(() => {
    const startTime = Date.now();
    const startValue = 0;

    const animate = () => {
      const now = Date.now();
      const progress = Math.min((now - startTime) / duration, 1);
      const easeProgress = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      
      setCurrentValue(Math.floor(startValue + (targetValue - startValue) * easeProgress));

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [targetValue, duration]);

  return currentValue;
}

export function StatsCards() {
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await apiClient.get<UserStats>("/api/v1/auth/me/stats");
        setStats(data);
      } catch (error) {
        console.error("Failed to fetch stats:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-36 bg-gradient-to-br from-muted to-muted/50 animate-pulse rounded-xl" />
        ))}
      </div>
    );
  }

  if (!stats) return null;

  // Helper function to format account age
  const formatAccountAge = (days: number, createdAt: string) => {
    if (days === 0) {
      const created = new Date(createdAt);
      const now = new Date();
      const hoursDiff = Math.floor((now.getTime() - created.getTime()) / (1000 * 60 * 60));
      
      if (hoursDiff < 1) {
        const minutesDiff = Math.floor((now.getTime() - created.getTime()) / (1000 * 60));
        return minutesDiff <= 1 ? "Just now" : `${minutesDiff} min ago`;
      }
      return hoursDiff === 1 ? "1 hour ago" : `${hoursDiff} hours ago`;
    }
    if (days === 1) return "Yesterday";
    if (days < 30) return `${days} days ago`;
    if (days < 365) {
      const months = Math.floor(days / 30);
      return `${months} ${months === 1 ? 'month' : 'months'} ago`;
    }
    const years = Math.floor(days / 365);
    return `${years} ${years === 1 ? 'year' : 'years'} ago`;
  };

  const statCards = [
    {
      icon: Calendar,
      label: "Account Age",
      value: stats.account_age_days,
      displayValue: formatAccountAge(stats.account_age_days, stats.created_at),
      gradient: "from-blue-500/10 via-cyan-500/5 to-transparent",
      iconBg: "bg-gradient-to-br from-blue-500/20 to-cyan-500/20",
      iconColor: "text-blue-600 dark:text-blue-400",
      borderAccent: "hover:border-blue-500/30",
    },
    {
      icon: TrendingUp,
      label: "Total Tasks",
      value: stats.total_tasks,
      suffix: "",
      gradient: "from-green-500/10 via-emerald-500/5 to-transparent",
      iconBg: "bg-gradient-to-br from-green-500/20 to-emerald-500/20",
      iconColor: "text-green-600 dark:text-green-400",
      borderAccent: "hover:border-green-500/30",
    },
    {
      icon: Shield,
      label: "Active Sessions",
      value: stats.active_sessions,
      suffix: "",
      gradient: "from-purple-500/10 via-pink-500/5 to-transparent",
      iconBg: "bg-gradient-to-br from-purple-500/20 to-pink-500/20",
      iconColor: "text-purple-600 dark:text-purple-400",
      borderAccent: "hover:border-purple-500/30",
    },
    {
      icon: Clock,
      label: "Last Login",
      value: 0,
      displayValue: stats.last_login
        ? new Date(stats.last_login).toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })
        : "Never",
      gradient: "from-orange-500/10 via-amber-500/5 to-transparent",
      iconBg: "bg-gradient-to-br from-orange-500/20 to-amber-500/20",
      iconColor: "text-orange-600 dark:text-orange-400",
      borderAccent: "hover:border-orange-500/30",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {statCards.map((stat, index) => (
        <div
          key={stat.label}
          className={`group relative overflow-hidden p-6 border rounded-xl bg-gradient-to-br ${stat.gradient} hover:shadow-lg transition-all duration-300 ${stat.borderAccent} animate-in fade-in slide-in-from-bottom-4`}
          style={{ animationDelay: `${index * 100}ms` }}
        >
          {/* Animated background glow */}
          <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
          
          <div className="relative">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-lg ${stat.iconBg} shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                <stat.icon className={`h-6 w-6 ${stat.iconColor}`} />
              </div>
            </div>
            
            <div className="space-y-1">
              <p className="text-3xl font-bold bg-gradient-to-br from-foreground to-foreground/60 bg-clip-text">
                {stat.displayValue !== undefined 
                  ? stat.displayValue 
                  : `${stat.value}${stat.suffix}`
                }
              </p>
              <p className="text-sm text-muted-foreground font-medium">{stat.label}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
