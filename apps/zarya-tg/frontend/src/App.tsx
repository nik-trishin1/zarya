import { useCallback, useEffect, useState } from "react";
import type { Event } from "./api/client";
import { fetchEvents, fetchMyRegistrations } from "./api/client";
import { EventCard } from "./components/EventCard";
import { EventDetails } from "./components/EventDetails";
import { Header } from "./components/Header";
import { useTelegram } from "./hooks/useTelegram";
import { getTelegramStartParam, parseEventStartParam } from "./utils/deepLink";
import "./App.css";

type Screen = "home" | "registrations";

function App() {
  useTelegram();
  const [screen, setScreen] = useState<Screen>("home");
  const [events, setEvents] = useState<Event[]>([]);
  const [registrationCount, setRegistrationCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEventId, setSelectedEventId] = useState<number | null>(() =>
    parseEventStartParam(getTelegramStartParam()),
  );

  const refreshRegistrationCount = useCallback(async () => {
    try {
      const data = await fetchMyRegistrations();
      setRegistrationCount(data.length);
    } catch {
      // Keep previous count if the request fails silently in the background.
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const data = screen === "home" ? await fetchEvents() : await fetchMyRegistrations();
        if (cancelled) return;
        setEvents(data);
        if (screen === "registrations") {
          setRegistrationCount(data.length);
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
  }, [screen]);

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
        const data = screen === "home" ? await fetchEvents() : await fetchMyRegistrations();
        setEvents(data);
        if (screen === "registrations") {
          setRegistrationCount(data.length);
        }
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Ошибка загрузки");
      } finally {
        setLoading(false);
      }
    })();
    void refreshRegistrationCount();
  }, [screen, refreshRegistrationCount]);

  const handleNavClick = () => {
    setLoading(true);
    setScreen((s) => (s === "home" ? "registrations" : "home"));
  };

  const emptyMessage =
    screen === "home"
      ? "Нет предстоящих событий"
      : "Вы не зарегистрированы ни на какие события";

  return (
    <div className="app">
      <Header screen={screen} registrationCount={registrationCount} onNavClick={handleNavClick} />

      <main className="app__main">
        {loading && <p className="app__status">Загрузка...</p>}
        {error && <p className="app__status app__status--error">{error}</p>}
        {!loading && !error && events.length === 0 && (
          <p className="app__status">{emptyMessage}</p>
        )}
        {!loading && !error && events.length > 0 && (
          <div className="event-list">
            {events.map((event) => (
              <EventCard key={event.event_id} event={event} onClick={(e) => setSelectedEventId(e.event_id)} />
            ))}
          </div>
        )}
      </main>

      {selectedEventId !== null && (
        <EventDetails
          key={selectedEventId}
          eventId={selectedEventId}
          onClose={() => setSelectedEventId(null)}
          onRegistrationChange={handleRegistrationChange}
        />
      )}
    </div>
  );
}

export default App;
