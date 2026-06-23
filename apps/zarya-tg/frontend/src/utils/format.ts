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
