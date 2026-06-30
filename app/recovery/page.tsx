"use client";

import { useEffect, useState } from "react";
import { RecoveryEvent } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export default function RecoveryPage() {
  const [history, setHistory] = useState<RecoveryEvent[]>([]);

  useEffect(() => {
    const fetchHistory = async () => {
      const res = await fetch("/api/recovery");
      if (res.ok) {
        const data = await res.json();
        setHistory([...data].reverse());
      }
    };
    fetchHistory();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-blue-500">RECOVERY_ACTION_LOG</h1>

      <Card className="bg-slate-900 border-slate-800">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-slate-400 font-mono">TIMESTAMP</TableHead>
              <TableHead className="text-slate-400 font-mono">SERVER</TableHead>
              <TableHead className="text-slate-400 font-mono">ACTION</TableHead>
              <TableHead className="text-slate-400 font-mono">OUTCOME</TableHead>
              <TableHead className="text-slate-400 font-mono">DURATION</TableHead>
              <TableHead className="text-slate-400 font-mono">MODE</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {history.map((h, i) => (
              <TableRow key={i} className="border-slate-800 hover:bg-slate-800/50">
                <TableCell className="text-xs text-slate-500 font-mono">
                  {new Date(h.timestamp).toLocaleString()}
                </TableCell>
                <TableCell className="font-mono font-bold text-blue-400 uppercase">{h.server_id}</TableCell>
                <TableCell className="uppercase font-mono text-xs">{h.action_taken}</TableCell>
                <TableCell>
                  <Badge className={h.outcome === 'success' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20 font-mono' : 'bg-rose-500/10 text-rose-500 border-rose-500/20 font-mono'}>
                    {h.outcome.toUpperCase()}
                  </Badge>
                </TableCell>
                <TableCell className="font-mono text-xs">{h.recovery_time_ms}ms</TableCell>
                <TableCell className="text-[10px] uppercase text-slate-500 font-mono">{h.auto_or_manual}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
