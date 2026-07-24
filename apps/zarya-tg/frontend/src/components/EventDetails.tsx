import { useEffect, useState } from "react";
import type { Event } from "../api/client";
import {
  cancelRegistration,
  downloadCalendar,
  fetchEvent,
  registerForEvent,
} from "../api/client";
import { CoverImage } from "./CoverImage";
import { buildEventShareLink, formatShareMessage } from "../utils/deepLink";
import { formatEventDate, formatEventSeats, hasGuestLimit, isEventPast } from "../utils/format";
import { openTelegramShareLink } from "../utils/telegram";
import "./EventDetails.css";

interface EventDetailsProps {
  eventId: number;
  onClose: () => void;
  onRegistrationChange: () => void;
}

export function EventDetails({ eventId, onClose, onRegistrationChange }: EventDetailsProps) {
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

  const handleRegister = async () => {
    if (!event) return;
    setActionLoading(true);
    try {
      const result = await registerForEvent(event.event_id);
      setToast(result.message);
      const updated = await fetchEvent(event.event_id);
      setEvent(updated);
      onRegistrationChange();
    } catch (err) {
      setToast(err instanceof Error ? err.message : "Ошибка регистрации");
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!event) return;
    setActionLoading(true);
    try {
      const result = await cancelRegistration(event.event_id);
      setToast(result.message);
      const updated = await fetchEvent(event.event_id);
      setEvent(updated);
      onRegistrationChange();
    } catch (err) {
      setToast(err instanceof Error ? err.message : "Ошибка отмены");
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

  if (loading) {
    return (
      <div className="event-details">
        <div className="event-details__loading">Загрузка...</div>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="event-details">
        <button type="button" className="event-details__back" onClick={onClose}>🏠</button>
        <p className="event-details__error">Событие не найдено</p>
      </div>
    );
  }

  const past = event.is_past ?? isEventPast(event.date);
  const full =
    !event.is_registered &&
    (event.is_full ??
      (hasGuestLimit(event.max_participants) &&
        event.registration_count >= (event.max_participants as number)));
  const registrationBlocked = past || full;

  return (
    <div className="event-details">
      <button type="button" className="event-details__back" onClick={onClose} aria-label="На главную">
        🏠
      </button>

      <CoverImage url={event.cover_image_url} className="event-details__cover" />

      <div className="event-details__body">
        <h2 className="event-details__title">{event.name}</h2>
        <p className="event-details__meta">{formatEventDate(event.date, event.time)}</p>
        <p className="event-details__meta">📍 {event.location}</p>
        <p className="event-details__description">{event.description}</p>
        <p className="event-details__count">
          {formatEventSeats(event.registration_count, event.max_participants)}
        </p>

        <div className="event-details__actions">
          {past && !event.is_registered && (
            <div className="event-details__past">Событие прошло. Stay tuned!</div>
          )}
          {full && (
            <div className="event-details__past">Fully booked. Stay tuned!</div>
          )}
          {event.is_registered ? (
            <div className="event-details__registered">Вы зарегистрированы ✅</div>
          ) : (
            <button
              type="button"
              className="btn btn--primary"
              onClick={handleRegister}
              disabled={actionLoading || registrationBlocked}
            >
              Зарегистрироваться
            </button>
          )}

          {event.is_registered && (
            <>
              <div className="event-details__secondary-row">
                <button type="button" className="btn btn--secondary btn--half" onClick={handleCalendar}>
                  🗓️ В календарь
                </button>
                <button type="button" className="btn btn--secondary btn--half" onClick={handleShare}>
                  🔗 Поделиться
                </button>
              </div>
              <button
                type="button"
                className="btn btn--ghost"
                onClick={handleCancel}
                disabled={actionLoading}
              >
                Отменить регистрацию
              </button>
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
