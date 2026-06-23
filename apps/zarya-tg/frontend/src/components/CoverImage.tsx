import { useState } from "react";
import { getDefaultCoverUrl, resolveCoverUrl } from "../api/client";

interface CoverImageProps {
  url: string | null | undefined;
  className?: string;
}

export function CoverImage({ url, className }: CoverImageProps) {
  const [src, setSrc] = useState(() => resolveCoverUrl(url));

  return (
    <img
      src={src}
      alt=""
      className={className}
      loading="lazy"
      onError={() => setSrc(getDefaultCoverUrl())}
    />
  );
}
