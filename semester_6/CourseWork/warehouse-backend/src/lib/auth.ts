import crypto from "node:crypto";
import jwt from "jsonwebtoken";

import { UserRole } from "@prisma/client";

import { env } from "@/lib/env";

type AccessTokenPayload = {
  sub: string;
  role: UserRole;
  email: string;
};

type RefreshTokenPayload = {
  sub: string;
};

const ACCESS_TOKEN_EXPIRES_IN = "15m";
const REFRESH_TOKEN_EXPIRES_IN = "7d";

export function createAccessToken(payload: AccessTokenPayload): string {
  return jwt.sign(payload, env.jwtAccessSecret, { expiresIn: ACCESS_TOKEN_EXPIRES_IN });
}

export function createRefreshToken(payload: RefreshTokenPayload): string {
  return jwt.sign(payload, env.jwtRefreshSecret, { expiresIn: REFRESH_TOKEN_EXPIRES_IN });
}

export function verifyAccessToken(token: string): AccessTokenPayload {
  return jwt.verify(token, env.jwtAccessSecret, { algorithms: ["HS256"] }) as AccessTokenPayload;
}

export function verifyRefreshToken(token: string): RefreshTokenPayload {
  return jwt.verify(token, env.jwtRefreshSecret, { algorithms: ["HS256"] }) as RefreshTokenPayload;
}

export function hashToken(token: string): string {
  return crypto.createHash("sha256").update(token).digest("hex");
}
