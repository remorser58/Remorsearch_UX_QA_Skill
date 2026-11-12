// Owned synthetic uploads only. This module never opens a path or accepts bytes
// from an action. A reviewed host supplies the in-memory registry separately.
import { ActionError, sha256 } from './util.mjs';

export const UPLOAD_LIMITS = Object.freeze({ files: 16, fileBytes: 16 * 1024 * 1024,
  totalBytes: 32 * 1024 * 1024, timeoutMs: 5000 });

export class OwnedUploadError extends Error {
  constructor(code) { super(code); this.name = 'OwnedUploadError'; this.code = code; }
}

export function uploadFileIds(value, where = 'upload.files') {
  if (!Array.isArray(value) || value.length < 1 || value.length > UPLOAD_LIMITS.files
    || !value.every(id => typeof id === 'string' && /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(id))
    || new Set(value).size !== value.length) {
    throw new ActionError(`${where} must contain 1..${UPLOAD_LIMITS.files} unique owned fixture identifiers`);
  }
  return [...value];
}

function refused(code) { throw new OwnedUploadError(code); }

function safeName(name) {
  return typeof name === 'string' && name.length > 0 && Buffer.byteLength(name, 'utf8') <= 255
    && name.trim() === name && name !== '.' && name !== '..'
    && !/[/\\:\u0000-\u001f\u007f]/.test(name);
}

function safeMime(value) {
  return typeof value === 'string' && value.length <= 127
    && /^[a-z0-9][a-z0-9!#$&^_.+-]*\/[a-z0-9][a-z0-9!#$&^_.+-]*$/.test(value);
}

/** Validate all selected entries before copying any bytes or interacting with a page. */
export function prepareOwnedUpload(action, registry) {
  if (!(registry instanceof Map)) refused('upload_registry_required');
  const ids = uploadFileIds(action.files);
  const timeoutMs = action.timeout_ms ?? UPLOAD_LIMITS.timeoutMs;
  if (!Number.isInteger(timeoutMs) || timeoutMs < 1 || timeoutMs > UPLOAD_LIMITS.timeoutMs) refused('upload_timeout_invalid');
  if (typeof action.input !== 'string' || !action.input.trim() || typeof action.target !== 'string' || !action.target.trim()) refused('upload_selectors_invalid');
  const entries = [];
  let total = 0;
  for (const id of ids) {
    const entry = registry.get(id);
    if (!entry || typeof entry !== 'object' || Array.isArray(entry)
      || ![Object.prototype, null].includes(Object.getPrototypeOf(entry))
      || Object.keys(entry).sort().join(',') !== 'buffer,mimeType,name,sha256'
      || !safeName(entry.name) || !safeMime(entry.mimeType) || !Buffer.isBuffer(entry.buffer)
      || typeof entry.sha256 !== 'string' || !/^[a-f0-9]{64}$/.test(entry.sha256)) refused('upload_fixture_invalid');
    if (entry.buffer.length > UPLOAD_LIMITS.fileBytes) refused('upload_file_bytes_exceeded');
    total += entry.buffer.length;
    if (total > UPLOAD_LIMITS.totalBytes) refused('upload_total_bytes_exceeded');
    entries.push({ id, entry });
  }
  // Buffer copies detach the selected bytes from subsequent registry mutation.
  const files = entries.map(({ id, entry }) => {
    const buffer = Buffer.from(entry.buffer);
    if (sha256(buffer) !== entry.sha256) refused('upload_fixture_sha256_mismatch');
    return { id, name: entry.name, mimeType: entry.mimeType, buffer, sha256: entry.sha256 };
  });
  return { timeoutMs, files,
    evidence: { method: 'playwright_filechooser', input: action.input,
      files: files.map(({ id, name, mimeType, buffer, sha256: digest }) =>
        ({ id, name, mime_type: mimeType, size_bytes: buffer.length, sha256: digest })) } };
}

/**
 * Click the observed control using the driver's normal pointer dispatch. The
 * headless filechooser is intercepted; this does not exercise an OS file dialog.
 * All page/Playwright errors become fixed codes, never paths or selected bytes.
 */
export async function chooseOwnedFiles({ page, action, registry, point, click }) {
  const prepared = prepareOwnedUpload(action, registry);
  if (!point || !Number.isFinite(point.x) || !Number.isFinite(point.y) || typeof click !== 'function') refused('upload_target_invalid');
  let controls;
  try {
    controls = await page.evaluate(({ target, input, point, count }) => {
      const targets = document.querySelectorAll(target);
      const inputs = document.querySelectorAll(input);
      if (targets.length !== 1 || inputs.length !== 1) return { target: false, input: false };
      const button = targets[0], field = inputs[0];
      const rect = button.getBoundingClientRect();
      let visible = !button.closest('[hidden]')
        && button.checkVisibility({ opacityProperty: true, visibilityProperty: true });
      for (let ancestor = button; visible && ancestor; ancestor = ancestor.parentElement) {
        const style = getComputedStyle(ancestor);
        if (style.display === 'none' || style.visibility !== 'visible' || !(Number(style.opacity) > 0)) visible = false;
      }
      const hit = document.elementFromPoint(point.x, point.y);
      return {
        target: visible && button.isConnected && rect.width > 0 && rect.height > 0
          && !button.matches(':disabled') && button.getAttribute('aria-disabled') !== 'true'
          && (button === hit || button.contains(hit)),
        input: field.isConnected && field.tagName === 'INPUT' && field.type === 'file'
          && !field.matches(':disabled') && !field.webkitdirectory && (count === 1 || field.multiple),
      };
    }, { target: action.target, input: action.input, point, count: prepared.files.length });
  } catch { refused('upload_controls_unavailable'); }
  if (!controls?.target) refused('upload_target_invalid');
  if (!controls?.input) refused('upload_input_invalid');

  const deadline = Date.now() + prepared.timeoutMs;
  const remaining = () => {
    const ms = deadline - Date.now();
    if (ms < 1) refused('upload_timeout');
    return ms;
  };
  let pending;
  try {
    // Install the listener before native pointer input. Convert rejection now so
    // a failed click cannot leave an unhandled chooser timeout rejection.
    pending = page.waitForEvent('filechooser', { timeout: remaining() })
      .then(chooser => ({ chooser }), () => ({ failed: true }));
  } catch { refused('upload_chooser_unavailable'); }
  try { await click(); }
  catch {
    await pending; // waitForEvent removes its own bounded listener on completion
    refused('upload_click_failed');
  }
  const { chooser, failed } = await pending;
  if (failed || !chooser) refused('upload_chooser_timeout');
  let element;
  try {
    if (chooser.page() !== page) refused('upload_chooser_input_mismatch');
    element = chooser.element();
    const matches = await page.evaluate(({ input, selector, count }) => {
      const found = document.querySelectorAll(selector);
      return found.length === 1 && found[0] === input && input.ownerDocument === document
        && input.isConnected && input.tagName === 'INPUT' && input.type === 'file'
        && !input.matches(':disabled') && !input.webkitdirectory && (count === 1 || input.multiple);
    }, { input: element, selector: action.input, count: prepared.files.length });
    if (!matches) refused('upload_chooser_input_mismatch');
    await chooser.setFiles(prepared.files.map(({ name, mimeType, buffer }) => ({ name, mimeType, buffer })),
      { timeout: remaining() });
  } catch (error) {
    if (error instanceof OwnedUploadError) throw error;
    refused('upload_selection_failed');
  } finally {
    if (element) await element.dispose().catch(() => {});
  }
  // setFiles acceptance is input evidence, not proof that the product imported it.
  return prepared.evidence;
}
