import type { Event } from "../api/client";
import { formatEventDate, formatEventSeats } from "../utils/format";
import { IconClock, IconPin, IconTag, IconUsers } from "./icons";
import { LinkifiedText } from "./LinkifiedText";

interface EventDetailsHeaderProps {
  event: Event;
}

/** Title, fact rows, and description inside `.event-details__body`. */
export function EventDetailsHeader({ event }: EventDetailsHeaderProps) {
  return (
    <>
      <h2 className="event-details__title">{event.name}</h2>

      <div className="event-details__rows">
        <div className="event-details__row">
          <IconClock size={18} />
          <span>{formatEventDate(event.date, event.time)}</span>
        </div>
        {event.location ? (
          <div className="event-details__row">
            <IconPin size={18} />
            <span>{event.location}</span>
          </div>
        ) : null}
        {event.price_label ? (
          <div className="event-details__row event-details__row--price">
            <IconTag size={18} />
            <span>{event.price_label}</span>
          </div>
        ) : null}
        <div className="event-details__row">
          <IconUsers size={18} />
          <span>{formatEventSeats(event.registration_count, event.max_participants)}</span>
        </div>
      </div>

      <LinkifiedText className="event-details__description" text={event.description} />
    </>
  );
}
