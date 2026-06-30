"use client";

import { Prediction } from "@/lib/types";
import { AlertTriangle } from "lucide-react";

interface AlertBannerProps {
  predictions: Prediction[];
  threshold: number;
}

export default function AlertBanner({ predictions, threshold }: AlertBannerProps) {
  const alerts = predictions.filter(p => p.confidence >= threshold && p.fault_type !== 'healthy');

  if (alerts.length === 0) return null;

  return (
    <div className="bg-rose-500/10 border border-rose-500/20 rounded-lg p-4 mb-8">
      {alerts.map((a, i) => (
        <div key={i} className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-rose-500 mt-0.5 shrink-0" />
          <div>
            <p className="text-sm font-bold text-rose-500 uppercase tracking-tight">
              High Confidence Fault Predicted: {a.server_id.toUpperCase()}
            </p>
            <p className="text-xs text-slate-400">{a.explanation}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
