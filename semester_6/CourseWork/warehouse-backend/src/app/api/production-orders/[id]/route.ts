import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { prisma } from "@/lib/prisma";

type ProductionOrderRouteContext = {
  params: Promise<{ id: string }>;
};

export async function GET(request: NextRequest, context: ProductionOrderRouteContext) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const { id } = await context.params;

  const order = await prisma.productionOrder.findUnique({
    where: { id },
    include: {
      finishedProduct: true,
      items: {
        include: {
          component: true,
        },
      },
    },
  });

  if (!order) {
    return NextResponse.json({ message: "Production order not found." }, { status: 404 });
  }

  return NextResponse.json(order);
}
