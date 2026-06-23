import { getTelegramInitData, getTelegramWebApp, toAbsoluteUrl } from "../utils/telegram";

export interface Event {
  event_id: number;
  name: string;
  description: string;
  date: string;
  time: string;
  location: string;
  cover_image_url: string | null;
  registration_count: number;
  is_registered: boolean;
}

export interface RegistrationResponse {
  message: string;
  registration_count: number;
  is_registered: boolean;
}

function resolveApiBase(): string {
  const envUrl = import.meta.env.VITE_API_URL?.trim();
  if (envUrl) return envUrl;
  // Same origin: dev uses Vite proxy, production uses nginx proxy to backend
  return "";
}

const API_BASE = resolveApiBase();

function parseErrorDetail(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return String(detail[0].msg);
  return "Ошибка сервера";
}

function networkErrorMessage(): string {
  if (import.meta.env.DEV) {
    return "Не удалось подключиться к API. Убедитесь, что backend запущен: http://localhost:8000/health";
  }
  return "Не удалось подключиться к серверу";
}

function getInitData(): string {
  return getTelegramInitData();
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const initData = getInitData();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (initData) {
    headers["X-Telegram-Init-Data"] = initData;
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch {
    throw new Error(networkErrorMessage());
  }

  if (!response.ok) {
    const contentType = response.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
      throw new Error(
        "API вернул неверный ответ. Проверьте API_UPSTREAM на frontend (URL backend) и redeploy.",
      );
    }
    const error = await response.json().catch(() => ({ detail: "Ошибка сервера" }));
    throw new Error(parseErrorDetail(error.detail));
  }

  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    throw new Error(
      "API вернул неверный ответ. Проверьте API_UPSTREAM на frontend (URL backend) и redeploy.",
    );
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export async function fetchEvents(): Promise<Event[]> {
  return apiFetch<Event[]>("/api/events");
}

export async function fetchEvent(eventId: number): Promise<Event> {
  return apiFetch<Event>(`/api/events/${eventId}`);
}

export async function fetchMyRegistrations(): Promise<Event[]> {
  return apiFetch<Event[]>("/api/registrations/my");
}

export async function registerForEvent(eventId: number): Promise<RegistrationResponse> {
  return apiFetch<RegistrationResponse>(`/api/registrations/${eventId}`, { method: "POST" });
}

export async function cancelRegistration(eventId: number): Promise<RegistrationResponse> {
  return apiFetch<RegistrationResponse>(`/api/registrations/${eventId}`, { method: "DELETE" });
}

export async function downloadCalendar(eventId: number, _eventName: string): Promise<void> {
  const fileName = `zarya-event-${eventId}.ics`;
  const calendarPath = `/api/events/${eventId}/calendar`;

  const { token } = await apiFetch<{ token: string }>(
    `/api/registrations/${eventId}/calendar-token`,
  );

  const calendarUrl = `${window.location.origin}${calendarPath}?calendar_token=${encodeURIComponent(token)}`;

  const response = await fetch(calendarUrl);
  if (!response.ok) {
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      const error = await response.json().catch(() => ({ detail: "Ошибка сервера" }));
      throw new Error(parseErrorDetail(error.detail));
    }
    throw new Error("Не удалось скачать календарь");
  }

  const blob = await response.blob();
  const file = new File([blob], fileName, { type: "text/calendar" });

  if (navigator.canShare?.({ files: [file] })) {
    try {
      await navigator.share({ files: [file] });
      return;
    } catch {
      // User cancelled or share unavailable — try other methods
    }
  }

  const tg = getTelegramWebApp();
  const initData = getInitData();

  if (initData && typeof tg?.downloadFile === "function") {
    const downloadFile = tg.downloadFile;
    try {
      await new Promise<void>((resolve, reject) => {
        downloadFile({ url: calendarUrl, file_name: fileName }, (accepted: boolean) => {
          if (accepted) {
            resolve();
          } else {
            reject(new Error("Скачивание отменено"));
          }
        });
      });
      return;
    } catch {
      if (typeof tg.openLink === "function") {
        tg.openLink(calendarUrl);
        return;
      }
    }
  }

  if (initData && typeof tg?.openLink === "function") {
    tg.openLink(calendarUrl);
    return;
  }

  const objectUrl = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = objectUrl;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(objectUrl);
}

/** Same-origin absolute URL for uploaded covers; null → gradient placeholder. */
export function resolveCoverUrl(url: string | null | undefined): string | null {
  if (!url) return null;

  const trimmed = url.trim();
  let path: string | null = null;

  if (trimmed.startsWith("/uploads/")) {
    path = trimmed;
  } else {
    try {
      const parsed = new URL(trimmed);
      if (parsed.pathname.startsWith("/uploads/")) {
        path = parsed.pathname;
      }
    } catch {
      return null;
    }
  }

  return path ? toAbsoluteUrl(path) : null;
}
