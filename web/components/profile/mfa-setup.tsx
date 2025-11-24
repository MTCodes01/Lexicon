"use client";

import { useState } from "react";
import { useAuthStore } from "@/lib/auth-store";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { Shield, ShieldCheck, ShieldAlert, Copy, Check } from "lucide-react";

export function MFASetup() {
  const { user, fetchUser } = useAuthStore();
  const [isSettingUp, setIsSettingUp] = useState(false);
  const [qrCode, setQrCode] = useState<string | null>(null);
  const [secret, setSecret] = useState<string | null>(null);
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [verificationCode, setVerificationCode] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleEnableMFA = async () => {
    try {
      setIsSettingUp(true);
      const response = await apiClient.post<{
        secret: string;
        qr_code: string;
        backup_codes: string[];
      }>("/api/v1/auth/mfa/setup", {
        device_name: `Lexicon Web (${navigator.platform})`,
      });

      setQrCode(response.qr_code);
      setSecret(response.secret);
      setBackupCodes(response.backup_codes);
      toast.success("MFA setup initiated!");
    } catch (error: any) {
      console.error("MFA Setup Error:", error);
      let errorMessage = "Failed to setup MFA";
      if (error.response?.data?.detail) {
        errorMessage = typeof error.response.data.detail === "string" 
          ? error.response.data.detail 
          : JSON.stringify(error.response.data.detail);
      } else if (error.message) {
        errorMessage = error.message;
      }
      toast.error(errorMessage);
      setIsSettingUp(false);
    }
  };

  const handleVerifyMFA = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      toast.error("Please enter a valid 6-digit code");
      return;
    }

    try {
      setIsVerifying(true);
      await apiClient.post("/api/v1/auth/mfa/verify", {
        code: verificationCode,
      });

      toast.success("MFA enabled successfully! 🎉");
      await fetchUser();
      setIsSettingUp(false);
      setQrCode(null);
      setSecret(null);
      setVerificationCode("");
      setBackupCodes([]);
    } catch (error: any) {
      console.error("MFA Verification Error:", error);
      let errorMessage = "Invalid verification code";
      if (error.response?.data?.detail) {
        errorMessage = typeof error.response.data.detail === "string" 
          ? error.response.data.detail 
          : JSON.stringify(error.response.data.detail);
      } else if (error.message) {
        errorMessage = error.message;
      }
      toast.error(errorMessage);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleDisableMFA = async () => {
    const password = prompt("Enter your password to disable MFA:");
    if (!password) return;

    try {
      await apiClient.post("/api/v1/auth/mfa/disable", { password });
      toast.success("MFA disabled successfully");
      await fetchUser();
    } catch (error: any) {
      console.error("MFA Disable Error:", error);
      let errorMessage = "Failed to disable MFA";
      if (error.response?.data?.detail) {
        errorMessage = typeof error.response.data.detail === "string" 
          ? error.response.data.detail 
          : JSON.stringify(error.response.data.detail);
      } else if (error.message) {
        errorMessage = error.message;
      }
      toast.error(errorMessage);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success("Copied to clipboard!");
    setTimeout(() => setCopied(false), 2000);
  };

  if (isSettingUp && qrCode) {
    return (
      <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <div className="text-center space-y-4">
          <div className="inline-block p-4 bg-white dark:bg-gray-900 rounded-xl shadow-lg">
            <img src={qrCode} alt="MFA QR Code" className="w-64 h-64" />
          </div>
          <div className="max-w-md mx-auto space-y-3">
            <p className="text-sm text-muted-foreground">
              Scan this QR code with your authenticator app (Google Authenticator, Authy, 1Password, etc.)
            </p>
            <div className="relative group">
              <div className="p-3 bg-muted rounded-lg font-mono text-sm break-all">
                {secret}
              </div>
              <button
                onClick={() => copyToClipboard(secret || "")}
                className="absolute top-2 right-2 p-1.5 bg-background rounded hover:bg-accent transition-colors"
                title="Copy secret"
              >
                {copied ? (
                  <Check className="h-4 w-4 text-green-500" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>
        </div>

        {backupCodes.length > 0 && (
          <div className="p-4 bg-gradient-to-br from-yellow-500/10 via-orange-500/5 to-transparent border border-yellow-500/20 rounded-lg animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-start gap-3 mb-3">
              <ShieldAlert className="h-5 w-5 text-yellow-600 dark:text-yellow-500 mt-0.5" />
              <div>
                <h4 className="font-semibold text-yellow-600 dark:text-yellow-500">
                  Save Your Backup Codes
                </h4>
                <p className="text-sm text-muted-foreground mt-1">
                  Store these codes in a safe place. You can use them if you lose access to your authenticator app.
                </p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 font-mono text-sm mt-4">
              {backupCodes.map((code, idx) => (
                <div 
                  key={idx} 
                  className="p-2.5 bg-background rounded border hover:border-primary transition-colors cursor-pointer"
                  onClick={() => copyToClipboard(code)}
                >
                  {code}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="space-y-4">
          <Input
            label="Verification Code"
            type="text"
            placeholder="000000"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
            helperText="Enter the 6-digit code from your authenticator app"
            maxLength={6}
          />
          <div className="flex gap-3">
            <Button onClick={handleVerifyMFA} isLoading={isVerifying} disabled={verificationCode.length !== 6}>
              <ShieldCheck className="h-4 w-4 mr-2" />
              Verify & Enable
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setIsSettingUp(false);
                setQrCode(null);
                setSecret(null);
                setBackupCodes([]);
              }}
            >
              Cancel
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-4 p-4 rounded-lg border bg-gradient-to-br from-background to-muted/20 hover:shadow-md transition-all duration-300">
        <div className={`p-3 rounded-lg transition-all duration-300 ${
          user?.mfa_enabled 
            ? "bg-gradient-to-br from-green-500/20 to-emerald-500/20 shadow-lg shadow-green-500/10" 
            : "bg-muted"
        }`}>
          {user?.mfa_enabled ? (
            <ShieldCheck className="h-6 w-6 text-green-600 dark:text-green-400" />
          ) : (
            <ShieldAlert className="h-6 w-6 text-muted-foreground" />
          )}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-semibold">
              Two-Factor Authentication
            </h4>
            {user?.mfa_enabled && (
              <span className="px-2 py-0.5 bg-green-500/20 text-green-600 dark:text-green-400 text-xs font-medium rounded-full">
                Enabled
              </span>
            )}
          </div>
          <p className="text-sm text-muted-foreground">
            Add an extra layer of security to your account by requiring a code from your authenticator app when signing in.
          </p>
        </div>
      </div>

      {user?.mfa_enabled ? (
        <Button variant="destructive" onClick={handleDisableMFA} className="w-full sm:w-auto">
          <ShieldAlert className="h-4 w-4 mr-2" />
          Disable MFA
        </Button>
      ) : (
        <Button onClick={handleEnableMFA} className="w-full sm:w-auto bg-gradient-to-r from-primary to-purple-600 hover:from-primary/90 hover:to-purple-600/90">
          <Shield className="h-4 w-4 mr-2" />
          Enable MFA
        </Button>
      )}
    </div>
  );
}
