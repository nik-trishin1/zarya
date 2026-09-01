export type LinkifySegment =
  | { type: "text"; value: string }
  | { type: "link"; value: string; href: string };

const URL_PATTERN = /(?:https?:\/\/|www\.)[^\s<>"{}|\\^`[\]]+/gi;
const TRAILING_PUNCTUATION = /[.,;:!?)]+$/;

function normalizeHref(raw: string): string | null {
  const trimmed = raw.replace(TRAILING_PUNCTUATION, "");
  const withScheme = trimmed.startsWith("www.") ? `https://${trimmed}` : trimmed;

  try {
    const parsed = new URL(withScheme);
    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
      return null;
    }
    return parsed.href;
  } catch {
    return null;
  }
}

export function linkifyText(text: string): LinkifySegment[] {
  const trimmed = text.trim();
  if (!trimmed) {
    return [];
  }

  const segments: LinkifySegment[] = [];
  let lastIndex = 0;

  for (const match of trimmed.matchAll(URL_PATTERN)) {
    const raw = match[0];
    const index = match.index ?? 0;
    const href = normalizeHref(raw);
    if (!href) {
      continue;
    }

    if (index > lastIndex) {
      segments.push({ type: "text", value: trimmed.slice(lastIndex, index) });
    }

    const withoutTrailing = raw.replace(TRAILING_PUNCTUATION, "");
    const trailing = raw.slice(withoutTrailing.length);
    segments.push({ type: "link", value: withoutTrailing, href });

    if (trailing) {
      segments.push({ type: "text", value: trailing });
    }

    lastIndex = index + raw.length;
  }

  if (lastIndex < trimmed.length) {
    segments.push({ type: "text", value: trimmed.slice(lastIndex) });
  }

  if (segments.length === 0) {
    return [{ type: "text", value: trimmed }];
  }

  return segments;
}
