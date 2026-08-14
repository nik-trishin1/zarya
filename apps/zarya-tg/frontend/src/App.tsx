import { useCallback, useEffect, useState } from "react";
import type { Event } from "./api/client";
import { fetchEvents, fetchMyArchive, fetchMyRegistrations } from "./api/client";
import { EventCard } from "./components/EventCard";
import { EventDetails } from "./components/EventDetails";
import { Header } from "./components/Header";
import { PosterSlider } from "./components/PosterSlider";
import { useTelegram } from "./hooks/useTelegram";
import { getTelegramStartParam, parseEventStartParam } from "./utils/deepLink";
import "./App.css";

type Screen = "home" | "registrations";

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

    (async () => {
      try {
        const { events: loadedEvents, archive } = await loadScreenData(screen);
        if (cancelled) return;
        setEvents(loadedEvents);
        setArchiveEvents(archive);
        if (screen === "registrations") {
          setRegistrationCount(loadedEvents.length);
        }
        setError(null);
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Ошибка загрузки");
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
    setLoading(true);
    void (async () => {
      try {
        const { events: loadedEvents, archive } = await loadScreenData(screen);
        setEvents(loadedEvents);
        setArchiveEvents(archive);
        if (screen === "registrations") {
          setRegistrationCount(loadedEvents.length);
        }
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Ошибка загрузки");
      } finally {
        setLoading(false);
      }
    })();
    void refreshRegistrationCount();
  }, [screen, loadScreenData, refreshRegistrationCount]);

  const handleNavClick = () => {
    setLoading(true);
    setScreen((s) => (s === "home" ? "registrations" : "home"));
  };

  const handleEventSelect = (event: Event, fromArchive = false) => {
    setSelectedFromArchive(fromArchive);
    setSelectedEventId(event.event_id);
  };

  const emptyMessage =
    screen === "home"
      ? "Нет предстоящих событий"
      : "Вы не зарегистрированы ни на какие события";

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
        {showEmptyState && <p className="app__status">{emptyMessage}</p>}
        {!loading && !error && screen === "home" && hasUpcoming && (
          <>
            {featuredEvents.length > 0 && (
              <PosterSlider
                events={featuredEvents}
                onSelect={(e) => handleEventSelect(e)}
              />
            )}
            <div className="event-list">
              {events.map((event) => (
                <EventCard key={event.event_id} event={event} onClick={(e) => handleEventSelect(e)} />
              ))}
            </div>
          </>
        )}
        {!loading && !error && screen === "registrations" && (hasUpcoming || hasArchive) && (
          <>
            {hasUpcoming && (
              <div className="event-list">
                {events.map((event) => (
                  <EventCard key={event.event_id} event={event} onClick={(e) => handleEventSelect(e)} />
                ))}
              </div>
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
