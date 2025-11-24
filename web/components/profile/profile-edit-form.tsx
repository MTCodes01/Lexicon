"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { useAuthStore } from "@/lib/auth-store";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import type { UserUpdate } from "@/lib/types";

const profileSchema = z.object({
  full_name: z.string().min(1, "Full name is required"),
  username: z.string().min(3, "Username must be at least 3 characters"),
  email: z.string().email("Invalid email address"),
  bio: z.string().optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

export function ProfileEditForm() {
  const { user, fetchUser } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      full_name: user?.full_name || "",
      username: user?.username || "",
      email: user?.email || "",
      bio: user?.bio || "",
    },
  });

  const onSubmit = async (data: ProfileFormData) => {
    try {
      setIsLoading(true);
      
      const updateData: UserUpdate = {
        full_name: data.full_name,
        username: data.username,
        email: data.email,
        bio: data.bio,
      };

      await apiClient.put("/api/v1/auth/me", updateData);
      await fetchUser(); // Refresh user data
      
      toast.success("Profile updated successfully!");
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to update profile");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 max-w-2xl">
      <Input
        label="Full Name"
        type="text"
        placeholder="John Doe"
        error={errors.full_name?.message}
        {...register("full_name")}
        disabled={isLoading}
      />

      <Input
        label="Username"
        type="text"
        placeholder="johndoe"
        error={errors.username?.message}
        {...register("username")}
        disabled={isLoading}
      />

      <Input
        label="Email Address"
        type="email"
        placeholder="john@example.com"
        error={errors.email?.message}
        {...register("email")}
        disabled={isLoading}
      />

      <Textarea
        label="Bio"
        placeholder="Tell us a little about yourself..."
        error={errors.bio?.message}
        {...register("bio")}
        disabled={isLoading}
        className="min-h-[120px]"
      />

      <div className="flex gap-3">
        <Button type="submit" isLoading={isLoading}>
          Save Changes
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={() => window.location.reload()}
          disabled={isLoading}
        >
          Cancel
        </Button>
      </div>
    </form>
  );
}
