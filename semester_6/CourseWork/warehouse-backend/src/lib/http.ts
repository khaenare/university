import { NextRequest, NextResponse } from "next/server";

export async function parseJsonObjectBody<T extends object>(
  request: NextRequest,
): Promise<T | NextResponse> {
  try {
    const body = await request.json();

    if (!body || typeof body !== "object" || Array.isArray(body)) {
      return NextResponse.json({ message: "JSON body must be an object." }, { status: 400 });
    }

    return body as T;
  } catch {
    return NextResponse.json({ message: "Invalid JSON body." }, { status: 400 });
  }
}
