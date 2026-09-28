// Minimal PNG decoder (8-bit grey/RGB/grey+alpha/RGBA, non-interlaced, filters
// 0-4) and per-frame luminance statistics for flash sampling and visual
// feedback detection. Uses node:zlib only.

import zlib from 'node:zlib';

const CHANNELS = { 0: 1, 2: 3, 4: 2, 6: 4 };
const MAX_PIXELS = 40_000_000;

function paeth(a, b, c) {
  const p = a + b - c;
  const pa = Math.abs(p - a);
  const pb = Math.abs(p - b);
  const pc = Math.abs(p - c);
  if (pa <= pb && pa <= pc) return a;
  if (pb <= pc) return b;
  return c;
}

/** Decode a PNG buffer into {width, height, channels, data (Uint8Array)}. */
export function decodePng(buf) {
  if (buf.length < 33 || buf.readUInt32BE(0) !== 0x89504e47 || buf.readUInt32BE(4) !== 0x0d0a1a0a) {
    throw new Error('not a PNG');
  }
  let pos = 8;
  let width = 0;
  let height = 0;
  let colorType = -1;
  const idat = [];
  while (pos + 8 <= buf.length) {
    const len = buf.readUInt32BE(pos);
    const type = buf.toString('latin1', pos + 4, pos + 8);
    const start = pos + 8;
    const end = start + len;
    if (end + 4 > buf.length) throw new Error('truncated PNG chunk');
    if (type === 'IHDR') {
      width = buf.readUInt32BE(start);
      height = buf.readUInt32BE(start + 4);
      const bitDepth = buf[start + 8];
      colorType = buf[start + 9];
      const interlace = buf[start + 12];
      if (bitDepth !== 8) throw new Error(`unsupported PNG bit depth ${bitDepth}`);
      if (!(colorType in CHANNELS)) throw new Error(`unsupported PNG color type ${colorType}`);
      if (interlace !== 0) throw new Error('interlaced PNG not supported');
      if (width <= 0 || height <= 0 || width * height > MAX_PIXELS) throw new Error('PNG dimensions out of range');
    } else if (type === 'IDAT') {
      idat.push(buf.subarray(start, end));
    } else if (type === 'IEND') {
      break;
    }
    pos = end + 4; // skip CRC
  }
  if (colorType < 0) throw new Error('PNG without IHDR');
  const channels = CHANNELS[colorType];
  const stride = width * channels;
  const raw = zlib.inflateSync(Buffer.concat(idat));
  if (raw.length < (stride + 1) * height) throw new Error('PNG image data too short');
  const out = new Uint8Array(stride * height);
  for (let y = 0; y < height; y++) {
    const filter = raw[y * (stride + 1)];
    const src = y * (stride + 1) + 1;
    const dst = y * stride;
    const prev = dst - stride;
    for (let x = 0; x < stride; x++) {
      const v = raw[src + x];
      const a = x >= channels ? out[dst + x - channels] : 0;
      const b = y > 0 ? out[prev + x] : 0;
      const c = x >= channels && y > 0 ? out[prev + x - channels] : 0;
      let r;
      switch (filter) {
        case 0: r = v; break;
        case 1: r = v + a; break;
        case 2: r = v + b; break;
        case 3: r = v + ((a + b) >> 1); break;
        case 4: r = v + paeth(a, b, c); break;
        default: throw new Error(`bad PNG filter ${filter}`);
      }
      out[dst + x] = r & 0xff;
    }
  }
  return { width, height, channels, data: out };
}

// sRGB 8-bit -> linear, and WCAG relative luminance.
const LIN = new Float64Array(256);
for (let i = 0; i < 256; i++) {
  const c = i / 255;
  LIN[i] = c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}

/**
 * Reduce a decoded image to per-pixel relative luminance and opaque RGB (alpha
 * composited over white). Returns {width, height, lum: Float32Array, rgb: Uint8Array}.
 */
export function frameFromImage(img) {
  const { width, height, channels, data } = img;
  const n = width * height;
  const lum = new Float32Array(n);
  const rgb = new Uint8Array(n * 3);
  for (let i = 0; i < n; i++) {
    const o = i * channels;
    let r;
    let g;
    let b;
    let a = 255;
    if (channels >= 3) {
      r = data[o]; g = data[o + 1]; b = data[o + 2];
      if (channels === 4) a = data[o + 3];
    } else {
      r = g = b = data[o];
      if (channels === 2) a = data[o + 1];
    }
    if (a < 255) {
      const f = a / 255;
      r = Math.round(r * f + 255 * (1 - f));
      g = Math.round(g * f + 255 * (1 - f));
      b = Math.round(b * f + 255 * (1 - f));
    }
    rgb[i * 3] = r; rgb[i * 3 + 1] = g; rgb[i * 3 + 2] = b;
    lum[i] = 0.2126 * LIN[r] + 0.7152 * LIN[g] + 0.0722 * LIN[b];
  }
  return { width, height, lum, rgb };
}

