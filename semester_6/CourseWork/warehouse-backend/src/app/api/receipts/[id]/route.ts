import { Prisma } from "@prisma/client";
import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { getProductStock, InventoryValidationError } from "@/lib/inventory";
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

export async function DELETE(request: NextRequest, context: ReceiptRouteContext) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const { id } = await context.params;

  try {
    const deleted = await prisma.$transaction(
      async (tx) => {
        const receipt = await tx.receipt.findUnique({
          where: { id },
          include: { lines: true },
        });

        if (!receipt) {
          return false;
        }

        for (const line of receipt.lines) {
          const currentStock = await getProductStock(tx, line.productId);
          if (currentStock.sub(line.quantity).isNegative()) {
            throw new InventoryValidationError(
              "Cannot delete receipt because related stock has already been consumed.",
            );
          }
        }

        await tx.inventoryTransaction.deleteMany({ where: { sourceDocument: `receipt:${id}` } });
        await tx.receipt.delete({ where: { id } });

        return true;
      },
      { isolationLevel: Prisma.TransactionIsolationLevel.Serializable },
    );

    if (!deleted) {
      return NextResponse.json({ message: "Receipt not found." }, { status: 404 });
    }

    return new NextResponse(null, { status: 204 });
  } catch (error) {
    if (error instanceof InventoryValidationError) {
      return NextResponse.json({ message: error.message }, { status: 400 });
    }

    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2025") {
      return NextResponse.json({ message: "Receipt not found." }, { status: 404 });
    }

    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2034") {
      return NextResponse.json(
        { message: "Receipt deletion conflicted with another stock operation. Please retry." },
        { status: 409 },
      );
    }

    throw error;
  }
}
