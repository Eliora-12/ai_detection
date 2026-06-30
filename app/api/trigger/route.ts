import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const recoveryUrl = process.env.RECOVERY_URL || 'http://localhost:5030';
  const body = await req.json();
  try {
    const res = await fetch(`${recoveryUrl}/recovery/trigger`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    return NextResponse.json(data);
  } catch (e) {
    return NextResponse.json({ error: 'Recovery manager unreachable' }, { status: 502 });
  }
}
