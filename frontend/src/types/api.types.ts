export type Provider = "openai" | "anthropic" | "google" | "google-gla";
export type Role = "communicator" | "receiver" | "bystander";

export interface ParticipantConfig {
  id?: string;
  name?: string;
  provider: Provider;
  role: Role;
  order?: number;
}

export interface StartSessionRequest {
  topic: string;
  secret_word?: string | null;
  participants: ParticipantConfig[];
}

export interface ParticipantInfo {
  id: string;
  name: string;
  role: Role;
  provider: Provider;
  order: number;
}

export interface StartSessionResponse {
  session_id: string;
  status: string;
  topic: string;
  participants: ParticipantInfo[];
}

export interface MessageResponse {
  participant_id: string;
  participant_name?: string;
  participant_role?: Role;
  internal_thoughts: string;
  comms: string;
}

export interface GuessResult {
  agent: string;
  correct: boolean;
  tries_remaining: number;
}

export interface NextTurnRequest {
  session_id: string;
}

export interface NextTurnResponse {
  messages: MessageResponse[];
  guess_result?: GuessResult | null;
  game_over: boolean;
  game_status?: "win" | "loss" | null;
}

export interface SessionHistoryMessage {
  turn: number;
  participant_id: string;
  participant_name?: string;
  participant_role?: Role;
  comms: string;
  internal_thoughts: string;
}

export interface SessionHistoryGuess {
  turn: number;
  participant_id: string;
  participant_name?: string;
  participant_role?: Role;
  guess: string;
  correct: boolean;
  tries_remaining: number;
}

export interface SessionHistoryResponse {
  session_id: string;
  topic: string;
  secret_word: string;
  created_at: string;
  participants: Record<string, {
    name?: string;
    role?: Role;
    provider?: Provider;
  }>;
  messages: SessionHistoryMessage[];
  guesses: SessionHistoryGuess[];
}

export interface SessionStatusResponse {
  session_id: string;
  turn_number: number;
  game_over: boolean;
  game_status: "win" | "loss" | null;
  tries_remaining: Record<string, number>;
}