export const FLASH_DELTA = 0.1; // WCAG 2.3.1: 10% of max relative luminance
export const FLASH_DARK_LIMIT = 0.8; // darker state must be below 0.80

/**
 * Frame statistics. `prev` (same size) enables change metrics:
 *  - changed_fraction: share of pixels whose luminance changed by >= 0.10
 *  - flash_fraction:   same, restricted to WCAG general-flash pairs (darker < 0.80)
 *  - red_fraction:     share of saturated-red pixels (R/(R+G+B) >= 0.8) in this frame
 */
export function frameStats(frame, prev) {
  const n = frame.lum.length;
  let sum = 0;
  let red = 0;
  for (let i = 0; i < n; i++) {
    sum += frame.lum[i];
    const r = frame.rgb[i * 3];
    const s = r + frame.rgb[i * 3 + 1] + frame.rgb[i * 3 + 2];
    if (s > 0 && r / s >= 0.8) red++;
  }
  const out = { mean_luminance: n ? sum / n : 0, changed_fraction: 0, flash_fraction: 0, red_fraction: n ? red / n : 0 };
  if (prev && prev.lum.length === n && n) {
    let changed = 0;
    let flash = 0;
    for (let i = 0; i < n; i++) {
      const a = frame.lum[i];
      const b = prev.lum[i];
      if (Math.abs(a - b) >= FLASH_DELTA) {
        changed++;
        if (Math.min(a, b) < FLASH_DARK_LIMIT) flash++;
      }
    }
    out.changed_fraction = changed / n;
    out.flash_fraction = flash / n;
  }
  return out;
}

/**
 * Visual difference between two frames: share of pixels whose max RGB channel
 * difference is >= `level` (default 16/255). Returns null if sizes differ.
 */
export function visualDiffFraction(a, b, level = 16) {
  if (!a || !b || a.rgb.length !== b.rgb.length) return null;
  const n = a.rgb.length / 3;
  let changed = 0;
  for (let i = 0; i < n; i++) {
    const o = i * 3;
    const d = Math.max(
      Math.abs(a.rgb[o] - b.rgb[o]),
      Math.abs(a.rgb[o + 1] - b.rgb[o + 1]),
      Math.abs(a.rgb[o + 2] - b.rgb[o + 2]),
    );
    if (d >= level) changed++;
  }
  return n ? changed / n : 0;
}

// ---------------------------------------------------------------------------
// CSS-scale copy of a screenshot for fast Python analysis (conspicuity grid).
// Box-averages device pixels down by an integer factor near the DPR and writes a
// filter-0 RGB PNG (cheap to decode without native code).

const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();

function crc32(buf) {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function chunk(type, body) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(body.length);
  const tb = Buffer.concat([Buffer.from(type, 'ascii'), body]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(tb));
  return Buffer.concat([len, tb, crc]);
}

export function encodeRgbPng(width, height, rgb) {
  const raw = Buffer.alloc((width * 3 + 1) * height);
  for (let y = 0; y < height; y++) {
    raw[y * (width * 3 + 1)] = 0;
    rgb.copy ? rgb.copy(raw, y * (width * 3 + 1) + 1, y * width * 3, (y + 1) * width * 3)
      : raw.set(rgb.subarray(y * width * 3, (y + 1) * width * 3), y * (width * 3 + 1) + 1);
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8; ihdr[9] = 2; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk('IHDR', ihdr),
    chunk('IDAT', zlib.deflateSync(raw, { level: 6 })),
    chunk('IEND', Buffer.alloc(0)),
  ]);
}

export function cssScaleCopy(pngBuf, dpr) {
  const img = decodePng(pngBuf);
  const f = Math.max(1, Math.round(dpr));
  const ow = Math.max(1, Math.floor(img.width / f));
  const oh = Math.max(1, Math.floor(img.height / f));
  const ch = img.channels;
  const out = Buffer.alloc(ow * oh * 3);
  for (let oy = 0; oy < oh; oy++) {
    for (let ox = 0; ox < ow; ox++) {
      let r = 0, g = 0, b = 0;
      for (let dy = 0; dy < f; dy++) {
        const row = (oy * f + dy) * img.width;
        for (let dx = 0; dx < f; dx++) {
          const i = (row + ox * f + dx) * ch;
          if (ch >= 3) { r += img.data[i]; g += img.data[i + 1]; b += img.data[i + 2]; }
          else { r += img.data[i]; g += img.data[i]; b += img.data[i]; }
        }
      }
      const n = f * f;
      const o = (oy * ow + ox) * 3;
      out[o] = Math.round(r / n); out[o + 1] = Math.round(g / n); out[o + 2] = Math.round(b / n);
    }
  }
  return { width: ow, height: oh, factor: f, png: encodeRgbPng(ow, oh, out) };
}

