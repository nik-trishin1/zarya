import { useCallback, useEffect, useState } from "react";
import type { Event } from "./api/client";
import { fetchEvents, fetchMyRegistrations } from "./api/client";
import { EventCard } from "./components/EventCard";
import { EventDetails } from "./components/EventDetails";
import { Header } from "./components/Header";
import { useTelegram } from "./hooks/useTelegram";
import "./App.css";

type Screen = "home" | "registrations";

function App() {
  useTelegram();
  const [screen, setScreen] = useState<Screen>("home");
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEventId, setSelectedEventId] = useState<number | null>(null);

  const loadEvents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = screen === "home" ? await fetchEvents() : await fetchMyRegistrations();
      setEvents(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  }, [screen]);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const handleNavClick = () => {
    setScreen((s) => (s === "home" ? "registrations" : "home"));
  };

  const emptyMessage =
    screen === "home"
      ? "Нет предстоящих событий"
      : "Вы не зарегистрированы ни на какие события";

  return (
    <div className="app">
      <Header
        title={screen === "home" ? "События" : "Мои регистрации"}
        navIcon={screen === "home" ? "🎫" : "🏠"}
        navLabel={screen === "home" ? "Мои регистрации" : "События"}
        onNavClick={handleNavClick}
      />

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
          eventId={selectedEventId}
          onClose={() => setSelectedEventId(null)}
          onRegistrationChange={loadEvents}
        />
      )}
    </div>
  );
}

export default App;
