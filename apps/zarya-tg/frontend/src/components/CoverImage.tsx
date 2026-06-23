import { useState } from "react";
import { resolveCoverUrl } from "../api/client";
import "./CoverImage.css";

interface CoverImageProps {
  url: string | null | undefined;
  className?: string;
}

export function CoverImage({ url, className }: CoverImageProps) {
  const [failed, setFailed] = useState(false);
  const coverSrc = resolveCoverUrl(url);

  if (!coverSrc || failed) {
    return <div className={`cover-placeholder ${className ?? ""}`} aria-hidden="true" />;
  }

  return (
    <img
      src={coverSrc}
      alt=""
      className={className}
      loading="lazy"
      onError={() => setFailed(true)}
    />
  );
}
