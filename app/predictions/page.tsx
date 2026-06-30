"use client";

import { useEffect, useState } from "react";
import { Prediction } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export default function PredictionsPage() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);

  useEffect(() => {
    const fetchHistory = async () => {
      const res = await fetch("/api/predictions");
      if (res.ok) {
        const data = await res.json();
        setPredictions([...data].reverse());
      }
    };
    fetchHistory();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-blue-500">AI_PREDICTION_HISTORY</h1>

      <Card className="bg-slate-900 border-slate-800">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-slate-400 font-mono">SERVER</TableHead>
              <TableHead className="text-slate-400 font-mono">FAULT_TYPE</TableHead>
              <TableHead className="text-slate-400 font-mono">CONFIDENCE</TableHead>
              <TableHead className="text-slate-400 font-mono">ACTION</TableHead>
              <TableHead className="text-slate-400 font-mono">EXPLANATION</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {predictions.map((p, i) => (
              <TableRow key={i} className="border-slate-800 hover:bg-slate-800/50">
                <TableCell className="font-mono font-bold text-blue-400 uppercase">{p.server_id}</TableCell>
                <TableCell>
                  <Badge variant={p.fault_type === 'healthy' ? 'outline' : 'destructive'} className="font-mono">
                    {p.fault_type.toUpperCase()}
                  </Badge>
                </TableCell>
                <TableCell className="font-mono">{(p.confidence * 100).toFixed(0)}%</TableCell>
                <TableCell>
                  <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20 uppercase text-[10px] font-mono">
                    {p.recommended_action}
                  </Badge>
                </TableCell>
                <TableCell className="text-xs text-slate-400 max-w-md font-mono">{p.explanation}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
