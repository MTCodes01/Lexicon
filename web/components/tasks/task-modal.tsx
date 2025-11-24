"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { Task, TaskCreate, TaskUpdate } from "@/lib/types";

const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(255, "Title too long"),
  description: z.string().optional(),
  priority: z.enum(["low", "medium", "high", "urgent"]),
  status: z.enum(["todo", "in_progress", "completed", "cancelled"]),
  due_date: z.string().optional(),
  tags: z.string().optional(), // Comma-separated tags
});

type TaskFormData = z.infer<typeof taskSchema>;

interface TaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => Promise<void>;
  task?: Task;
  isLoading?: boolean;
}

export function TaskModal({ isOpen, onClose, onSubmit, task, isLoading }: TaskModalProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      priority: "medium",
      status: "todo",
    },
  });

  // Reset form when task changes (for editing)
  useEffect(() => {
    if (task) {
      reset({
        title: task.title,
        description: task.description || "",
        priority: task.priority,
        status: task.status,
        due_date: task.due_date ? new Date(task.due_date).toISOString().split("T")[0] : "",
        tags: task.tags?.join(", ") || "",
      });
    } else {
      reset({
        title: "",
        description: "",
        priority: "medium",
        status: "todo",
        due_date: "",
        tags: "",
      });
    }
  }, [task, reset]);

  const handleFormSubmit = async (data: TaskFormData) => {
    const taskData: any = {
      title: data.title,
      description: data.description || undefined,
      priority: data.priority as any,
      status: data.status as any,
      due_date: data.due_date || undefined,
      tags: data.tags ? data.tags.split(",").map((t) => t.trim()).filter(Boolean) : undefined,
    };

    await onSubmit(taskData);
    reset();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-card rounded-lg shadow-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold">
            {task ? "Edit Task" : "Create New Task"}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-accent rounded-md transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(handleFormSubmit)} className="p-6 space-y-4">
          {/* Title */}
          <Input
            label="Title"
            placeholder="Enter task title"
            error={errors.title?.message}
            required
            {...register("title")}
          />

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Description
            </label>
            <textarea
              placeholder="Enter task description (optional)"
              className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              {...register("description")}
            />
            {errors.description && (
              <p className="mt-1 text-sm text-destructive">{errors.description.message}</p>
            )}
          </div>

          {/* Priority and Status */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Priority <span className="text-destructive">*</span>
              </label>
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                {...register("priority")}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
              {errors.priority && (
                <p className="mt-1 text-sm text-destructive">{errors.priority.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Status <span className="text-destructive">*</span>
              </label>
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                {...register("status")}
              >
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
              {errors.status && (
                <p className="mt-1 text-sm text-destructive">{errors.status.message}</p>
              )}
            </div>
          </div>

          {/* Due Date */}
          <Input
            label="Due Date"
            type="date"
            helperText="Optional - set a deadline for this task"
            {...register("due_date")}
          />

          {/* Tags */}
          <Input
            label="Tags"
            placeholder="work, urgent, project-x (comma-separated)"
            helperText="Separate tags with commas"
            {...register("tags")}
          />

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" isLoading={isLoading}>
              {task ? "Update Task" : "Create Task"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
