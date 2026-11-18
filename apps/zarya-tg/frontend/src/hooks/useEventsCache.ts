import { useCallback, useEffect, useRef, useState } from "react";
import type { Event } from "../api/client";
import { fetchEvents, fetchMyArchive, fetchMyRegistrations } from "../api/client";
import type { Screen } from "../routes";

type ScreenCache = {
  home: Event[] | null;
  registrations: { events: Event[]; archive: Event[] } | null;
};

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

export function useEventsCache() {
  const [screen, setScreen] = useState<Screen>("home");
  const [events, setEvents] = useState<Event[]>([]);
  const [archiveEvents, setArchiveEvents] = useState<Event[]>([]);
  const [registrationCount, setRegistrationCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
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

  const toggleScreen = useCallback(() => {
    setScreen((s) => (s === "home" ? "registrations" : "home"));
  }, []);

  return {
    screen,
    events,
    archiveEvents,
    registrationCount,
    loading,
    error,
    handleRegistrationChange,
    toggleScreen,
  };
}
