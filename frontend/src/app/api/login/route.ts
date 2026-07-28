import { NextRequest, NextResponse } from "next/server";
import { SignJWT } from "jose";
import bcrypt from "bcryptjs";
import {
  clearLoginAttempts,
  isLoginRateLimited,
  recordFailedLogin,
} from "@/lib/db";

function getClientIp(req: NextRequest): string {
  const forwarded = req.headers.get("x-forwarded-for");
  return forwarded ? forwarded.split(",")[0].trim() : "unknown";
}

export async function POST(req: NextRequest) {
  const ip = getClientIp(req);

  if (await isLoginRateLimited(ip)) {
    return NextResponse.json(
      { error: "Too many attempts. Try again later." },
      { status: 429 }
    );
  }

  const { username, password } = await req.json();

  const passwordHash = Buffer.from(
    process.env.ADMIN_PASSWORD_HASH_B64 ?? "",
    "base64"
  ).toString("utf-8");

  const validUsername = username === process.env.ADMIN_USERNAME;
  const validPassword =
    typeof password === "string" &&
    passwordHash.length > 0 &&
    (await bcrypt.compare(password, passwordHash));

  if (!validUsername || !validPassword) {
    await recordFailedLogin(ip);
    return NextResponse.json({ error: "Invalid credentials" }, { status: 401 });
  }

  await clearLoginAttempts(ip);

  const secret = new TextEncoder().encode(process.env.SESSION_SECRET);
  const token = await new SignJWT({ sub: username })
    .setProtectedHeader({ alg: "HS256" })
    .setExpirationTime("7d")
    .sign(secret);

  const response = NextResponse.json({ ok: true });
  response.cookies.set("session", token, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });
  return response;
}
