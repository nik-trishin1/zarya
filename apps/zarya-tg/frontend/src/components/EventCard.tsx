import type { Event } from "../api/client";
import { CoverImage } from "./CoverImage";
import { formatEventDate } from "../utils/format";
import { IconClock, IconPin } from "./icons";
import "./EventCard.css";

interface EventCardProps {
  event: Event;
  onClick: (event: Event) => void;
  completed?: boolean;
}

export function EventCard({ event, onClick, completed = false }: EventCardProps) {
  const showGoing = !completed && event.is_registered;
  const showMaybe = !completed && !event.is_registered && event.is_maybe;

  return (
    <button
      type="button"
      className={`event-card${completed ? " event-card--completed" : ""}`}
      onClick={() => onClick(event)}
    >
      <div className="event-card__thumb">
        <CoverImage url={event.cover_image_url} className="event-card__image" />
        {showGoing && <span className="event-card__status event-card__status--going">Иду</span>}
        {showMaybe && <span className="event-card__status event-card__status--maybe">Подумаю</span>}
      </div>
      <div className="event-card__body">
        <h2 className="event-card__title">{event.name}</h2>
        <div className="event-card__meta">
          <div className="event-card__meta-row">
            <IconClock size={14} />
            <span>{formatEventDate(event.date, event.time)}</span>
          </div>
          {event.location ? (
            <div className="event-card__meta-row">
              <IconPin size={14} />
              <span>{event.location}</span>
            </div>
          ) : null}
        </div>
      </div>
    </button>
  );
}
