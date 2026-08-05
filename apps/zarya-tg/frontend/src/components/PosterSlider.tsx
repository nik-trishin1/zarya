import { useEffect, useRef, useState } from "react";
import type { Event } from "../api/client";
import { formatEventDate } from "../utils/format";
import { CoverImage } from "./CoverImage";
import "./PosterSlider.css";

interface PosterSliderProps {
  events: Event[];
  onSelect: (event: Event) => void;
}

export function PosterSlider({ events, onSelect }: PosterSliderProps) {
  const trackRef = useRef<HTMLDivElement>(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const showDots = events.length > 1;

  useEffect(() => {
    const track = trackRef.current;
    if (!track || !showDots) return;

    const handleScroll = () => {
      const width = track.clientWidth;
      if (width <= 0) return;
      const index = Math.round(track.scrollLeft / width);
      setActiveIndex(Math.min(Math.max(index, 0), events.length - 1));
    };

    track.addEventListener("scroll", handleScroll, { passive: true });
    return () => track.removeEventListener("scroll", handleScroll);
  }, [events.length, showDots]);

  if (events.length === 0) return null;

  return (
    <section className="poster-slider" aria-label="Избранные события">
      <div
        ref={trackRef}
        className={`poster-slider__track${showDots ? "" : " poster-slider__track--single"}`}
      >
        {events.map((event) => (
          <button
            key={event.event_id}
            type="button"
            className="poster-slider__slide"
            onClick={() => onSelect(event)}
            aria-label={`Открыть ${event.name}`}
          >
            <CoverImage url={event.cover_image_url} className="poster-slider__image" />
            <div className="poster-slider__overlay">
              <time className="poster-slider__date">{formatEventDate(event.date, event.time)}</time>
              <h2 className="poster-slider__title">{event.name}</h2>
            </div>
          </button>
        ))}
      </div>
      {showDots && (
        <div className="poster-slider__dots" aria-hidden="true">
          {events.map((event, index) => (
            <span
              key={event.event_id}
              className={`poster-slider__dot${index === activeIndex ? " is-active" : ""}`}
            />
          ))}
        </div>
      )}
    </section>
  );
}
