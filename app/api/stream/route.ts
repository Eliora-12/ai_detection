import { NextRequest } from 'next/server';
import { Prediction } from '@/lib/types';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  const encoder = new TextEncoder();
  const monitorUrl = process.env.MONITOR_URL || 'http://localhost:5020';
  const aiUrl = process.env.AI_SERVICE_URL || 'http://localhost:5010';

  const stream = new ReadableStream({
    async start(controller) {
      const send = (data: unknown) => {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
      };

      const interval = setInterval(async () => {
        try {
          const [statusRes, predictionsRes, faultsRes] = await Promise.all([
            fetch(`${monitorUrl}/monitor/status`),
            fetch(`${aiUrl}/predictions/history`),
            fetch(`${monitorUrl}/monitor/faults`)
          ]);

          if (statusRes.ok) {
            const statuses = await statusRes.json();
            const predictions: Prediction[] = predictionsRes.ok ? await predictionsRes.json() : [];

            Object.keys(statuses).forEach(sid => {
              const latestPred = [...predictions].reverse().find((p) => p.server_id === sid);
              if (latestPred) {
                statuses[sid].prediction = latestPred;
              }
            });
            send({ type: 'status', servers: statuses });
          }

          if (faultsRes.ok) {
            const faults = await faultsRes.json();
            if (faults.length > 0) {
              const latestFault = faults[faults.length - 1];
              send({ type: 'event', event: latestFault });
            }
          }
        } catch (e) {
          // Silent fail in stream
        }
      }, 3000);

      req.signal.addEventListener('abort', () => {
        clearInterval(interval);
        controller.close();
      });
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
