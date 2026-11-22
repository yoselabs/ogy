// Fixed shelves in source order, independent of camera, selection and chrome.
export function pack(blocks, level) {
  const limit = level === "summary" ? 3600 : 9000,
    gap = level === "summary" ? 50 : 160;
  let x = 0,
    y = 0,
    height = 0;
  for (const block of blocks) {
    if (x && x + block.w > limit) {
      x = 0;
      y += height + gap;
      height = 0;
    }
    Object.assign(block, { x, y });
    x += block.w + gap;
    height = Math.max(height, block.h);
  }
  return blocks;
}
