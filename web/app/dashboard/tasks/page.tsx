"use client";

import { useState, useEffect } from "react";
import { useAuthStore } from "@/lib/auth-store";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { TaskModal } from "@/components/tasks/task-modal";
import { Plus, Search, CheckCircle2, Circle, Clock, Edit, Trash2, Calendar } from "lucide-react";
import { toast } from "sonner";
import type { Task, TaskStatus, TaskPriority, TaskCreate, TaskUpdate } from "@/lib/types";

export default function TasksPage() {
  const { user } = useAuthStore();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState<TaskStatus | "all">("all");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | undefined>();
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const response = await apiClient.listTasks();
      setTasks(response.items);
    } catch (error: any) {
      toast.error("Failed to load tasks");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (data: TaskCreate) => {
    try {
      setIsSubmitting(true);
      await apiClient.createTask(data);
      toast.success("Task created successfully!");
      setIsModalOpen(false);
      loadTasks();
    } catch (error) {
      toast.error("Failed to create task");
      throw error;
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateTask = async (data: TaskUpdate) => {
    if (!editingTask) return;
    
    try {
      setIsSubmitting(true);
      await apiClient.updateTask(editingTask.id, data);
      toast.success("Task updated successfully!");
      setIsModalOpen(false);
      setEditingTask(undefined);
      loadTasks();
    } catch (error) {
      toast.error("Failed to update task");
      throw error;
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!confirm("Are you sure you want to delete this task?")) return;

    try {
      await apiClient.deleteTask(taskId);
      toast.success("Task deleted!");
      loadTasks();
    } catch (error) {
      toast.error("Failed to delete task");
    }
  };

  const handleToggleComplete = async (task: Task) => {
    try {
      // Toggle between completed and todo
      const newStatus = (task.status === "completed" ? "todo" : "completed") as TaskStatus;
      await apiClient.updateTask(task.id, { status: newStatus });
      toast.success(newStatus === "completed" ? "Task completed!" : "Task reopened!");
      loadTasks();
    } catch (error) {
      toast.error("Failed to update task");
    }
  };

  const openEditModal = (task: Task) => {
    setEditingTask(task);
    setIsModalOpen(true);
  };

  const openCreateModal = () => {
    setEditingTask(undefined);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingTask(undefined);
  };

  const filteredTasks = tasks.filter((task) => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === "all" || task.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case "urgent":
        return "text-red-500 bg-red-500/10";
      case "high":
        return "text-orange-500 bg-orange-500/10";
      case "medium":
        return "text-yellow-500 bg-yellow-500/10";
      case "low":
        return "text-green-500 bg-green-500/10";
      default:
        return "text-gray-500 bg-gray-500/10";
    }
  };

  const getStatusIcon = (status: TaskStatus) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case "in_progress":
        return <Clock className="h-5 w-5 text-blue-500" />;
      default:
        return <Circle className="h-5 w-5 text-gray-400" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent" />
          <p className="mt-4 text-muted-foreground">Loading tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Tasks</h1>
          <p className="text-muted-foreground mt-1">
            Manage your tasks and stay organized
          </p>
        </div>
        <Button onClick={openCreateModal}>
          <Plus className="h-4 w-4 mr-2" />
          New Task
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value as any)}
          className="px-4 py-2 rounded-md border bg-background"
        >
          <option value="all">All Status</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Total</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tasks.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">To Do</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {tasks.filter((t) => t.status === "todo").length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {tasks.filter((t) => t.status === "in_progress").length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {tasks.filter((t) => t.status === "completed").length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Task List */}
      <Card>
        <CardHeader>
          <CardTitle>Your Tasks</CardTitle>
          <CardDescription>
            {filteredTasks.length} {filteredTasks.length === 1 ? "task" : "tasks"} found
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredTasks.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No tasks found</p>
              <Button className="mt-4" onClick={openCreateModal}>
                <Plus className="h-4 w-4 mr-2" />
                Create your first task
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredTasks.map((task) => (
                <div
                  key={task.id}
                  className="flex items-center gap-4 p-4 rounded-lg border hover:bg-accent transition-colors group"
                >
                  <button
                    onClick={() => handleToggleComplete(task)}
                    className="flex-shrink-0 hover:scale-110 transition-transform"
                    title={task.status === "completed" ? "Mark as incomplete" : "Mark as complete"}
                  >
                    {getStatusIcon(task.status)}
                  </button>
                  
                  <div className="flex-1 min-w-0">
                    <h3 className={`font-medium ${task.status === "completed" ? "line-through text-muted-foreground" : ""}`}>
                      {task.title}
                    </h3>
                    {task.description && (
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                        {task.description}
                      </p>
                    )}
                    <div className="flex items-center gap-3 mt-2 flex-wrap">
                      <span className={`text-xs font-medium px-2 py-1 rounded-full ${getPriorityColor(task.priority)}`}>
                        {task.priority.toUpperCase()}
                      </span>
                      {task.due_date && (
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(task.due_date).toLocaleDateString()}
                        </span>
                      )}
                      {task.tags && task.tags.length > 0 && (
                        <div className="flex gap-1">
                          {task.tags.map((tag, i) => (
                            <span
                              key={i}
                              className="text-xs px-2 py-1 rounded-full bg-secondary"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openEditModal(task)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteTask(task.id)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Task Modal */}
      <TaskModal
        isOpen={isModalOpen}
        onClose={closeModal}
        onSubmit={editingTask ? handleUpdateTask : handleCreateTask}
        task={editingTask}
        isLoading={isSubmitting}
      />
    </div>
  );
}
