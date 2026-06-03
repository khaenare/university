import { Prisma } from "@prisma/client";
import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { parseJsonObjectBody } from "@/lib/http";
import { prisma } from "@/lib/prisma";
import { normalizeOptionalString, requireSupplierName, SupplierValidationError } from "@/lib/suppliers";

type CreateSupplierBody = {
  name?: string;
  contactName?: string | null;
  contactEmail?: string | null;
  contactPhone?: string | null;
  address?: string | null;
};

export async function GET(request: NextRequest) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const suppliers = await prisma.supplier.findMany({
    orderBy: { createdAt: "desc" },
  });

  return NextResponse.json(suppliers);
}

export async function POST(request: NextRequest) {
  const authorizationError = requireRole(request, ["ADMIN"]);

  if (authorizationError) {
    return authorizationError;
  }

  const parsedBody = await parseJsonObjectBody<CreateSupplierBody>(request);

  if (parsedBody instanceof NextResponse) {
    return parsedBody;
  }

  try {
    const name = requireSupplierName(parsedBody.name);

    const supplier = await prisma.supplier.create({
      data: {
        name,
        contactName: normalizeOptionalString(parsedBody.contactName),
        contactEmail: normalizeOptionalString(parsedBody.contactEmail),
        contactPhone: normalizeOptionalString(parsedBody.contactPhone),
        address: normalizeOptionalString(parsedBody.address),
      },
    });

    return NextResponse.json(supplier, { status: 201 });
  } catch (error) {
    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2002") {
      return NextResponse.json({ message: "Supplier with this name already exists." }, { status: 409 });
    }

    if (error instanceof SupplierValidationError) {
      return NextResponse.json({ message: error.message }, { status: 400 });
    }

    throw error;
  }
}
