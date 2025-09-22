async function generateAndCopyRandomText(len = 1_000_000) {
  const charset =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-={}[];:'\",.<>/?|\\`~";
  const chunkSize = 20_000; // build in chunks for responsiveness
  const pieces = [];
  let produced = 0;

  // Probability settings
  const SPACE_PCT = 12; // ~12% spaces
  const NEWLINE_PCT = 5; // ~5% line breaks

  // Fill a Uint32Array safely under the 65,536-byte per-call limit
  function getRandomU32(count) {
    const out = new Uint32Array(count);
    const MAX_ENTRIES_PER_CALL = 16384; // 16384 * 4 bytes = 65536
    for (let i = 0; i < count; i += MAX_ENTRIES_PER_CALL) {
      crypto.getRandomValues(
        out.subarray(i, Math.min(i + MAX_ENTRIES_PER_CALL, count)),
      );
    }
    return out;
  }

  while (produced < len) {
    const remain = len - produced;
    const n = Math.min(chunkSize, remain);

    // Two parallel random streams: one for deciding type, one for picking a char
    const rType = getRandomU32(n); // 4 bytes * n (chunked safely)
    const rIdx = getRandomU32(n); // 4 bytes * n (chunked safely)

    // Build a chunk
    const buf = new Array(n);
    for (let i = 0; i < n; i++) {
      const t = rType[i] % 100;
      if (t < SPACE_PCT) {
        buf[i] = " ";
      } else if (t < SPACE_PCT + NEWLINE_PCT) {
        buf[i] = "\n";
      } else {
        buf[i] = charset[rIdx[i] % charset.length];
      }
    }

    pieces.push(buf.join(""));
    produced += n;
  }

  const out = pieces.join("");

  async function copy(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
    // Fallback path
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.top = "-1000px";
    ta.style.left = "-1000px";
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try {
      return document.execCommand("copy");
    } finally {
      document.body.removeChild(ta);
    }
  }

  const copied = await copy(out);
  console.log(
    `Generated and ${copied ? "copied" : "failed to copy"} ${out.length.toLocaleString()} characters.`,
  );
  return out;
}

// Usage:
(async () => {
  await generateAndCopyRandomText();
})();
