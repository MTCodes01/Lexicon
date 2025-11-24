// API Response Types
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

// User Types
export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  bio?: string;
  avatar_url?: string;
  banner_url?: string;
  is_active: boolean;
  is_superuser: boolean;
  mfa_enabled: boolean;
  created_at: string;
  updated_at: string;
}

// Auth Types
export interface LoginRequest {
  email: string;
  password: string;
  mfa_code?: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Task Types
export type TaskStatus = "TODO" | "IN_PROGRESS" | "DONE" | "ARCHIVED";
export type TaskPriority = "LOW" | "MEDIUM" | "HIGH" | "URGENT";

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_date?: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
  user_id: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  tags?: string[];
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  tags?: string[];
}

// Profile Types
export interface UserStats {
  account_age_days: number;
  total_tasks: number;
  active_sessions: number;
  last_login: string | null;
  created_at: string;
}

export interface UserSession {
  id: string;
  device_info: string;
  ip_address: string;
  last_activity: string | null;
  created_at: string;
  is_current: boolean;
}

export interface UserPasswordUpdate {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface UserUpdate {
  full_name?: string;
  username?: string;
  email?: string;
}
