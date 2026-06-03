import { Prisma } from "@prisma/client";
import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { parseJsonObjectBody } from "@/lib/http";
import { prisma } from "@/lib/prisma";
import {
  normalizeOptionalString,
  SupplierValidationError,
  validateSupplierPatchName,
} from "@/lib/suppliers";

type SupplierRouteContext = {
  params: Promise<{
    id: string;
  }>;
};

type UpdateSupplierBody = {
  name?: string;
  contactName?: string | null;
  contactEmail?: string | null;
  contactPhone?: string | null;
  address?: string | null;
};

export async function GET(request: NextRequest, context: SupplierRouteContext) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const { id } = await context.params;
  const supplier = await prisma.supplier.findUnique({ where: { id } });

  if (!supplier) {
    return NextResponse.json({ message: "Supplier not found." }, { status: 404 });
  }

  return NextResponse.json(supplier);
}

export async function PATCH(request: NextRequest, context: SupplierRouteContext) {
  const authorizationError = requireRole(request, ["ADMIN"]);

  if (authorizationError) {
    return authorizationError;
  }

  const { id } = await context.params;
  const parsedBody = await parseJsonObjectBody<UpdateSupplierBody>(request);

  if (parsedBody instanceof NextResponse) {
    return parsedBody;
  }

  const data: UpdateSupplierBody = {};

  try {
    const name = validateSupplierPatchName(parsedBody.name);
    if (name !== undefined) {
      data.name = name;
    }

    if (parsedBody.contactName !== undefined) {
      data.contactName = normalizeOptionalString(parsedBody.contactName);
    }

    if (parsedBody.contactEmail !== undefined) {
      data.contactEmail = normalizeOptionalString(parsedBody.contactEmail);
    }

    if (parsedBody.contactPhone !== undefined) {
      data.contactPhone = normalizeOptionalString(parsedBody.contactPhone);
    }

    if (parsedBody.address !== undefined) {
      data.address = normalizeOptionalString(parsedBody.address);
    }
  } catch (error) {
    if (error instanceof SupplierValidationError) {
      return NextResponse.json({ message: error.message }, { status: 400 });
    }

    throw error;
  }

  try {
    const supplier = await prisma.supplier.update({
      where: { id },
      data,
    });

    return NextResponse.json(supplier);
  } catch (error) {
    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2025") {
      return NextResponse.json({ message: "Supplier not found." }, { status: 404 });
    }

    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2002") {
      return NextResponse.json({ message: "Supplier with this name already exists." }, { status: 409 });
    }

    throw error;
  }
}

export async function DELETE(request: NextRequest, context: SupplierRouteContext) {
  const authorizationError = requireRole(request, ["ADMIN"]);

  if (authorizationError) {
    return authorizationError;
  }

  const { id } = await context.params;

  try {
    await prisma.supplier.delete({ where: { id } });
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2025") {
      return NextResponse.json({ message: "Supplier not found." }, { status: 404 });
    }

    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2003") {
      return NextResponse.json(
        { message: "Cannot delete supplier with related receipts." },
        { status: 409 },
      );
    }

    throw error;
  }
}
