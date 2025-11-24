"use client";

import { useAuthStore } from "@/lib/auth-store";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckSquare, FileText, Calendar, DollarSign, Activity, Folder } from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuthStore();

  const stats = [
    {
      title: "Tasks",
      value: "12",
      description: "3 due today",
      icon: CheckSquare,
      color: "text-blue-500",
    },
    {
      title: "Notes",
      value: "24",
      description: "5 updated this week",
      icon: FileText,
      color: "text-green-500",
    },
    {
      title: "Events",
      value: "8",
      description: "2 upcoming",
      icon: Calendar,
      color: "text-purple-500",
    },
    {
      title: "Files",
      value: "156",
      description: "2.4 GB used",
      icon: Folder,
      color: "text-orange-500",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          Welcome back, {user?.full_name || user?.username || user?.email}!
        </h1>
        <p className="text-muted-foreground mt-2">
          Here's what's happening with your Lexicon today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {stat.description}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Recent Activity */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Tasks</CardTitle>
            <CardDescription>Your latest task updates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="h-2 w-2 rounded-full bg-blue-500" />
                <div className="flex-1">
                  <p className="text-sm font-medium">Complete project proposal</p>
                  <p className="text-xs text-muted-foreground">Due today</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="h-2 w-2 rounded-full bg-green-500" />
                <div className="flex-1">
                  <p className="text-sm font-medium">Review pull requests</p>
                  <p className="text-xs text-muted-foreground">Due tomorrow</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="h-2 w-2 rounded-full bg-yellow-500" />
                <div className="flex-1">
                  <p className="text-sm font-medium">Update documentation</p>
                  <p className="text-xs text-muted-foreground">Due in 3 days</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks and shortcuts</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <button className="w-full text-left px-4 py-2 rounded-md hover:bg-accent transition-colors">
                <div className="flex items-center gap-3">
                  <CheckSquare className="h-4 w-4 text-blue-500" />
                  <span className="text-sm font-medium">Create new task</span>
                </div>
              </button>
              <button className="w-full text-left px-4 py-2 rounded-md hover:bg-accent transition-colors">
                <div className="flex items-center gap-3">
                  <FileText className="h-4 w-4 text-green-500" />
                  <span className="text-sm font-medium">Write a note</span>
                </div>
              </button>
              <button className="w-full text-left px-4 py-2 rounded-md hover:bg-accent transition-colors">
                <div className="flex items-center gap-3">
                  <Calendar className="h-4 w-4 text-purple-500" />
                  <span className="text-sm font-medium">Schedule event</span>
                </div>
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
