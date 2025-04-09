export { };

declare global {
    interface Window {
        Telegram: {
            WebApp: {
                initData: string;
                initDataUnsafe: {
                    query_id?: string;
                    user?: {
                        id: number;
                        first_name?: string;
                        last_name?: string;
                        username?: string;
                        language_code?: string;
                    };
                    receiver?: {
                        id: number;
                        type: string;
                    };
                    auth_date?: number;
                    hash?: string;
                };
                version: string;
                platform: string;
                colorScheme: "light" | "dark";
                themeParams: {
                    background_color?: string;
                    text_color?: string;
                    hint_color?: string;
                    link_color?: string;
                    button_color?: string;
                    button_text_color?: string;
                };
                isExpanded: boolean;
                isClosingConfirmationEnabled: boolean;
                headerColor: string;
                backgroundColor: string;
                BackButton: {
                    isVisible: boolean;
                    onClick: (callback: () => void) => void;
                    offClick: (callback: () => void) => void;
                    show: () => void;
                    hide: () => void;
                };
                MainButton: {
                    text: string;
                    color?: string;
                    textColor?: string;
                    isVisible: boolean;
                    isActive: boolean;
                    isProgressVisible: boolean;
                    setText: (text: string) => void;
                    onClick: (callback: () => void) => void;
                    offClick: (callback: () => void) => void;
                    show: () => void;
                    hide: () => void;
                    enable: () => void;
                    disable: () => void;
                    showProgress: (leaveActiveState?: boolean) => void;
                    hideProgress: () => void;
                };
                HapticFeedback: {
                    impactOccurred: (style: "light" | "medium" | "heavy" | "rigid" | "soft") => void;
                    notificationOccurred: (type: "error" | "success" | "warning") => void;
                    selectionChanged: () => void;
                };
            };
        };
    }
}
