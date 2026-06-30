import { NextResponse } from 'next/server';
import { Prediction } from '@/lib/types';

export async function GET() {
  const monitorUrl = process.env.MONITOR_URL || 'http://localhost:5020';
  const aiUrl = process.env.AI_SERVICE_URL || 'http://localhost:5010';

  try {
    const [statusRes, predictionsRes] = await Promise.all([
      fetch(`${monitorUrl}/monitor/status`),
      fetch(`${aiUrl}/predictions/history`)
    ]);

    if (!statusRes.ok) return NextResponse.json({ error: 'Monitor unreachable' }, { status: 502 });

    const statuses = await statusRes.json();
    const predictions: Prediction[] = predictionsRes.ok ? await predictionsRes.json() : [];

    Object.keys(statuses).forEach(sid => {
      const latestPred = [...predictions].reverse().find((p) => p.server_id === sid);
      if (latestPred) {
        statuses[sid].prediction = latestPred;
      }
    });

    return NextResponse.json(statuses);
  } catch (e) {
    return NextResponse.json({ error: 'API Error' }, { status: 500 });
  }
}
