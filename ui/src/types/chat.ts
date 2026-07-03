export interface Attachment {
  id: string;
  type: "image";
  url: string;
}

export interface Toggles {
  webSearch?: boolean;       // Optional, depending on your app features
  deepThink?: boolean;
  [key: string]: any;        // Catch-all allowance for dynamic toggle keys
}

export interface ChatRequest {
  conversationId: string;    // The unique ID matching your backend
  message: string;       // The array of message history objects
  toggles: Toggles;          // Features enabled for the chat generation
}
