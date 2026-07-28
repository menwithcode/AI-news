import { NextRequest, NextResponse } from "next/server";
import { savePushSubscription } from "@/lib/db";

export async function POST(req: NextRequest) {
  const body = await req.json();

  const endpoint = body?.endpoint;
  const p256dh = body?.keys?.p256dh;
  const auth = body?.keys?.auth;

  if (!endpoint || !p256dh || !auth) {
    return NextResponse.json({ error: "Invalid subscription" }, { status: 400 });
  }

  await savePushSubscription({ endpoint, p256dh, auth });
  return NextResponse.json({ ok: true });
}
