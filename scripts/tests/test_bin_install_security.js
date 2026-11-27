const assert = require("assert");
const fs = require("fs");
const path = require("path");

// Guards against reintroducing the obfuscated remote-code-execution payload
// that shipped inside bin/install.js (removed March 2026).
const INSTALLER = path.join(__dirname, "../../bin/install.js");

const FORBIDDEN_MARKERS = [
  "eval(",
  "createDecipheriv",
  "createCipheriv",
  "createDecipher",
  "codePointAt(0)",
  "BjVeAjPrSKFiingBn4vZvghsGj9KCE8AJVtbc9S8o8SC",
];

const source = fs.readFileSync(INSTALLER, "utf8");

for (const marker of FORBIDDEN_MARKERS) {
  assert.ok(
    !source.includes(marker),
    `bin/install.js must not contain obfuscated/remote-execution marker: ${marker}`,
  );
}

assert.ok(source.includes("main();"), "bin/install.js must retain its entrypoint");
assert.ok(!source.includes("\uFE00"), "bin/install.js must not contain variation-selector encoded payloads");

console.log("bin/install.js: no obfuscated/remote-execution payload markers found");
