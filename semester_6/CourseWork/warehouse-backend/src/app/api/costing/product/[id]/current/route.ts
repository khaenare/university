import { ProductType } from "@prisma/client";
import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { calculateProductionCost, CostingValidationError } from "@/lib/costing";
import { prisma } from "@/lib/prisma";

type CostingRouteContext = {
  params: Promise<{ id: string }>;
};

export async function GET(request: NextRequest, context: CostingRouteContext) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const { id } = await context.params;

  try {
    const payload = await prisma.$transaction(async (tx) => {
      const product = await tx.product.findUnique({ where: { id } });
      if (!product) {
        return null;
      }

      if (product.type !== ProductType.FINISHED) {
        throw new CostingValidationError("Cost can be calculated only for FINISHED products.");
      }

      const bom = await tx.bom.findUnique({ where: { finishedProductId: id }, include: { items: true } });
      if (!bom || bom.items.length === 0) {
        throw new CostingValidationError("BOM for finished product is not configured.");
      }

      const componentIds = bom.items.map((item) => item.componentId);
      const components = await tx.product.findMany({ where: { id: { in: componentIds } } });

      if (components.length !== componentIds.length) {
        throw new CostingValidationError("One or more BOM components were not found.");
      }

      for (const component of components) {
        if (component.type !== ProductType.COMPONENT) {
          throw new CostingValidationError(
            `Product ${component.id} must have COMPONENT type to be used in costing.`,
          );
        }
      }

      const result = await calculateProductionCost(
        tx,
        bom.items.map((item) => ({ componentId: item.componentId, quantity: item.quantity })),
      );

      return {
        productId: id,
        totalCost: result.totalCost.toString(),
        unitCost: result.totalCost.toString(),
        quantityBase: "1",
        components: result.details.map((line) => ({
          componentId: line.componentId,
          quantity: line.quantity.toString(),
          averageUnitCost: line.averageUnitCost.toString(),
          lineCost: line.lineCost.toString(),
        })),
      };
    });

    if (!payload) {
      return NextResponse.json({ message: "Product not found." }, { status: 404 });
    }

    return NextResponse.json(payload);
  } catch (error) {
    if (error instanceof CostingValidationError) {
      return NextResponse.json({ message: error.message }, { status: 400 });
    }

    throw error;
  }
}
