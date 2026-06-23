import { useState } from "react";
import { getDefaultCoverUrl, resolveCoverUrl } from "../api/client";
import "./CoverImage.css";

interface CoverImageProps {
  url: string | null | undefined;
  className?: string;
}

export function CoverImage({ url, className }: CoverImageProps) {
  const [usePlaceholder, setUsePlaceholder] = useState(false);
  const [src, setSrc] = useState(() => resolveCoverUrl(url));

  if (usePlaceholder) {
    return <div className={`cover-placeholder ${className ?? ""}`} aria-hidden="true" />;
  }

  return (
    <img
      src={src}
      alt=""
      className={className}
      loading="lazy"
      onError={() => {
        if (src !== getDefaultCoverUrl()) {
          setSrc(getDefaultCoverUrl());
          return;
        }
        setUsePlaceholder(true);
      }}
    />
  );
}
