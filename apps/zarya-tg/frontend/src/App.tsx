import { useState } from "react";
import type { Event } from "./api/client";
import { EventDetails } from "./components/EventDetails";
import { Header } from "./components/Header";
import { useEventsCache } from "./hooks/useEventsCache";
import { useTelegram } from "./hooks/useTelegram";
import { HomeScreen, RegistrationsScreen, ScreenEmptyState } from "./routes";
import { getTelegramStartParam, parseEventStartParam } from "./utils/deepLink";
import "./App.css";

function App() {
  useTelegram();
  const {
    screen,
    events,
    archiveEvents,
    registrationCount,
    loading,
    error,
    handleRegistrationChange,
    toggleScreen,
  } = useEventsCache();
  const [selectedEventId, setSelectedEventId] = useState<number | null>(() =>
    parseEventStartParam(getTelegramStartParam()),
  );
  const [selectedFromArchive, setSelectedFromArchive] = useState(false);

  const handleEventSelect = (event: Event, fromArchive = false) => {
    setSelectedFromArchive(fromArchive);
    setSelectedEventId(event.event_id);
  };

  const hasUpcoming = events.length > 0;
  const hasArchive = screen === "registrations" && archiveEvents.length > 0;
  const showEmptyState = !loading && !error && !hasUpcoming && !hasArchive;

  return (
    <div className="app">
      <Header screen={screen} registrationCount={registrationCount} onNavClick={toggleScreen} />

      <main className="app__main">
        {loading && <p className="app__status">Загрузка...</p>}
        {error && <p className="app__status app__status--error">{error}</p>}
        {showEmptyState && <ScreenEmptyState screen={screen} />}
        {!loading && !error && screen === "home" && hasUpcoming && (
          <HomeScreen events={events} onSelect={handleEventSelect} />
        )}
        {!loading && !error && screen === "registrations" && (hasUpcoming || hasArchive) && (
          <RegistrationsScreen
            events={events}
            archiveEvents={archiveEvents}
            onSelect={handleEventSelect}
          />
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
