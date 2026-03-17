/**
 * MetricsCard Component
 * Displays generation metrics in a visually appealing format
 */

interface MetricsCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  highlight?: boolean;
  suffix?: string;
}

export function MetricsCard({ label, value, icon, highlight = false, suffix }: MetricsCardProps) {
  return (
    <div
      className={`p-4 rounded-xl ${
        highlight
          ? "bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30"
          : "bg-slate-800/50 border border-slate-700/50"
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-slate-400 uppercase tracking-wide">{label}</span>
        {icon && <span className="text-slate-500">{icon}</span>}
      </div>
      <div className="flex items-baseline gap-1">
        <span
          className={`text-2xl font-bold ${
            highlight ? "text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400" : "text-white"
          }`}
        >
          {typeof value === "number" ? value.toLocaleString() : value}
        </span>
        {suffix && <span className="text-sm text-slate-500">{suffix}</span>}
      </div>
    </div>
  );
}

export default MetricsCard;
