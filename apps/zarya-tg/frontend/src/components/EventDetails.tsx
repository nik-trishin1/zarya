import { useEffect, useState } from "react";
import type { Event } from "../api/client";
import {
  cancelRegistration,
  downloadCalendar,
  fetchEvent,
  markEventMaybe,
  registerForEvent,
  updateRegistrationPartySize,
} from "../api/client";
import { buildEventShareLink, formatShareMessage } from "../utils/deepLink";
import { hapticImpact, openTelegramShareLink } from "../utils/telegram";
import { CoverImage } from "./CoverImage";
import { EventDetailsActions } from "./EventDetailsActions";
import { EventDetailsHeader } from "./EventDetailsHeader";
import { EventDetailsRegistration } from "./EventDetailsRegistration";
import "./EventDetails.css";

interface EventDetailsProps {
  eventId: number;
  readOnly?: boolean;
  onClose: () => void;
  onRegistrationChange: () => void;
}

export function EventDetails({ eventId, readOnly = false, onClose, onRegistrationChange }: EventDetailsProps) {
  const [event, setEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  // Parent remounts this component with key={eventId}; loading starts true.
  useEffect(() => {
    let cancelled = false;
    fetchEvent(eventId)
      .then((data) => {
        if (!cancelled) setEvent(data);
      })
      .catch(() => {
        if (!cancelled) setToast("Не удалось загрузить событие");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [eventId]);

  const refreshAfterChange = async (message?: string | null) => {
    if (!event) return;
    if (message) setToast(message);
    const updated = await fetchEvent(event.event_id);
    setEvent(updated);
    onRegistrationChange();
  };

  const handleRegister = async (partySize: number) => {
    if (!event) return;
    hapticImpact();
    setActionLoading(true);
    try {
      const result = await registerForEvent(event.event_id, partySize);
      await refreshAfterChange(result.message);
    } catch (err) {
      setToast(err instanceof Error ? err.message : "Ошибка регистрации");
    } finally {
      setActionLoading(false);
    }
  };

  const handlePartySizeChange = async (partySize: number) => {
    if (!event) return;
    hapticImpact();
    setActionLoading(true);
    try {
      const result = await updateRegistrationPartySize(event.event_id, partySize);
      await refreshAfterChange(result.message);
    } catch (err) {
      setToast(err instanceof Error ? err.message : "Не удалось изменить +1");
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!event) return;
    const clearingMaybe = event.is_maybe === true && !event.is_registered && !event.is_pending;
    hapticImpact("light");
    setActionLoading(true);
    try {
      const result = await cancelRegistration(event.event_id);
      // No toast when clearing «Подумаю» — UI already shows the new state
      await refreshAfterChange(clearingMaybe ? null : result.message);
    } catch (err) {
      setToast(err instanceof Error ? err.message : "Ошибка отмены");
    } finally {
      setActionLoading(false);
    }
  };

  const handleMaybe = async () => {
    if (!event) return;
    hapticImpact();
    setActionLoading(true);
    try {
      const result = await markEventMaybe(event.event_id);
      await refreshAfterChange(result.message);
    } catch (err) {
      setToast(err instanceof Error ? err.message : "Не удалось отметить «Подумаю»");
    } finally {
      setActionLoading(false);
    }
  };

  const handleCalendar = async () => {
    if (!event) return;
    try {
      await downloadCalendar(event.event_id);
    } catch (err) {
      setToast(err instanceof Error ? err.message : "Не удалось открыть календарь");
    }
  };

  const handleShare = async () => {
    if (!event) return;
    const link = buildEventShareLink(event.event_id);
    const message = formatShareMessage(event.name, link, event.description);
    if (openTelegramShareLink(message)) {
      return;
    }

    try {
      await navigator.clipboard.writeText(message);
      setToast("Ссылка скопирована");
    } catch {
      setToast("Не удалось скопировать ссылку");
    }
  };

  const backControl = (
    <button type="button" className="event-details__back" onClick={onClose} aria-label="На главную">
      🏠
    </button>
  );

  if (loading) {
    return (
      <div className="event-details">
        {backControl}
        <div className="event-details__loading">Загрузка...</div>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="event-details">
        {backControl}
        <p className="event-details__error">Событие не найдено</p>
      </div>
    );
  }

  const archiveView = readOnly;

  return (
    <div className="event-details">
      {backControl}

      {/* Cover stays outside `.event-details__body` (same layout as before the split). */}
      <CoverImage url={event.cover_image_url} className="event-details__cover" />

      <div className="event-details__body">
        <EventDetailsHeader event={event} />

        <div className="event-details__actions">
          {archiveView ? null : (
            <>
              <EventDetailsRegistration
                event={event}
                actionLoading={actionLoading}
                onRegister={(partySize) => void handleRegister(partySize)}
                onPartySizeChange={(partySize) => void handlePartySizeChange(partySize)}
                onMaybe={() => void handleMaybe()}
              />
              <EventDetailsActions
                event={event}
                actionLoading={actionLoading}
                onCancel={() => void handleCancel()}
                onShare={() => void handleShare()}
                onCalendar={() => void handleCalendar()}
              />
            </>
          )}
        </div>
      </div>

      {toast && (
        <div className="toast" onClick={() => setToast(null)}>
          {toast}
        </div>
      )}
    </div>
  );
}
