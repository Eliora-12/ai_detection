"use client";

import { useEffect, useState } from "react";
import { ServerStatus, SystemEvent, Prediction } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Activity, AlertTriangle, CheckCircle, Server, Zap, WifiOff } from "lucide-react";
import ServerCard from "@/components/dashboard/ServerCard";
import AlertBanner from "@/components/dashboard/AlertBanner";

export default function Dashboard() {
  const [servers, setServers] = useState<Record<string, ServerStatus>>({});
  const [events, setEvents] = useState<SystemEvent[]>([]);
  const [isOffline, setIsOffline] = useState(false);

  useEffect(() => {
    let eventSource: EventSource | null = null;

    const connect = () => {
      eventSource = new EventSource("/api/stream");

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "status") {
          setServers(data.servers);
          setIsOffline(false);
        } else if (data.type === "event") {
          setEvents((prev) => [data.event, ...prev].slice(0, 50));
        } else if (data.type === "error") {
          setIsOffline(true);
        }
      };

      eventSource.onerror = () => {
        setIsOffline(true);
        eventSource?.close();
        // Try to reconnect after 5 seconds
        setTimeout(connect, 5000);
      };
    };

    connect();
    return () => eventSource?.close();
  }, []);

  const triggerRecovery = async (serverId: string, action: string) => {
    await fetch("/api/trigger", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ server_id: serverId, action }),
    });
  };

  const predictions = Object.values(servers)
    .map(s => s.prediction)
    .filter((p): p is Prediction => !!p);

  return (
    <div className="space-y-8">
      {isOffline && (
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-4 flex items-center gap-3">
          <WifiOff className="h-5 w-5 text-amber-500" />
          <p className="text-sm font-medium text-amber-500">
            Backend services offline. Dashboard is in demo mode.
          </p>
        </div>
      )}

      <AlertBanner predictions={predictions} threshold={0.7} />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-400">Total Servers</p>
                <p className="text-2xl font-bold">{Object.keys(servers).length || 0}</p>
              </div>
              <Server className="h-8 w-8 text-blue-500 opacity-50" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-400">Healthy</p>
                <p className="text-2xl font-bold text-emerald-500">
                  {Object.values(servers).filter(s => s.status === 'ok').length}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-emerald-500 opacity-50" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-400">Degraded/Down</p>
                <p className="text-2xl font-bold text-rose-500">
                  {Object.values(servers).filter(s => s.status !== 'ok').length}
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-rose-500 opacity-50" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-400">Avg Confidence</p>
                <p className="text-2xl font-bold text-blue-400">
                   {Object.values(servers).length > 0
                     ? (Object.values(servers).reduce((acc, s) => acc + (s.prediction?.confidence || 0), 0) / Object.values(servers).length * 100).toFixed(0)
                     : 0}%
                </p>
              </div>
              <Zap className="h-8 w-8 text-blue-400 opacity-50" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(servers).length > 0 ? (
            Object.entries(servers).map(([id, s]) => (
              <ServerCard key={id} serverId={id} server={s} onTrigger={triggerRecovery} />
            ))
          ) : (
            <Card className="bg-slate-900 border-slate-800 col-span-full py-12 flex flex-col items-center justify-center text-slate-500">
               <Server className="h-12 w-12 mb-4 opacity-20" />
               <p className="text-sm font-mono uppercase tracking-widest">No Active Servers Found</p>
            </Card>
          )}
        </div>

        <Card className="bg-slate-900 border-slate-800 flex flex-col h-[500px]">
          <CardHeader className="border-b border-slate-800">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4 text-blue-500" />
              SYSTEM_EVENTS.LOG
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0 flex-1 overflow-hidden">
            <ScrollArea className="h-full">
              <div className="p-4 space-y-4">
                {events.length > 0 ? (
                  events.map((e, i) => (
                    <div key={i} className="space-y-1 font-mono text-[11px]">
                      <div className="flex items-center justify-between text-slate-500">
                        <span>[{new Date(e.timestamp).toLocaleTimeString()}]</span>
                        <span className="text-blue-400 uppercase tracking-tighter">{e.event_type}</span>
                      </div>
                      <p className="text-slate-300">
                        <span className="text-blue-500 font-bold">{e.source}:</span> {e.message}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-[10px] text-slate-600 font-mono italic">Waiting for events...</p>
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
