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
        downloadFile: (
          params: { url: string; file_name: string },
          callback?: (accepted: boolean) => void,
        ) => void;
        isVersionAtLeast: (version: string) => boolean;
      };
    };
  }
}
