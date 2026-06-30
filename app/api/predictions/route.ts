import { NextResponse } from 'next/server';

export async function GET() {
  const aiUrl = process.env.AI_SERVICE_URL || 'http://localhost:5010';
  try {
    const res = await fetch(`${aiUrl}/predictions/history`);
    const data = await res.json();
    return NextResponse.json(data);
  } catch (e) {
    return NextResponse.json([], { status: 500 });
  }
}
