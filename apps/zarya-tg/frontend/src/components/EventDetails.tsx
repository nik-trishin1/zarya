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
import { CoverImage } from "./CoverImage";
import { buildEventShareLink, formatShareMessage } from "../utils/deepLink";
import {
  canTakeSeats,
  formatEventDate,
  formatEventSeats,
  isEventPast,
} from "../utils/format";
import { openTelegramShareLink } from "../utils/telegram";
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

  const handleMaybe = async () => {
    if (!event) return;
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
  const isMaybe = event.is_maybe === true && !event.is_registered;
  const archiveView = readOnly;
  // «Подумаю» allowed when full (no seat); going blocked when full
  const goingBlocked = past || (event.is_full ?? false);
  const allowsPlusOne = event.allows_plus_one !== false;
  const allowsSharing = event.allows_sharing !== false;
  const canRegisterAlone =
    !past &&
    !(event.is_full ?? false) &&
    canTakeSeats(event.registration_count, event.max_participants, 1);
  const canRegisterPlusOne =
    allowsPlusOne &&
    !past &&
    !(event.is_full ?? false) &&
    canTakeSeats(event.registration_count, event.max_participants, 2);
  const canAddPlusOne =
    allowsPlusOne &&
    event.is_registered &&
    event.party_size === 1 &&
    !past &&
    canTakeSeats(event.registration_count, event.max_participants, 1);
  const hasPlusOne = event.is_registered && event.party_size > 1;
  const canMarkMaybe = !past && !event.is_registered;

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

        {archiveView && (
          <div className="event-details__completed-banner">Событие завершено</div>
        )}

        <div className="event-details__actions">
          {archiveView ? null : (
            <>
          {past && !event.is_registered && (
            <div className="event-details__past">Событие прошло. Stay tuned!</div>
          )}
          {goingBlocked && !past && !event.is_registered && !isMaybe && (
            <div className="event-details__past">Fully booked. Stay tuned!</div>
          )}

          {event.is_registered ? (
            <div className="event-details__registered">
              {hasPlusOne ? "Вы зарегистрированы (+1) ✅" : "Вы зарегистрированы ✅"}
            </div>
          ) : isMaybe ? (
            <div className="event-details__maybe">Отметили «Подумаю»</div>
          ) : null}

          {!event.is_registered && !isMaybe && !past && (
            <>
              {allowsPlusOne ? (
                <div className="event-details__register-row">
                  <button
                    type="button"
                    className="btn btn--primary btn--half"
                    onClick={() => handleRegister(1)}
                    disabled={actionLoading || !canRegisterAlone}
                  >
                    Буду
                  </button>
                  <button
                    type="button"
                    className="btn btn--secondary btn--half"
                    onClick={() => handleRegister(2)}
                    disabled={actionLoading || !canRegisterPlusOne}
                    title={!canRegisterPlusOne ? "Недостаточно мест для +1" : undefined}
                  >
                    Буду +1
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  className="btn btn--primary"
                  onClick={() => handleRegister(1)}
                  disabled={actionLoading || !canRegisterAlone}
                >
                  Зарегистрироваться
                </button>
              )}
            </>
          )}

          {isMaybe && (
            <div className="event-details__register-row">
              <button
                type="button"
                className="btn btn--primary btn--half"
                onClick={() => handleRegister(1)}
                disabled={actionLoading || !canRegisterAlone}
              >
                Буду
              </button>
              {allowsPlusOne && (
                <button
                  type="button"
                  className="btn btn--secondary btn--half"
                  onClick={() => handleRegister(2)}
                  disabled={actionLoading || !canRegisterPlusOne}
                  title={!canRegisterPlusOne ? "Недостаточно мест для +1" : undefined}
                >
                  Буду +1
                </button>
              )}
            </div>
          )}

          {canMarkMaybe && !isMaybe && (
            <button
              type="button"
              className="btn btn--secondary"
              onClick={handleMaybe}
              disabled={actionLoading}
            >
              Подумаю
            </button>
          )}

          {event.is_registered && (
            <>
              {allowsPlusOne &&
                (hasPlusOne ? (
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
                ))}
              <div className="event-details__secondary-row">
                <button
                  type="button"
                  className={`btn btn--secondary${allowsSharing ? " btn--half" : ""}`}
                  onClick={handleCalendar}
                >
                  🗓️ В календарь
                </button>
                {allowsSharing && (
                  <button type="button" className="btn btn--secondary btn--half" onClick={handleShare}>
                    🔗 Поделиться
                  </button>
                )}
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

          {isMaybe && (
            <button
              type="button"
              className="btn btn--ghost"
              onClick={handleCancel}
              disabled={actionLoading}
            >
              Снять «Подумаю»
            </button>
          )}
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
