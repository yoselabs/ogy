export function fit(blocks, width, height, maximum = 0.35) {
  if (!blocks.length) return { x: 20, y: 20, scale: maximum };
  const left = Math.min(...blocks.map((b) => b.x)),
    top = Math.min(...blocks.map((b) => b.y));
  const right = Math.max(...blocks.map((b) => b.x + b.w)),
    bottom = Math.max(...blocks.map((b) => b.y + b.h));
  const scale = Math.max(0.002, Math.min(maximum, (width - 40) / (right - left + 40), (height - 40) / (bottom - top + 40)));
  return { scale, x: width / 2 - ((left + right) * scale) / 2, y: height / 2 - ((top + bottom) * scale) / 2 };
}
