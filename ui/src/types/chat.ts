export interface Attachment {
  id: string;
  type: "image";
  url: string;
}

export interface Toggles {
  webSearch?: boolean;
  deepThink?: boolean;
  [key: string]: any;
}

export interface ChatRequest {
  conversationId: string; 
  message: string; 
  toggles: Toggles;
  attachments?: Attachment[]
}

export interface ChatResponse {
  content: string
}