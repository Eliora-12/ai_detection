import { NextResponse } from 'next/server';

export async function GET() {
  const recoveryUrl = process.env.RECOVERY_URL || 'http://localhost:5030';
  try {
    const res = await fetch(`${recoveryUrl}/recovery/log`, { cache: 'no-store' });
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
