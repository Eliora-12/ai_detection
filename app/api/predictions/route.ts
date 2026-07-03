import { NextResponse } from 'next/server';

export async function GET() {
  const aiUrl = process.env.AI_SERVICE_URL || 'http://localhost:5010';
  try {
    const res = await fetch(`${aiUrl}/predictions/history`, { cache: 'no-store' });
    if (!res.ok) throw new Error('AI Service unreachable');
    const data = await res.json();
    return NextResponse.json(data);
  } catch (e) {
    return NextResponse.json({
      error: true,
      message: "Service unavailable. Backend services are not reachable.",
      service: "ai"
    }, { status: 503 });
  }
}
