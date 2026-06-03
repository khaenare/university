import assert from "node:assert/strict";
import test from "node:test";

import { ProductType } from "@prisma/client";

import { assertProductType, BomValidationError, requireBomItems, requireId } from "@/lib/bom";

test("requireId returns trimmed value", () => {
  assert.equal(requireId("  id-1  ", "Field"), "id-1");
});

test("requireId rejects invalid values", () => {
  assert.throws(() => requireId("  ", "Field"), BomValidationError);
  assert.throws(() => requireId(12, "Field"), BomValidationError);
});

test("requireBomItems validates list and uniqueness", () => {
  const items = requireBomItems([
    { componentId: "c-1", quantity: 2 },
    { componentId: "c-2", quantity: 1.5 },
  ]);

  assert.equal(items.length, 2);
  assert.throws(
    () => requireBomItems([{ componentId: "c-1", quantity: 1 }, { componentId: "c-1", quantity: 2 }]),
    BomValidationError,
  );
});

test("requireBomItems rejects invalid item payload", () => {
  assert.throws(() => requireBomItems([]), BomValidationError);
  assert.throws(() => requireBomItems([{ componentId: "x", quantity: 0 }]), BomValidationError);
  assert.throws(() => requireBomItems([{ componentId: "x", quantity: "1" }]), BomValidationError);
  assert.throws(() => requireBomItems([{ componentId: "x", quantity: Number.POSITIVE_INFINITY }]), BomValidationError);
  assert.throws(() => requireBomItems([{ componentId: "x", quantity: Number.NEGATIVE_INFINITY }]), BomValidationError);
});

test("assertProductType validates expected type", () => {
  assert.doesNotThrow(() => assertProductType(ProductType.COMPONENT, ProductType.COMPONENT, "Error"));
  assert.throws(
    () => assertProductType(ProductType.FINISHED, ProductType.COMPONENT, "Type mismatch"),
    BomValidationError,
  );
});
