"use client";

import { useTheme } from "next-themes";
import { Label } from "@/components/ui/label";
import { Moon, Sun, Monitor } from "lucide-react";

export function AppearanceSettings() {
  const { theme, setTheme } = useTheme();

  const themes = [
    { value: "light", label: "Light", icon: Sun, description: "Light mode" },
    { value: "dark", label: "Dark", icon: Moon, description: "Dark mode" },
    { value: "system", label: "System", icon: Monitor, description: "Follow system preference" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Appearance</h3>
        <p className="text-sm text-muted-foreground">
          Customize the appearance of the application
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <Label>Theme</Label>
          <p className="text-sm text-muted-foreground mb-3">
            Select your preferred color theme
          </p>
          <div className="grid grid-cols-3 gap-4">
            {themes.map((t) => (
              <button
                key={t.value}
                onClick={() => setTheme(t.value)}
                className={`relative flex flex-col items-center gap-3 p-4 rounded-lg border-2 transition-all hover:bg-accent ${
                  theme === t.value
                    ? "border-primary bg-accent"
                    : "border-border"
                }`}
              >
                <t.icon className={`h-6 w-6 ${theme === t.value ? "text-primary" : "text-muted-foreground"}`} />
                <div className="text-center">
                  <p className="font-medium text-sm">{t.label}</p>
                  <p className="text-xs text-muted-foreground">{t.description}</p>
                </div>
                {theme === t.value && (
                  <div className="absolute top-2 right-2 h-2 w-2 rounded-full bg-primary" />
                )}
              </button>
            ))}
          </div>
        </div>

        <div className="pt-4 border-t">
          <Label>Date Format</Label>
          <p className="text-sm text-muted-foreground mb-3">
            Choose how dates are displayed
          </p>
          <div className="space-y-2">
            {[
              { value: "MM/DD/YYYY", label: "MM/DD/YYYY (12/31/2024)" },
              { value: "DD/MM/YYYY", label: "DD/MM/YYYY (31/12/2024)" },
              { value: "YYYY-MM-DD", label: "YYYY-MM-DD (2024-12-31)" },
            ].map((format) => (
              <label
                key={format.value}
                className="flex items-center gap-3 p-3 rounded-md border cursor-pointer hover:bg-accent"
              >
                <input
                  type="radio"
                  name="date_format"
                  value={format.value}
                  defaultChecked={format.value === "MM/DD/YYYY"}
                  className="h-4 w-4"
                />
                <span className="text-sm">{format.label}</span>
              </label>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
