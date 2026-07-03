import { NextResponse } from 'next/server';
import { Prediction } from '@/lib/types';

export async function GET() {
  const monitorUrl = process.env.MONITOR_URL || 'http://localhost:5020';
  const aiUrl = process.env.AI_SERVICE_URL || 'http://localhost:5010';

  try {
    const [statusRes, predictionsRes] = await Promise.all([
      fetch(`${monitorUrl}/monitor/status`, { cache: 'no-store' }),
      fetch(`${aiUrl}/predictions/history`, { cache: 'no-store' })
    ]);

    if (!statusRes.ok) throw new Error('Monitor unreachable');

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
    return NextResponse.json({
      error: true,
      message: "Service unavailable. Backend services are not reachable.",
      service: "monitor"
    }, { status: 503 });
  }
}
