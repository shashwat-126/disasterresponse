import { API_BASE_URL } from "./constants";

const API_ORIGIN = API_BASE_URL.replace(/\/api\/v1\/?$/, "");

/** Turn a server-stored upload path (e.g. an absolute filesystem path returned
 * by the API) into a URL the browser can actually fetch from /uploads/... */
export function fileUrl(path) {
  if (!path) return "";
  const normalized = path.replace(/\\/g, "/");
  const idx = normalized.indexOf("uploads/");
  const relative = idx >= 0 ? normalized.slice(idx) : normalized;
  return `${API_ORIGIN}/${relative}`;
}

export function fileNameOf(path) {
  if (!path) return "";
  return path.replace(/\\/g, "/").split("/").pop();
}

export function isImagePath(path) {
  return /\.(jpg|jpeg|png|webp)$/i.test(path || "");
}

export function isVideoPath(path) {
  return /\.(mp4|mov)$/i.test(path || "");
}
