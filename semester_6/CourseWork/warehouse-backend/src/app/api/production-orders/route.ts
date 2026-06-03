import { Prisma, ProductType, TransactionType } from "@prisma/client";
import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { parseJsonObjectBody } from "@/lib/http";
import { calculateProductionCost, CostingValidationError } from "@/lib/costing";
import { assertSufficientStock, InventoryValidationError } from "@/lib/inventory";
import { prisma } from "@/lib/prisma";
import {
  ProductionOrderValidationError,
  requireProductionProductId,
  requireProductionQuantity,
} from "@/lib/production-orders";

type CreateProductionOrderBody = {
  finishedProductId?: string;
  quantity?: number;
};

export async function GET(request: NextRequest) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const orders = await prisma.productionOrder.findMany({
    include: {
      finishedProduct: true,
      items: {
        include: {
          component: true,
        },
      },
    },
    orderBy: { createdAt: "desc" },
  });

  return NextResponse.json(orders);
}

export async function POST(request: NextRequest) {
  const authorizationError = requireRole(request, ["ADMIN", "MANAGER"]);

  if (authorizationError) {
    return authorizationError;
  }

  const parsedBody = await parseJsonObjectBody<CreateProductionOrderBody>(request);
  if (parsedBody instanceof NextResponse) {
    return parsedBody;
  }

  try {
    const finishedProductId = requireProductionProductId(parsedBody.finishedProductId);
    const quantity = requireProductionQuantity(parsedBody.quantity);
    const outputQuantity = new Prisma.Decimal(quantity);

    const createdOrder = await prisma.$transaction(
      async (tx) => {
        const finishedProduct = await tx.product.findUnique({ where: { id: finishedProductId } });
        if (!finishedProduct) {
          throw new ProductionOrderValidationError("Finished product not found.");
        }

        if (finishedProduct.type !== ProductType.FINISHED) {
          throw new ProductionOrderValidationError("Target product must have FINISHED type.");
        }

        const bom = await tx.bom.findUnique({
          where: { finishedProductId },
          include: { items: true },
        });

        if (!bom || bom.items.length === 0) {
          throw new ProductionOrderValidationError("BOM for finished product is not configured.");
        }

        const consumptionLines = bom.items.map((item) => ({
          componentId: item.componentId,
          quantity: item.quantity.mul(outputQuantity),
        }));

        const componentIds = consumptionLines.map((line) => line.componentId);
        const components = await tx.product.findMany({
          where: { id: { in: componentIds } },
        });

        if (components.length !== componentIds.length) {
          throw new ProductionOrderValidationError("One or more BOM components were not found.");
        }

        for (const component of components) {
          if (component.type !== ProductType.COMPONENT) {
            throw new ProductionOrderValidationError(
              `Product ${component.id} must have COMPONENT type to be consumed in production.`,
            );
          }
        }

        for (const line of consumptionLines) {
          await assertSufficientStock(tx, line.componentId, line.quantity);
        }

        const costResult = await calculateProductionCost(tx, consumptionLines);
        const unitCost = costResult.totalCost.div(outputQuantity);

        const order = await tx.productionOrder.create({
          data: {
            finishedProductId,
            quantity: outputQuantity,
            items: {
              create: consumptionLines.map((line) => ({
                componentId: line.componentId,
                quantity: line.quantity,
              })),
            },
          },
        });

        await tx.inventoryTransaction.create({
          data: {
            productId: finishedProductId,
            type: TransactionType.PRODUCTION_OUTPUT,
            quantity: outputQuantity,
            unitCost,
            sourceDocument: `production:${order.id}`,
          },
        });

        await tx.inventoryTransaction.createMany({
          data: consumptionLines.map((line) => ({
            productId: line.componentId,
            type: TransactionType.ISSUE_PRODUCTION,
            quantity: line.quantity.negated(),
            unitCost: null,
            sourceDocument: `production:${order.id}`,
          })),
        });

        await tx.costSnapshot.create({
          data: {
            productionOrderId: order.id,
            finishedProductId,
            totalCost: costResult.totalCost,
            unitCost,
            calculationData: {
              outputQuantity: outputQuantity.toString(),
              components: costResult.details.map((item) => ({
                componentId: item.componentId,
                quantity: item.quantity.toString(),
                averageUnitCost: item.averageUnitCost.toString(),
                lineCost: item.lineCost.toString(),
              })),
            },
          },
        });

        return tx.productionOrder.findUnique({
          where: { id: order.id },
          include: {
            finishedProduct: true,
            items: {
              include: {
                component: true,
              },
            },
          },
        });
      },
      { isolationLevel: Prisma.TransactionIsolationLevel.Serializable },
    );

    return NextResponse.json(createdOrder, { status: 201 });
  } catch (error) {
    if (
      error instanceof ProductionOrderValidationError ||
      error instanceof InventoryValidationError ||
      error instanceof CostingValidationError
    ) {
      return NextResponse.json({ message: error.message }, { status: 400 });
    }

    throw error;
  }
}
