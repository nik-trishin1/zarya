import type { Event } from "../api/client";
import { getDefaultCoverUrl } from "../api/client";
import { formatEventDate } from "../utils/format";
import "./EventCard.css";

interface EventCardProps {
  event: Event;
  onClick: (event: Event) => void;
}

export function EventCard({ event, onClick }: EventCardProps) {
  const coverUrl = event.cover_image_url || getDefaultCoverUrl();

  return (
    <button type="button" className="event-card" onClick={() => onClick(event)}>
      <div className="event-card__image-wrap">
        <img src={coverUrl} alt="" className="event-card__image" loading="lazy" />
      </div>
      <div className="event-card__content">
        <time className="event-card__date">{formatEventDate(event.date, event.time)}</time>
        <h2 className="event-card__title">{event.name}</h2>
        <p className="event-card__location">{event.location}</p>
      </div>
      {event.is_registered && <span className="event-card__badge" aria-label="Зарегистрирован">✅</span>}
    </button>
  );
}
