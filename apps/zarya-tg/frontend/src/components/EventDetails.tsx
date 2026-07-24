import { useEffect, useState } from "react";
import type { Event } from "../api/client";
import {
  cancelRegistration,
  downloadCalendar,
  fetchEvent,
  registerForEvent,
  updateRegistrationPartySize,
} from "../api/client";
import { CoverImage } from "./CoverImage";
import { buildEventShareLink, formatShareMessage } from "../utils/deepLink";
import {
  canTakeSeats,
  formatEventDate,
  formatEventSeats,
  hasGuestLimit,
  isEventPast,
} from "../utils/format";
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

  const refreshAfterChange = async (message: string) => {
    if (!event) return;
    setToast(message);
    const updated = await fetchEvent(event.event_id);
    setEvent(updated);
    onRegistrationChange();
  };

  const handleRegister = async (partySize: number) => {
    if (!event) return;
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
    setActionLoading(true);
    try {
      const result = await cancelRegistration(event.event_id);
      await refreshAfterChange(result.message);
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
  const canRegisterAlone =
    !registrationBlocked && canTakeSeats(event.registration_count, event.max_participants, 1);
  const canRegisterPlusOne =
    !registrationBlocked && canTakeSeats(event.registration_count, event.max_participants, 2);
  const canAddPlusOne =
    event.is_registered &&
    event.party_size === 1 &&
    !past &&
    canTakeSeats(event.registration_count, event.max_participants, 1);
  const hasPlusOne = event.is_registered && event.party_size > 1;

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
            <div className="event-details__registered">
              {hasPlusOne ? "Вы зарегистрированы (+1) ✅" : "Вы зарегистрированы ✅"}
            </div>
          ) : (
            !registrationBlocked && (
              <div className="event-details__register-row">
                <button
                  type="button"
                  className="btn btn--primary btn--half"
                  onClick={() => handleRegister(1)}
                  disabled={actionLoading || !canRegisterAlone}
                >
                  Один
                </button>
                <button
                  type="button"
                  className="btn btn--secondary btn--half"
                  onClick={() => handleRegister(2)}
                  disabled={actionLoading || !canRegisterPlusOne}
                  title={!canRegisterPlusOne ? "Недостаточно мест для +1" : undefined}
                >
                  +1
                </button>
              </div>
            )
          )}

          {event.is_registered && (
            <>
              {hasPlusOne ? (
                <button
                  type="button"
                  className="btn btn--secondary"
                  onClick={() => handlePartySizeChange(1)}
                  disabled={actionLoading || past}
                >
                  Убрать +1
                </button>
              ) : (
                <button
                  type="button"
                  className="btn btn--secondary"
                  onClick={() => handlePartySizeChange(2)}
                  disabled={actionLoading || past || !canAddPlusOne}
                  title={!canAddPlusOne ? "Недостаточно мест для +1" : undefined}
                >
                  Добавить +1
                </button>
              )}
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
