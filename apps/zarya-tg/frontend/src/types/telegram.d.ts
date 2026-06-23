export {};

declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        initData: string;
        colorScheme?: "light" | "dark";
        ready: () => void;
        expand: () => void;
        setHeaderColor: (color: string) => void;
        setBackgroundColor: (color: string) => void;
        openLink: (url: string) => void;
        downloadFile?: (
          params: { url: string; file_name: string },
          callback?: (accepted: boolean) => void,
        ) => void;
        requestFullscreen?: () => void;
        onEvent?: (eventType: string, callback: () => void) => void;
        offEvent?: (eventType: string, callback: () => void) => void;
        safeAreaInset?: { top: number; bottom: number; left: number; right: number };
        contentSafeAreaInset?: { top: number; bottom: number; left: number; right: number };
      };
    };
  }
}
