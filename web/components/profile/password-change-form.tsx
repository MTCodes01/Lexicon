"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AlertCircle } from "lucide-react";

const passwordSchema = z.object({
  current_password: z.string().min(1, "Current password is required"),
  new_password: z.string().min(8, "Password must be at least 8 characters"),
  confirm_password: z.string().min(1, "Please confirm your password"),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ["confirm_password"],
});

type PasswordFormData = z.infer<typeof passwordSchema>;

export function PasswordChangeForm() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<PasswordFormData>({
    resolver: zodResolver(passwordSchema),
  });

  const onSubmit = async (data: PasswordFormData) => {
    try {
      setIsLoading(true);
      
      await apiClient.put("/api/v1/auth/me/password", {
        current_password: data.current_password,
        new_password: data.new_password,
      });
      
      toast.success("Password updated successfully! Please log in again.");
      
      // Redirect to login after short delay
      setTimeout(() => {
        router.push("/login");
      }, 1500);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to update password");
    } finally {
      setIsLoading(false);
    }
  };

  const getPasswordStrength = (password: string) => {
    if (!password) return { strength: 0, label: "", color: "" };
    
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;

    const labels = ["Weak", "Fair", "Good", "Strong", "Very Strong"];
    const colors = [
      "bg-red-500",
      "bg-orange-500",
      "bg-yellow-500",
      "bg-green-500",
      "bg-emerald-500",
    ];

    return {
      strength: (strength / 5) * 100,
      label: labels[strength - 1] || "",
      color: colors[strength - 1] || "",
    };
  };

  const [newPassword, setNewPassword] = useState("");
  const passwordStrength = getPasswordStrength(newPassword);

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 max-w-2xl">
      <div className="flex items-start gap-3 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
        <AlertCircle className="h-5 w-5 text-yellow-600 dark:text-yellow-500 mt-0.5" />
        <div className="text-sm">
          <p className="font-medium text-yellow-600 dark:text-yellow-500">
            Security Notice
          </p>
          <p className="text-yellow-600/80 dark:text-yellow-500/80 mt-1">
            Changing your password will log you out of all active sessions. You'll need to log in again.
          </p>
        </div>
      </div>

      <Input
        label="Current Password"
        type="password"
        placeholder="••••••••"
        error={errors.current_password?.message}
        {...register("current_password")}
        disabled={isLoading}
      />

      <div>
        <Input
          label="New Password"
          type="password"
          placeholder="••••••••"
          error={errors.new_password?.message}
          {...register("new_password")}
          onChange={(e) => setNewPassword(e.target.value)}
          disabled={isLoading}
        />
        {newPassword && (
          <div className="mt-2">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-muted-foreground">Password strength:</span>
              <span className="font-medium">{passwordStrength.label}</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div
                className={`h-full transition-all ${passwordStrength.color}`}
                style={{ width: `${passwordStrength.strength}%` }}
              />
            </div>
          </div>
        )}
      </div>

      <Input
        label="Confirm New Password"
        type="password"
        placeholder="••••••••"
        error={errors.confirm_password?.message}
        {...register("confirm_password")}
        disabled={isLoading}
      />

      <div className="flex gap-3">
        <Button type="submit" isLoading={isLoading}>
          Update Password
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={() => reset()}
          disabled={isLoading}
        >
          Reset
        </Button>
      </div>
    </form>
  );
}
