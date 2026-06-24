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
