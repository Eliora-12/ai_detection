import { NextResponse } from 'next/server';

export async function GET() {
  const recoveryUrl = process.env.RECOVERY_URL || 'http://localhost:5030';
  try {
    const res = await fetch(`${recoveryUrl}/recovery/log`);
    const data = await res.json();
    return NextResponse.json(data);
  } catch (e) {
    return NextResponse.json([], { status: 500 });
  }
}
