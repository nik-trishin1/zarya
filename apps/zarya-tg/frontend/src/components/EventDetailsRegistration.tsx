import type { Event } from "../api/client";
import { canTakeSeats, isEventPast } from "../utils/format";
import { IconCheck, IconPause } from "./icons";

interface EventDetailsRegistrationProps {
  event: Event;
  actionLoading: boolean;
  onRegister: (partySize: number) => void;
  onPartySizeChange: (partySize: number) => void;
  onMaybe: () => void;
}

export function EventDetailsRegistration({
  event,
  actionLoading,
  onRegister,
  onPartySizeChange,
  onMaybe,
}: EventDetailsRegistrationProps) {
  const past = event.is_past ?? isEventPast(event.date);
  const isMaybe = event.is_maybe === true && !event.is_registered && !event.is_pending;
  const isPending = event.is_pending === true && !event.is_registered;
  const requiresApproval = event.requires_approval === true;
  const goingBlocked = past || (event.is_full ?? false);
  const allowsPlusOne = event.allows_plus_one !== false;
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
  const goingDisabled =
    actionLoading || (!event.is_registered && !isPending && !canRegisterAlone);
  const canMarkMaybe = !past && !event.is_registered && !isPending;
  const showRsvp = !past || event.is_registered || isMaybe || isPending;
  const showMaybeCircle = showRsvp && !event.is_registered && !isPending;
  const goingCaption = isPending
    ? "На рассмотрении"
    : requiresApproval && !event.is_registered
      ? "Записаться"
      : "Буду";
  const showPlusOneChip = allowsPlusOne && !isPending;

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
    <>
      {past && !event.is_registered && !isPending && (
        <div className="event-details__past">Событие прошло</div>
      )}
      {goingBlocked && !past && !event.is_registered && !isMaybe && !isPending && (
        <div className="event-details__past">Мест нет</div>
      )}

      {showRsvp && (
        <div className="rsvp">
          <div className="rsvp__row">
            <div className="rsvp__option">
              <button
                type="button"
                className={`rsvp__circle rsvp__circle--going${event.is_registered ? " rsvp__circle--selected" : ""}${isPending ? " rsvp__circle--pending rsvp__circle--selected" : ""}`}
                onClick={() => {
                  if (!event.is_registered && !isPending) {
                    onRegister(1);
                  }
                }}
                disabled={goingDisabled}
                aria-pressed={event.is_registered || isPending}
                aria-label={goingCaption}
              >
                <IconCheck size={24} />
              </button>
              <span className="rsvp__caption">{goingCaption}</span>
              {showPlusOneChip && (
                <button
                  type="button"
                  className={`rsvp__chip${hasPlusOne ? " rsvp__chip--active" : ""}`}
                  onClick={() => {
                    if (event.is_registered) {
                      onPartySizeChange(hasPlusOne ? 1 : 2);
                    } else {
                      onRegister(2);
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
                      onMaybe();
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
    </>
  );
}
