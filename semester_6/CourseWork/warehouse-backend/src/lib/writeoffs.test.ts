import assert from "node:assert/strict";
import test from "node:test";

import {
  requireWriteOffLines,
  requireWriteOffReason,
  WriteOffValidationError,
} from "@/lib/writeoffs";

test("requireWriteOffReason accepts valid reasons", () => {
  assert.equal(requireWriteOffReason("SALE"), "SALE");
});

test("requireWriteOffReason rejects invalid values", () => {
  assert.throws(() => requireWriteOffReason("OTHER"), WriteOffValidationError);
  assert.throws(() => requireWriteOffReason("PRODUCTION"), WriteOffValidationError);
});

test("requireWriteOffLines validates and normalizes lines", () => {
  const lines = requireWriteOffLines([{ productId: " p-1 ", quantity: 2 }]);
  assert.equal(lines.length, 1);
  assert.equal(lines[0].productId, "p-1");
  assert.throws(() => requireWriteOffLines([]), WriteOffValidationError);
  assert.throws(() => requireWriteOffLines([{ productId: "p-1", quantity: 0 }]), WriteOffValidationError);
  assert.throws(
    () => requireWriteOffLines([{ productId: "p-1", quantity: 1 }, { productId: "p-1", quantity: 2 }]),
    WriteOffValidationError,
  );
});
