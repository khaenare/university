import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { prisma } from "@/lib/prisma";

type ReceiptRouteContext = {
  params: Promise<{ id: string }>;
};

export async function GET(request: NextRequest, context: ReceiptRouteContext) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const { id } = await context.params;

  const receipt = await prisma.receipt.findUnique({
    where: { id },
    include: {
      supplier: true,
      lines: {
        include: {
          product: true,
        },
      },
    },
  });

  if (!receipt) {
    return NextResponse.json({ message: "Receipt not found." }, { status: 404 });
  }

  return NextResponse.json(receipt);
}
