import assert from "node:assert/strict";
import test from "node:test";

import { ProductType } from "@prisma/client";

import {
  ProductValidationError,
  requireProductName,
  requireProductSku,
  requireProductType,
  requireProductUnit,
  validateOptionalBoolean,
  validatePatchProductType,
  validatePatchString,
} from "@/lib/products";

test("required product fields are trimmed", () => {
  assert.equal(requireProductSku("  SKU-1 "), "SKU-1");
  assert.equal(requireProductName("  Bolt  "), "Bolt");
  assert.equal(requireProductUnit("  pcs "), "pcs");
});

test("required product fields reject invalid values", () => {
  assert.throws(() => requireProductSku("   "), ProductValidationError);
  assert.throws(() => requireProductName(12), ProductValidationError);
  assert.throws(() => requireProductUnit(null), ProductValidationError);
});

test("product type validation accepts only enum values", () => {
  assert.equal(requireProductType(ProductType.COMPONENT), ProductType.COMPONENT);
  assert.equal(validatePatchProductType(ProductType.FINISHED), ProductType.FINISHED);
  assert.throws(() => requireProductType("RAW"), ProductValidationError);
});

test("patch string validation behavior", () => {
  assert.equal(validatePatchString(undefined, "Product name"), undefined);
  assert.equal(validatePatchString("  Name ", "Product name"), "Name");
  assert.throws(() => validatePatchString("   ", "Product name"), ProductValidationError);
  assert.throws(() => validatePatchString(123, "Product name"), ProductValidationError);
});

test("optional boolean validation behavior", () => {
  assert.equal(validateOptionalBoolean(undefined, "isActive"), undefined);
  assert.equal(validateOptionalBoolean(true, "isActive"), true);
  assert.throws(() => validateOptionalBoolean("true", "isActive"), ProductValidationError);
});
