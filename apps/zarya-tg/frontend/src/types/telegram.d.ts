export {};

declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        initData: string;
        ready: () => void;
        expand: () => void;
        setHeaderColor: (color: string) => void;
        setBackgroundColor: (color: string) => void;
        openLink: (url: string) => void;
        isVersionAtLeast: (version: string) => boolean;
      };
    };
  }
}
