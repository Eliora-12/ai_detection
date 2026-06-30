"use client";

import { ServerStatus } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface ServerCardProps {
  serverId: string;
  server: ServerStatus;
  onTrigger: (id: string, action: string) => void;
}

export default function ServerCard({ serverId, server, onTrigger }: ServerCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "ok": return "text-emerald-400";
      case "degraded": return "text-amber-400";
      case "down": return "text-rose-400";
      case "restarting": return "text-blue-400";
      case "draining": return "text-indigo-400";
      default: return "text-slate-400";
    }
  };

  return (
    <Card className="bg-slate-900 border-slate-800 hover:border-slate-700 transition-colors">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-lg font-mono tracking-tight">{serverId.toUpperCase()}</CardTitle>
        <Badge variant={server.status === 'ok' ? 'outline' : 'destructive'} className={getStatusColor(server.status)}>
          {server.status.toUpperCase()}
        </Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <p className="text-[10px] uppercase tracking-wider text-slate-500">CPU Load</p>
            <div className="flex items-center gap-2">
              <div className="flex-1 h-1 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500" style={{ width: `${server.cpu * 100}%` }} />
              </div>
              <span className="text-xs font-mono">{(server.cpu * 100).toFixed(0)}%</span>
            </div>
          </div>
          <div className="space-y-1">
            <p className="text-[10px] uppercase tracking-wider text-slate-500">Memory</p>
            <div className="flex items-center gap-2">
              <div className="flex-1 h-1 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500" style={{ width: `${server.memory * 100}%` }} />
              </div>
              <span className="text-xs font-mono">{(server.memory * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>

        {server.prediction && (
          <div className="p-3 rounded-lg bg-blue-500/5 border border-blue-500/10 space-y-2">
            <div className="flex justify-between items-center">
               <p className="text-[10px] uppercase tracking-wider text-blue-400 font-bold">AI Prediction</p>
               <Badge className="bg-blue-500/20 text-blue-400 border-0">
                 {server.prediction.confidence * 100}%
               </Badge>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">{server.prediction.explanation}</p>
            {server.prediction.recommended_action !== "none" && (
               <Button
                 size="sm"
                 variant="secondary"
                 className="w-full text-xs h-7 bg-blue-500 text-white hover:bg-blue-600"
                 onClick={() => onTrigger(serverId, server.prediction!.recommended_action)}
               >
                 Trigger {server.prediction.recommended_action.toUpperCase()}
               </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
