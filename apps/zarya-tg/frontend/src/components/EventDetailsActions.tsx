import type { Event } from "../api/client";
import { IconCalendar, IconShare } from "./icons";

interface EventDetailsActionsProps {
  event: Event;
  actionLoading: boolean;
  onCancel: () => void;
  onShare: () => void;
  onCalendar: () => void;
}

export function EventDetailsActions({
  event,
  actionLoading,
  onCancel,
  onShare,
  onCalendar,
}: EventDetailsActionsProps) {
  const isMaybe = event.is_maybe === true && !event.is_registered && !event.is_pending;
  const isPending = event.is_pending === true && !event.is_registered;
  const allowsSharing = event.allows_sharing !== false;

  return (
    <>
      {event.is_registered && (
        <>
          <button
            type="button"
            className="btn btn--ghost"
            onClick={onCancel}
            disabled={actionLoading}
          >
            Отменить регистрацию
          </button>
          <div className="event-details__icon-row">
            {allowsSharing && (
              <button
                type="button"
                className="icon-btn"
                onClick={onShare}
                aria-label="Поделиться"
              >
                <IconShare size={18} />
              </button>
            )}
            <button
              type="button"
              className="icon-btn"
              onClick={onCalendar}
              aria-label="В календарь"
            >
              <IconCalendar size={18} />
            </button>
          </div>
        </>
      )}

      {isPending && (
        <button
          type="button"
          className="btn btn--ghost"
          onClick={onCancel}
          disabled={actionLoading}
        >
          Отменить заявку
        </button>
      )}

      {isMaybe && (
        <button
          type="button"
          className="btn btn--ghost"
          onClick={onCancel}
          disabled={actionLoading}
        >
          Решил, что не пойду
        </button>
      )}
    </>
  );
}
