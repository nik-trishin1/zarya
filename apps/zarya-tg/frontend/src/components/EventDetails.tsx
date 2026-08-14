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
import {
  IconCalendar,
  IconCheck,
  IconChevronLeft,
  IconClock,
  IconPause,
  IconPin,
  IconShare,
  IconUsers,
} from "./icons";
import { useTelegramBackButton } from "../hooks/useTelegram";
import { buildEventShareLink, formatShareMessage } from "../utils/deepLink";
import {
  canTakeSeats,
  formatEventDate,
  formatEventSeats,
  isEventPast,
} from "../utils/format";
import { hapticImpact, isTelegramMiniApp, openTelegramShareLink } from "../utils/telegram";
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
  const showChevronBack = !isTelegramMiniApp();

  useTelegramBackButton(onClose);

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
    const clearingMaybe = event.is_maybe === true && !event.is_registered;
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

  const backControl = showChevronBack ? (
    <button type="button" className="event-details__back" onClick={onClose} aria-label="Назад">
      <IconChevronLeft size={22} />
    </button>
  ) : null;

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

  const past = event.is_past ?? isEventPast(event.date);
  const isMaybe = event.is_maybe === true && !event.is_registered;
  const archiveView = readOnly;
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
  const goingDisabled = actionLoading || (!event.is_registered && !canRegisterAlone);
  const canMarkMaybe = !past && !event.is_registered;
  const showRsvp = !archiveView && (!past || event.is_registered || isMaybe);
  const showMaybeCircle = showRsvp && !event.is_registered;

  const plusOneDisabled = event.is_registered
    ? actionLoading || past || (!hasPlusOne && !canAddPlusOne)
    : actionLoading || !canRegisterPlusOne;
  const plusOneTitle = event.is_registered
    ? !hasPlusOne && !canAddPlusOne
      ? "Недостаточно мест для +1"
      : undefined
    : !canRegisterPlusOne
      ? "Недостаточно мест для +1"
      : undefined;

  return (
    <div className="event-details">
      {backControl}

      <CoverImage url={event.cover_image_url} className="event-details__cover" />

      <div className="event-details__body">
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
          <div className="event-details__row">
            <IconUsers size={18} />
            <span>{formatEventSeats(event.registration_count, event.max_participants)}</span>
          </div>
        </div>

        <p className="event-details__description">{event.description}</p>

        <div className="event-details__actions">
          {archiveView ? null : (
            <>
              {past && !event.is_registered && (
                <div className="event-details__past">Событие прошло</div>
              )}
              {goingBlocked && !past && !event.is_registered && !isMaybe && (
                <div className="event-details__past">Мест нет</div>
              )}

              {showRsvp && (
                <div className="rsvp">
                  <div className="rsvp__row">
                    <div className="rsvp__option">
                      <button
                        type="button"
                        className={`rsvp__circle rsvp__circle--going${event.is_registered ? " rsvp__circle--selected" : ""}`}
                        onClick={() => {
                          if (!event.is_registered) {
                            void handleRegister(1);
                          }
                        }}
                        disabled={goingDisabled}
                        aria-pressed={event.is_registered}
                        aria-label="Буду"
                      >
                        <IconCheck size={24} />
                      </button>
                      <span className="rsvp__caption">Буду</span>
                      {allowsPlusOne && (
                        <button
                          type="button"
                          className={`rsvp__chip${hasPlusOne ? " rsvp__chip--active" : ""}`}
                          onClick={() => {
                            if (event.is_registered) {
                              void handlePartySizeChange(hasPlusOne ? 1 : 2);
                            } else {
                              void handleRegister(2);
                            }
                          }}
                          disabled={plusOneDisabled}
                          title={plusOneTitle}
                          aria-label={hasPlusOne ? "Убрать +1" : "+1"}
                        >
                          {hasPlusOne ? "Убрать +1" : "+1"}
                        </button>
                      )}
                    </div>

                    {showMaybeCircle && (
                      <div className="rsvp__option">
                        <button
                          type="button"
                          className={`rsvp__circle rsvp__circle--maybe${isMaybe ? " rsvp__circle--selected" : ""}`}
                          onClick={() => {
                            if (!isMaybe) {
                              void handleMaybe();
                            }
                          }}
                          disabled={actionLoading || (!isMaybe && !canMarkMaybe)}
                          aria-pressed={isMaybe}
                          aria-label="Подумаю"
                        >
                          <IconPause size={22} />
                        </button>
                        <span className="rsvp__caption">Подумаю</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {event.is_registered && (
                <>
                  <button
                    type="button"
                    className="btn btn--ghost"
                    onClick={() => void handleCancel()}
                    disabled={actionLoading}
                  >
                    Отменить регистрацию
                  </button>
                  <div className="event-details__icon-row">
                    {allowsSharing && (
                      <button
                        type="button"
                        className="icon-btn"
                        onClick={() => void handleShare()}
                        aria-label="Поделиться"
                      >
                        <IconShare size={18} />
                      </button>
                    )}
                    <button
                      type="button"
                      className="icon-btn"
                      onClick={() => void handleCalendar()}
                      aria-label="В календарь"
                    >
                      <IconCalendar size={18} />
                    </button>
                  </div>
                </>
              )}

              {isMaybe && (
                <button
                  type="button"
                  className="btn btn--ghost"
                  onClick={() => void handleCancel()}
                  disabled={actionLoading}
                >
                  Решил, что не пойду
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
