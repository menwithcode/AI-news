import { NextRequest, NextResponse } from "next/server";
import { SignJWT } from "jose";
import bcrypt from "bcryptjs";

export async function POST(req: NextRequest) {
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
    return NextResponse.json({ error: "Invalid credentials" }, { status: 401 });
  }

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
