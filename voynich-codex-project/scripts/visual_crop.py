"""Shared real-image crop previews for the human Voynich tools."""
from __future__ import annotations

import html

VISUAL_CROP_CSS = """
    .visual-crop-grid { display: grid; gap: 8px; }
    .visual-crop-card { display: grid; gap: 6px; padding: 8px; border: 1px solid var(--line, #d7cabb); border-radius: 8px; background: #fffaf2; }
    .visual-crop-card.is-target { border-color: rgba(31, 118, 104, 0.58); background: #eef6f2; }
    .visual-crop-label { display: flex; align-items: center; justify-content: space-between; gap: 8px; color: var(--ink, #241f1a); font-size: 12px; font-weight: 900; line-height: 1.2; }
    .visual-crop-note { color: var(--muted, #6f675f); font-size: 12px; line-height: 1.28; }
    .visual-crop-canvas { display: block; width: 100%; min-height: 72px; height: auto; border: 1px solid rgba(55, 45, 35, 0.18); border-radius: 7px; background: #ece3d7; }
    .visual-crop-card[data-crop-status="erro"] .visual-crop-canvas { background: #f7e8e3; }
    .visual-crop-card[data-crop-status="erro"] .visual-crop-note::after { content: " Imagem nao carregou."; color: #8f3f33; font-weight: 800; }
""".rstrip()

VISUAL_CROP_JS = """
const cropImageCache = new Map();

function parseCropBox(value) {
  const parts = String(value || "").split(",").map(Number);
  if (parts.length !== 4 || parts.some((part) => !Number.isFinite(part))) return null;
  const [x1, y1, x2, y2] = parts;
  if (x2 <= x1 || y2 <= y1) return null;
  return [Math.max(0, x1), Math.max(0, y1), Math.min(100, x2), Math.min(100, y2)];
}

function cropBoxFromPoints(pointsText, verticalPad = 3.6, horizontalPad = 2.0) {
  const points = parsePoints(pointsText || "");
  if (!points || points.length < 2) return "";
  const xs = points.map(([x]) => x);
  const ys = points.map(([, y]) => y);
  const centerY = ys.reduce((total, y) => total + y, 0) / ys.length;
  const x1 = Math.max(0, Math.min(...xs) - horizontalPad);
  const x2 = Math.min(100, Math.max(...xs) + horizontalPad);
  const y1 = Math.max(0, centerY - verticalPad);
  const y2 = Math.min(100, centerY + verticalPad);
  if (x2 <= x1 || y2 <= y1) return "";
  return `${x1.toFixed(2)},${y1.toFixed(2)},${x2.toFixed(2)},${y2.toFixed(2)}`;
}

function loadCropImage(src) {
  if (!src) return Promise.reject(new Error("sem imagem"));
  if (cropImageCache.has(src)) return cropImageCache.get(src);
  const promise = new Promise((resolve, reject) => {
    const image = new Image();
    image.decoding = "async";
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error(`falha ao carregar ${src}`));
    image.src = src;
  });
  cropImageCache.set(src, promise);
  return promise;
}

async function paintCropCanvas(canvas) {
  const box = parseCropBox(canvas.dataset.boxPct);
  const src = canvas.dataset.imageSrc;
  const card = canvas.closest(".visual-crop-card");
  if (!box || !src) {
    if (card) card.dataset.cropStatus = "erro";
    return;
  }
  try {
    const image = await loadCropImage(src);
    const [x1, y1, x2, y2] = box;
    const sx = Math.max(0, Math.floor((x1 / 100) * image.naturalWidth));
    const sy = Math.max(0, Math.floor((y1 / 100) * image.naturalHeight));
    const sw = Math.max(1, Math.ceil(((x2 - x1) / 100) * image.naturalWidth));
    const sh = Math.max(1, Math.ceil(((y2 - y1) / 100) * image.naturalHeight));
    const targetWidth = Math.max(360, Math.min(1100, sw));
    const targetHeight = Math.max(58, Math.round(targetWidth * (sh / sw)));
    canvas.width = targetWidth;
    canvas.height = targetHeight;
    canvas.style.aspectRatio = `${targetWidth} / ${targetHeight}`;
    const ctx = canvas.getContext("2d");
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(image, sx, sy, sw, sh, 0, 0, targetWidth, targetHeight);
    ctx.strokeStyle = "rgba(31, 118, 104, 0.88)";
    ctx.lineWidth = 2;
    ctx.strokeRect(1, 1, targetWidth - 2, targetHeight - 2);
    ctx.strokeStyle = "rgba(231, 182, 87, 0.72)";
    ctx.setLineDash([8, 6]);
    ctx.beginPath();
    ctx.moveTo(0, targetHeight / 2);
    ctx.lineTo(targetWidth, targetHeight / 2);
    ctx.stroke();
    if (card) card.dataset.cropStatus = "ok";
  } catch (_error) {
    if (card) card.dataset.cropStatus = "erro";
  }
}

function paintCropPreviews(root = document) {
  for (const canvas of root.querySelectorAll("canvas[data-crop-preview]")) {
    paintCropCanvas(canvas);
  }
}
""".strip()


