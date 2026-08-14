const RU_MONTHS = [
  "",
  "января",
  "февраля",
  "марта",
  "апреля",
  "мая",
  "июня",
  "июля",
  "августа",
  "сентября",
  "октября",
  "ноября",
  "декабря",
];

const RU_WEEKDAYS = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"];

const RU_MONTHS_SHORT = [
  "янв",
  "фев",
  "мар",
  "апр",
  "мая",
  "июн",
  "июл",
  "авг",
  "сен",
  "окт",
  "ноя",
  "дек",
];

function startOfLocalDay(date: Date): Date {
  const copy = new Date(date);
  copy.setHours(0, 0, 0, 0);
  return copy;
}

function parseEventCalendarDate(dateStr: string): Date {
  return new Date(`${dateStr}T00:00:00`);
}

/** Local calendar-day header: Сегодня / пт, Завтра / сб, 28 июн / сб. */
export function formatDayGroupHeader(dateStr: string): string {
  const eventDay = startOfLocalDay(parseEventCalendarDate(dateStr));
  const today = startOfLocalDay(new Date());
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  const weekday = RU_WEEKDAYS[eventDay.getDay()].toLowerCase();

  if (eventDay.getTime() === today.getTime()) {
    return `Сегодня / ${weekday}`;
  }
  if (eventDay.getTime() === tomorrow.getTime()) {
    return `Завтра / ${weekday}`;
  }
  return `${eventDay.getDate()} ${RU_MONTHS_SHORT[eventDay.getMonth()]} / ${weekday}`;
}

/** Group in API order. Headers only when the list spans 2+ distinct calendar days. */
export function groupEventsByCalendarDay<T extends { date: string }>(
  events: T[],
): { header: string | null; events: T[] }[] {
  const uniqueDates = new Set(events.map((event) => event.date));
  if (uniqueDates.size < 2) {
    return [{ header: null, events }];
  }

  const groups: { dateKey: string; header: string; events: T[] }[] = [];
  for (const event of events) {
    const last = groups[groups.length - 1];
    if (last && last.dateKey === event.date) {
      last.events.push(event);
    } else {
      groups.push({
        dateKey: event.date,
        header: formatDayGroupHeader(event.date),
        events: [event],
      });
    }
  }
  return groups.map(({ header, events: grouped }) => ({ header, events: grouped }));
}

export function formatEventDate(dateStr: string, timeStr: string): string {
  const date = new Date(dateStr + "T00:00:00");
  const weekday = RU_WEEKDAYS[date.getDay()];
  const month = RU_MONTHS[date.getMonth() + 1];
  const time = timeStr.slice(0, 5);
  return `${weekday}, ${date.getDate()} ${month}, ${time}`;
}

export function formatTime(timeStr: string): string {
  return timeStr.slice(0, 5);
}

/** Calendar date before today (same rule as backend list filter). */
export function isEventPast(dateStr: string): boolean {
  const today = new Date();
  const todayKey = [
    today.getFullYear(),
    String(today.getMonth() + 1).padStart(2, "0"),
    String(today.getDate()).padStart(2, "0"),
  ].join("-");
  return dateStr < todayKey;
}

export function hasGuestLimit(maxParticipants: number | null | undefined): boolean {
  return typeof maxParticipants === "number" && Number.isFinite(maxParticipants) && maxParticipants > 0;
}

/** Seats still available; unlimited events return Infinity. */
export function remainingSeats(
  registrationCount: number,
  maxParticipants: number | null | undefined,
): number {
  if (!hasGuestLimit(maxParticipants)) {
    return Number.POSITIVE_INFINITY;
  }
  return Math.max(0, (maxParticipants as number) - registrationCount);
}

export function canTakeSeats(
  registrationCount: number,
  maxParticipants: number | null | undefined,
  seatsNeeded: number,
): boolean {
  return remainingSeats(registrationCount, maxParticipants) >= seatsNeeded;
}

export function formatEventSeats(registrationCount: number, maxParticipants: number | null | undefined): string {
  if (hasGuestLimit(maxParticipants)) {
    return `Гостей: ${registrationCount} из ${maxParticipants} + Плюша`;
  }
  return `Гостей: ${registrationCount} + Плюша`;
}
