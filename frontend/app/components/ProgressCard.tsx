/**
 * ProgressCard Component
 * Displays generation progress with visual feedback
 */

import { Loader2, Check, X } from "lucide-react";

interface ProgressCardProps {
  phase: string;
  message: string;
  progress: number;
  status?: "pending" | "active" | "completed" | "error";
}

export function ProgressCard({ phase, message, progress, status = "pending" }: ProgressCardProps) {
  const getStatusIcon = () => {
    switch (status) {
      case "completed":
        return <Check className="w-5 h-5 text-green-400" />;
      case "error":
        return <X className="w-5 h-5 text-red-400" />;
      case "active":
        return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />;
      default:
        return <div className="w-5 h-5 rounded-full bg-slate-600" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case "completed":
        return "border-green-500/50 bg-green-900/20";
      case "error":
        return "border-red-500/50 bg-red-900/20";
      case "active":
        return "border-blue-500/50 bg-blue-900/20";
      default:
        return "border-slate-700 bg-slate-800/50";
    }
  };

  return (
    <div className={`p-4 rounded-xl border ${getStatusColor()} transition-all duration-300`}>
      <div className="flex items-start gap-3">
        <div className="mt-0.5">{getStatusIcon()}</div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-white capitalize">{phase}</span>
            <span className="text-xs text-slate-400">{progress}%</span>
          </div>
          <p className="text-sm text-slate-400 mt-1">{message}</p>
          {status === "active" && (
            <div className="mt-2 h-1 bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ProgressCard;
