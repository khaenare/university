import assert from "node:assert/strict";
import test from "node:test";

import {
  ReceiptValidationError,
  requireInvoiceDate,
  requireReceiptId,
  requireReceiptLines,
} from "@/lib/receipts";

test("requireReceiptId validates and trims", () => {
  assert.equal(requireReceiptId("  abc  ", "ID"), "abc");
  assert.throws(() => requireReceiptId("", "ID"), ReceiptValidationError);
});

test("requireInvoiceDate validates ISO date string", () => {
  const date = requireInvoiceDate("2026-01-01T00:00:00.000Z");
  assert.equal(date.toISOString(), "2026-01-01T00:00:00.000Z");
  assert.throws(() => requireInvoiceDate("bad-date"), ReceiptValidationError);
  assert.throws(() => requireInvoiceDate("2026-01-01"), ReceiptValidationError);
});

test("requireReceiptLines validates line list", () => {
  const lines = requireReceiptLines([{ productId: "p-1", quantity: 2, purchasePrice: 10.5 }]);
  assert.equal(lines.length, 1);
  assert.throws(() => requireReceiptLines([]), ReceiptValidationError);
  assert.throws(
    () => requireReceiptLines([{ productId: "p-1", quantity: -1, purchasePrice: 10 }]),
    ReceiptValidationError,
  );
  assert.throws(
    () => requireReceiptLines([{ productId: "p-1", quantity: 1, purchasePrice: Number.POSITIVE_INFINITY }]),
    ReceiptValidationError,
  );
  assert.throws(
    () => requireReceiptLines([
      { productId: "p-1", quantity: 1, purchasePrice: 10 },
      { productId: "p-1", quantity: 2, purchasePrice: 10 },
    ]),
    ReceiptValidationError,
  );
});
