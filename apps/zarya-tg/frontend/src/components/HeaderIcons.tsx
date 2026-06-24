interface IconProps {
  className?: string;
}

export function TicketIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" width="18" height="18" aria-hidden="true">
      <path
        fill="currentColor"
        d="M4 5.5A1.5 1.5 0 0 1 5.5 4h9A1.5 1.5 0 0 1 16 5.5V7a1 1 0 0 0 0 2v3.5a1 1 0 0 0 0 2V16a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 4 16v-1.5a1 1 0 0 0 0-2V9a1 1 0 0 0 0-2V5.5Zm2 .25v1.06a2.5 2.5 0 0 1 0 4.88V14.5h8V11.7a2.5 2.5 0 0 1 0-3.4V5.75H6Z"
      />
    </svg>
  );
}

export function HomeIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" width="18" height="18" aria-hidden="true">
      <path
        fill="currentColor"
        d="M10 3.2 3.75 8.4a.75.75 0 0 0-.25.56V15.5c0 .69.56 1.25 1.25 1.25H8v-4.25a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1V16.75h3.25c.69 0 1.25-.56 1.25-1.25V8.96a.75.75 0 0 0-.25-.56L10 3.2Z"
      />
    </svg>
  );
}
