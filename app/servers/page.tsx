"use client";

import { useEffect, useState } from "react";
import { ServerStatus } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export default function ServersPage() {
  const [servers, setServers] = useState<Record<string, ServerStatus>>({});

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch("/api/status");
        if (res.ok) {
          const data = await res.json();
          setServers(data);
        }
      } catch (e) {}
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-blue-500">SERVER_INVENTORY</h1>

      <Card className="bg-slate-900 border-slate-800">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-slate-400 font-mono">ID</TableHead>
              <TableHead className="text-slate-400 font-mono">STATUS</TableHead>
              <TableHead className="text-slate-400 font-mono">CPU</TableHead>
              <TableHead className="text-slate-400 font-mono">MEM</TableHead>
              <TableHead className="text-slate-400 font-mono">LATENCY</TableHead>
              <TableHead className="text-slate-400 font-mono">ERRORS</TableHead>
              <TableHead className="text-slate-400 text-right font-mono">UPTIME</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {Object.entries(servers).map(([id, s]) => (
              <TableRow key={id} className="border-slate-800 hover:bg-slate-800/50">
                <TableCell className="font-mono font-bold text-blue-400 uppercase">{id}</TableCell>
                <TableCell>
                  <Badge variant={s.status === 'ok' ? 'outline' : 'destructive'} className="font-mono">
                    {s.status.toUpperCase()}
                  </Badge>
                </TableCell>
                <TableCell className="font-mono">{(s.cpu * 100).toFixed(1)}%</TableCell>
                <TableCell className="font-mono">{(s.memory * 100).toFixed(1)}%</TableCell>
                <TableCell className="font-mono">{s.latency_ms}ms</TableCell>
                <TableCell className="font-mono text-rose-400">{(s.error_rate * 100).toFixed(1)}%</TableCell>
                <TableCell className="text-right font-mono text-slate-500">{s.uptime_seconds}s</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