def parse_box_pct(value: str) -> tuple[float, float, float, float] | None:
    parts = value.split(",")
    if len(parts) != 4:
        return None
    try:
        x1, y1, x2, y2 = [float(part) for part in parts]
    except ValueError:
        return None
    if not (0 <= x1 <= 100 and 0 <= x2 <= 100 and 0 <= y1 <= 100 and 0 <= y2 <= 100):
        return None
    if x2 <= x1 or y2 <= y1:
        return None
    return x1, y1, x2, y2


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def box_text(box: tuple[float, float, float, float]) -> str:
    return ",".join(f"{value:.2f}" for value in box)


def box_from_zone(zone: dict[str, object]) -> tuple[float, float, float, float] | None:
    try:
        left = float(zone["left"])
        top = float(zone["top"])
        width = float(zone["width"])
        height = float(zone["height"])
    except (KeyError, TypeError, ValueError):
        return None
    return parse_box_pct(box_text((_clamp(left), _clamp(top), _clamp(left + width), _clamp(top + height))))


def baseline_box_from_points(
    points_text: str,
    vertical_pad: float = 3.6,
    horizontal_pad: float = 2.0,
) -> tuple[float, float, float, float] | None:
    points: list[tuple[float, float]] = []
    for pair in points_text.strip().split():
        if pair.count(",") != 1:
            return None
        raw_x, raw_y = pair.split(",", 1)
        try:
            x = float(raw_x)
            y = float(raw_y)
        except ValueError:
            return None
        if not (0 <= x <= 100 and 0 <= y <= 100):
            return None
        points.append((x, y))
    if len(points) < 2:
        return None
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    center_y = sum(ys) / len(ys)
    box = (
        _clamp(min(xs) - horizontal_pad),
        _clamp(center_y - vertical_pad),
        _clamp(max(xs) + horizontal_pad),
        _clamp(center_y + vertical_pad),
    )
    return box if box[2] > box[0] and box[3] > box[1] else None


def render_crop_canvas(
    image_src: str,
    box: tuple[float, float, float, float] | None,
    label: str,
    *,
    note: str = "",
    class_name: str = "",
    is_target: bool = False,
) -> str:
    if not image_src or not box:
        return ""
    classes = ["visual-crop-card"]
    if class_name:
        classes.append(class_name)
    if is_target:
        classes.append("is-target")
    note_html = f'<span class="visual-crop-note">{html.escape(note)}</span>' if note else ""
    return (
        f'<article class="{html.escape(" ".join(classes))}">'
        f'<span class="visual-crop-label">{html.escape(label)}</span>'
        f'<canvas class="visual-crop-canvas" data-crop-preview '
        f'data-image-src="{html.escape(image_src)}" '
        f'data-box-pct="{html.escape(box_text(box))}" '
        f'aria-label="{html.escape(label)}"></canvas>'
        f"{note_html}"
        "</article>"
    )
