import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { parseOptionalDate } from "@/lib/date";
import { prisma } from "@/lib/prisma";
import { parseOptionalLimit } from "@/lib/query";

export async function GET(request: NextRequest) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  try {
    const from = parseOptionalDate(request.nextUrl.searchParams.get("from"), "from");
    const to = parseOptionalDate(request.nextUrl.searchParams.get("to"), "to");
    const limit = parseOptionalLimit(request.nextUrl.searchParams.get("limit"));

    const where = {
      createdAt: {
        gte: from ?? undefined,
        lte: to ?? undefined,
      },
    };

    const snapshots = await prisma.costSnapshot.findMany({
      where,
      include: {
        finishedProduct: {
          select: {
            id: true,
            sku: true,
            name: true,
            unit: true,
          },
        },
        productionOrder: {
          select: {
            id: true,
            quantity: true,
          },
        },
      },
      orderBy: { createdAt: "desc" },
      take: limit,
    });

    return NextResponse.json({
      items: snapshots.map((snapshot) => ({
        snapshotId: snapshot.id,
        productionOrderId: snapshot.productionOrderId,
        finishedProduct: snapshot.finishedProduct,
        outputQuantity: snapshot.productionOrder.quantity.toString(),
        totalCost: snapshot.totalCost.toString(),
        unitCost: snapshot.unitCost.toString(),
        calculationData: snapshot.calculationData,
        createdAt: snapshot.createdAt,
      })),
    });
  } catch (error) {
    if (error instanceof Error && error.message.startsWith("Invalid '")) {
      return NextResponse.json({ message: error.message }, { status: 400 });
    }

    throw error;
  }
}
