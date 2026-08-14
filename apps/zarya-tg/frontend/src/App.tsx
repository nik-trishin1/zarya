import { useCallback, useEffect, useRef, useState } from "react";
import type { Event } from "./api/client";
import { fetchEvents, fetchMyArchive, fetchMyRegistrations } from "./api/client";
import { EventCard } from "./components/EventCard";
import { EventDetails } from "./components/EventDetails";
import { Header } from "./components/Header";
import { IconCalendarEmpty } from "./components/icons";
import { PosterSlider } from "./components/PosterSlider";
import { useTelegram } from "./hooks/useTelegram";
import { getTelegramStartParam, parseEventStartParam } from "./utils/deepLink";
import { groupEventsByCalendarDay } from "./utils/format";
import "./App.css";

type Screen = "home" | "registrations";

type ScreenCache = {
  home: Event[] | null;
  registrations: { events: Event[]; archive: Event[] } | null;
};

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

function applyCacheToState(
  screen: Screen,
  cache: ScreenCache,
  setEvents: (events: Event[]) => void,
  setArchiveEvents: (events: Event[]) => void,
): boolean {
  if (screen === "home" && cache.home) {
    setEvents(cache.home);
    setArchiveEvents([]);
    return true;
  }
  if (screen === "registrations" && cache.registrations) {
    setEvents(cache.registrations.events);
    setArchiveEvents(cache.registrations.archive);
    return true;
  }
  return false;
}

function App() {
  useTelegram();
  const [screen, setScreen] = useState<Screen>("home");
  const [events, setEvents] = useState<Event[]>([]);
  const [archiveEvents, setArchiveEvents] = useState<Event[]>([]);
  const [registrationCount, setRegistrationCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEventId, setSelectedEventId] = useState<number | null>(() =>
    parseEventStartParam(getTelegramStartParam()),
  );
  const [selectedFromArchive, setSelectedFromArchive] = useState(false);
  const cacheRef = useRef<ScreenCache>({ home: null, registrations: null });

  const refreshRegistrationCount = useCallback(async () => {
    try {
      const data = await fetchMyRegistrations();
      setRegistrationCount(data.length);
    } catch {
      // Keep previous count if the request fails silently in the background.
    }
  }, []);

  const loadScreenData = useCallback(async (currentScreen: Screen) => {
    if (currentScreen === "home") {
      const data = await fetchEvents();
      return { events: data, archive: [] as Event[] };
    }
    const [upcoming, archive] = await Promise.all([
      fetchMyRegistrations(),
      fetchMyArchive(),
    ]);
    return { events: upcoming, archive };
  }, []);

  useEffect(() => {
    let cancelled = false;
    const hadCache = applyCacheToState(screen, cacheRef.current, setEvents, setArchiveEvents);
    if (hadCache) {
      setLoading(false);
    } else {
      setLoading(true);
    }

    (async () => {
      try {
        const { events: loadedEvents, archive } = await loadScreenData(screen);
        if (cancelled) return;
        if (screen === "home") {
          cacheRef.current.home = loadedEvents;
        } else {
          cacheRef.current.registrations = { events: loadedEvents, archive };
        }
        setEvents(loadedEvents);
        setArchiveEvents(archive);
        if (screen === "registrations") {
          setRegistrationCount(loadedEvents.length);
        }
        setError(null);
      } catch (err) {
        if (cancelled) return;
        if (!hadCache) {
          setError(err instanceof Error ? err.message : "Ошибка загрузки");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [screen, loadScreenData]);

  useEffect(() => {
    if (screen !== "home") return;
    let cancelled = false;

    (async () => {
      try {
        const data = await fetchMyRegistrations();
        if (!cancelled) setRegistrationCount(data.length);
      } catch {
        // Keep previous count if the request fails silently in the background.
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [screen]);

  const handleRegistrationChange = useCallback(() => {
    void (async () => {
      try {
        const { events: loadedEvents, archive } = await loadScreenData(screen);
        if (screen === "home") {
          cacheRef.current.home = loadedEvents;
        } else {
          cacheRef.current.registrations = { events: loadedEvents, archive };
        }
        setEvents(loadedEvents);
        setArchiveEvents(archive);
        if (screen === "registrations") {
          setRegistrationCount(loadedEvents.length);
        }
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Ошибка загрузки");
      }
    })();
    void refreshRegistrationCount();
  }, [screen, loadScreenData, refreshRegistrationCount]);

  const handleNavClick = () => {
    setScreen((s) => (s === "home" ? "registrations" : "home"));
  };

  const handleEventSelect = (event: Event, fromArchive = false) => {
    setSelectedFromArchive(fromArchive);
    setSelectedEventId(event.event_id);
  };

  const featuredEvents =
    screen === "home" ? events.filter((event) => event.is_featured) : [];

  const hasUpcoming = events.length > 0;
  const hasArchive = screen === "registrations" && archiveEvents.length > 0;
  const showEmptyState = !loading && !error && !hasUpcoming && !hasArchive;

  return (
    <div className="app">
      <Header screen={screen} registrationCount={registrationCount} onNavClick={handleNavClick} />

      <main className="app__main">
        {loading && <p className="app__status">Загрузка...</p>}
        {error && <p className="app__status app__status--error">{error}</p>}
        {showEmptyState && screen === "home" && (
          <EmptyState
            title="Нет предстоящих событий"
            hint="Загляните позже — новые встречи появятся здесь."
          />
        )}
        {showEmptyState && screen === "registrations" && (
          <EmptyState
            title="Пока нет регистраций"
            hint="Откройте События и отметьтесь на встрече."
          />
        )}
        {!loading && !error && screen === "home" && hasUpcoming && (
          <>
            {featuredEvents.length > 0 && (
              <PosterSlider
                events={featuredEvents}
                onSelect={(e) => handleEventSelect(e)}
              />
            )}
            <GroupedEventList events={events} onSelect={handleEventSelect} />
          </>
        )}
        {!loading && !error && screen === "registrations" && (hasUpcoming || hasArchive) && (
          <>
            {hasUpcoming && (
              <GroupedEventList events={events} onSelect={handleEventSelect} />
            )}
            {hasArchive && (
              <>
                <h2 className="app__section-title">Архив</h2>
                <div className="event-list">
                  {archiveEvents.map((event) => (
                    <EventCard
                      key={event.event_id}
                      event={event}
                      completed
                      onClick={(e) => handleEventSelect(e, true)}
                    />
                  ))}
                </div>
              </>
            )}
          </>
        )}
      </main>

      {selectedEventId !== null && (
        <EventDetails
          key={selectedEventId}
          eventId={selectedEventId}
          readOnly={selectedFromArchive}
          onClose={() => {
            setSelectedEventId(null);
            setSelectedFromArchive(false);
          }}
          onRegistrationChange={handleRegistrationChange}
        />
      )}
    </div>
  );
}

export default App;
