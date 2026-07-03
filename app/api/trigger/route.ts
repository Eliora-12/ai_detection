import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const recoveryUrl = process.env.RECOVERY_URL || 'http://localhost:5030';
  try {
    const body = await req.json();
    const res = await fetch(`${recoveryUrl}/recovery/trigger`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error('Recovery Manager unreachable');
    const data = await res.json();
    return NextResponse.json(data);
  } catch (e) {
    return NextResponse.json({
      error: true,
      message: "Service unavailable. Backend services are not reachable.",
      service: "recovery"
    }, { status: 503 });
  }
}
