import { linkifyText } from "../utils/linkify";
import { openExternalUrl } from "../utils/telegram";

interface LinkifiedTextProps {
  text?: string | null;
  className?: string;
}

export function LinkifiedText({ text, className }: LinkifiedTextProps) {
  const trimmed = text?.trim();
  if (!trimmed) {
    return null;
  }

  const segments = linkifyText(trimmed);

  return (
    <p className={className}>
      {segments.map((segment, index) => {
        if (segment.type === "text") {
          return <span key={index}>{segment.value}</span>;
        }

        return (
          <a
            key={index}
            href={segment.href}
            className="linkified-text__link"
            onClick={(event) => {
              event.preventDefault();
              openExternalUrl(segment.href);
            }}
          >
            {segment.value}
          </a>
        );
      })}
    </p>
  );
}
