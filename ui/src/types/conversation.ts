export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
}

export interface Message{
  id: number;
  role: string;
  conent: string;
  attachments: Attachment[]
}

export interface Attachment{
  url: string;
  name: string;
}

export interface ConversationsResponse {
  items: Conversation[]
}

export interface ConversationResponse {
  data: Conversation
}