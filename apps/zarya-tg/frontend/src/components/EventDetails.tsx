import { useEffect, useState } from "react";
import type { Event } from "../api/client";
import {
  cancelRegistration,
  downloadCalendar,
  fetchEvent,
  registerForEvent,
} from "../api/client";
import { CoverImage } from "./CoverImage";
import { formatEventDate } from "../utils/format";
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

  useEffect(() => {
    setLoading(true);
    fetchEvent(eventId)
      .then(setEvent)
      .catch(() => setToast("Не удалось загрузить событие"))
      .finally(() => setLoading(false));
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
      await downloadCalendar(event.event_id, event.name);
    } catch {
      setToast("Не удалось скачать календарь");
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
        <p className="event-details__count">Зарегистрировано: {event.registration_count} человек</p>

        <div className="event-details__actions">
          {event.is_registered ? (
            <>
              <div className="event-details__registered">Вы зарегистрированы ✅</div>
              <button type="button" className="btn btn--secondary" onClick={handleCalendar}>
                Добавить в календарь
              </button>
              <button
                type="button"
                className="btn btn--ghost"
                onClick={handleCancel}
                disabled={actionLoading}
              >
                Отменить регистрацию
              </button>
            </>
          ) : (
            <button
              type="button"
              className="btn btn--primary"
              onClick={handleRegister}
              disabled={actionLoading}
            >
              Зарегистрироваться
            </button>
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
