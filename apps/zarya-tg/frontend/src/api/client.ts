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

const API_BASE =
  import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? "" : "http://localhost:8000");

function parseErrorDetail(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return String(detail[0].msg);
  return "Ошибка сервера";
}

function getInitData(): string {
  const tg = window.Telegram?.WebApp;
  return tg?.initData || "";
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

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Ошибка сервера" }));
    throw new Error(parseErrorDetail(error.detail));
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

export async function downloadCalendar(eventId: number, eventName: string): Promise<void> {
  const initData = getInitData();
  const response = await fetch(`${API_BASE}/api/events/${eventId}/calendar`, {
    headers: { "X-Telegram-Init-Data": initData },
  });

  if (!response.ok) {
    throw new Error("Не удалось скачать календарь");
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `zarya-${eventName.replace(/\s+/g, "-")}.ics`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function getDefaultCoverUrl(): string {
  return `${API_BASE}/static/default-cover.svg`;
}
