import assert from "node:assert/strict";
import test from "node:test";

import {
  normalizeOptionalString,
  requireSupplierName,
  SupplierValidationError,
  validateSupplierPatchName,
} from "@/lib/suppliers";

test("requireSupplierName returns trimmed name", () => {
  assert.equal(requireSupplierName("  ACME  "), "ACME");
});

test("requireSupplierName throws for invalid type", () => {
  assert.throws(() => requireSupplierName(123), SupplierValidationError);
});

test("validateSupplierPatchName rejects empty values", () => {
  assert.throws(() => validateSupplierPatchName("   "), SupplierValidationError);
});

test("normalizeOptionalString rejects non string type", () => {
  assert.throws(() => normalizeOptionalString(123), SupplierValidationError);
});

test("normalizeOptionalString trims and nullifies empty string", () => {
  assert.equal(normalizeOptionalString("  hello  "), "hello");
  assert.equal(normalizeOptionalString("   "), null);
  assert.equal(normalizeOptionalString(null), null);
});
