import type { Event } from "./api/client";
import { EventCard } from "./components/EventCard";
import { IconCalendarEmpty } from "./components/icons";
import { PosterSlider } from "./components/PosterSlider";
import { groupEventsByCalendarDay } from "./utils/format";

export type Screen = "home" | "registrations";

function EmptyState({ title, hint }: { title: string; hint: string }) {
  return (
    <div className="empty-state">
      <IconCalendarEmpty className="empty-state__icon" />
      <p className="empty-state__title">{title}</p>
      <p className="empty-state__hint">{hint}</p>
    </div>
  );
}

function GroupedEventList({
  events,
  completed = false,
  onSelect,
}: {
  events: Event[];
  completed?: boolean;
  onSelect: (event: Event, fromArchive?: boolean) => void;
}) {
  const groups = groupEventsByCalendarDay(events);
  return (
    <div className="event-list">
      {groups.map((group, index) => (
        <section key={group.header ?? `day-${index}`} className="event-list__group">
          {group.header && <h2 className="event-list__day-header">{group.header}</h2>}
          {group.events.map((event) => (
            <EventCard
              key={event.event_id}
              event={event}
              completed={completed}
              onClick={(selected) => onSelect(selected, completed)}
            />
          ))}
        </section>
      ))}
    </div>
  );
}

export function HomeScreen({
  events,
  onSelect,
}: {
  events: Event[];
  onSelect: (event: Event, fromArchive?: boolean) => void;
}) {
  const featuredEvents = events.filter((event) => event.is_featured);
  return (
    <>
      {featuredEvents.length > 0 && (
        <PosterSlider events={featuredEvents} onSelect={(e) => onSelect(e)} />
      )}
      <GroupedEventList events={events} onSelect={onSelect} />
    </>
  );
}

export function RegistrationsScreen({
  events,
  archiveEvents,
  onSelect,
}: {
  events: Event[];
  archiveEvents: Event[];
  onSelect: (event: Event, fromArchive?: boolean) => void;
}) {
  const hasUpcoming = events.length > 0;
  const hasArchive = archiveEvents.length > 0;
  return (
    <>
      {hasUpcoming && <GroupedEventList events={events} onSelect={onSelect} />}
      {hasArchive && (
        <>
          <h2 className="app__section-title">Архив</h2>
          <div className="event-list">
            {archiveEvents.map((event) => (
              <EventCard
                key={event.event_id}
                event={event}
                completed
                onClick={(e) => onSelect(e, true)}
              />
            ))}
          </div>
        </>
      )}
    </>
  );
}

export function ScreenEmptyState({ screen }: { screen: Screen }) {
  if (screen === "home") {
    return (
      <EmptyState
        title="Нет предстоящих событий"
        hint="Загляните позже — новые встречи появятся здесь."
      />
    );
  }
  return (
    <EmptyState
      title="Пока нет регистраций"
      hint="Откройте События и отметьтесь на встрече."
    />
  );
}
