import type { Event } from "../api/client";
import { CoverImage } from "./CoverImage";
import { formatEventDate } from "../utils/format";
import "./EventCard.css";

interface EventCardProps {
  event: Event;
  onClick: (event: Event) => void;
  completed?: boolean;
}

export function EventCard({ event, onClick, completed = false }: EventCardProps) {
  return (
    <button
      type="button"
      className={`event-card${completed ? " event-card--completed" : ""}`}
      onClick={() => onClick(event)}
    >
      <div className="event-card__image-wrap">
        <CoverImage url={event.cover_image_url} className="event-card__image" />
      </div>
      <div className="event-card__content">
        <time className="event-card__date">{formatEventDate(event.date, event.time)}</time>
        <h2 className="event-card__title">{event.name}</h2>
        <p className="event-card__location">{event.location}</p>
      </div>
      {!completed && event.is_registered && (
        <span className="event-card__badge" aria-label="Зарегистрирован">✅</span>
      )}
      {!completed && !event.is_registered && event.is_maybe && (
        <span className="event-card__badge event-card__badge--maybe" aria-label="Подумаю">
          …
        </span>
      )}
    </button>
  );
}
