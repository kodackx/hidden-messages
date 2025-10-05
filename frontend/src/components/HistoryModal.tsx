import { useState, useEffect } from 'react';
import { SessionHistoryResponse } from '@/types/api.types';
import MessageCard from './MessageCard';
import { X, Loader } from 'lucide-react';

interface HistoryModalProps {
  sessionId: string;
  onClose: () => void;
}

export default function HistoryModal({ sessionId, onClose }: HistoryModalProps) {
  const [history, setHistory] = useState<SessionHistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showThoughts, setShowThoughts] = useState(true);

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const { apiClient } = await import('@/services/api');
        const data = await apiClient.getSessionHistory(sessionId);
        setHistory(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load history');
      } finally {
        setIsLoading(false);
      }
    };

    loadHistory();
  }, [sessionId]);

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-terminal-bg/90 backdrop-blur-sm flex items-center justify-center z-50 scanlines">
        <div className="terminal-panel max-w-md">
          <div className="flex items-center justify-center gap-3">
            <Loader className="animate-spin" size={20} />
            <span className="uppercase">LOADING_HISTORY<span className="cursor-blink">_</span></span>
          </div>
        </div>
      </div>
    );
  }

  if (error || !history) {
    return (
      <div className="fixed inset-0 bg-terminal-bg/90 backdrop-blur-sm flex items-center justify-center z-50 p-4 scanlines">
        <div className="terminal-panel max-w-md border-error">
          <div className="flex justify-between items-start mb-4">
            <div className="text-error terminal-flicker uppercase font-bold">ERROR</div>
            <button onClick={onClose} className="text-primary hover:text-error transition-colors">
              <X size={20} />
            </button>
          </div>
          <p className="text-sm">{error || 'Failed to load history'}</p>
          <button onClick={onClose} className="terminal-button w-full mt-4">
            CLOSE
          </button>
        </div>
      </div>
    );
  }

  // Group messages by turn
  const turnMessages = history.messages.reduce((acc, msg) => {
    if (!acc[msg.turn]) {
      acc[msg.turn] = [];
    }
    acc[msg.turn].push(msg);
    return acc;
  }, {} as Record<number, typeof history.messages>);

  const turnGuesses = history.guesses.reduce((acc, guess) => {
    acc[guess.turn] = guess;
    return acc;
  }, {} as Record<number, typeof history.guesses[0]>);

  const turns = Object.keys(turnMessages)
    .map(Number)
    .sort((a, b) => a - b);

  return (
    <div className="fixed inset-0 bg-terminal-bg/95 backdrop-blur-sm flex items-center justify-center z-50 p-4 scanlines crt-screen">
      <div className="w-full max-w-5xl max-h-[90vh] flex flex-col terminal-panel">
        {/* Header */}
        <div className="flex justify-between items-start mb-4 pb-4 border-b border-primary">
          <div>
            <h2 className="text-xl font-bold uppercase tracking-widest text-terminal-glow mb-2">
              &gt;&gt; SESSION_HISTORY.LOG
            </h2>
            <div className="text-sm space-y-1">
              <div>
                <span className="text-muted-foreground">TOPIC:</span>{' '}
                <span className="text-primary">{history.topic}</span>
              </div>
              <div>
                <span className="text-muted-foreground">SECRET_WORD:</span>{' '}
                <span className="text-success text-terminal-glow font-bold">{history.secret_word}</span>
              </div>
              <div>
                <span className="text-muted-foreground">CREATED:</span>{' '}
                <span className="text-primary">
                  {new Date(history.created_at).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-primary hover:text-error transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Toggle */}
        <div className="mb-4">
          <button
            onClick={() => setShowThoughts(!showThoughts)}
            className={`terminal-button ${showThoughts ? 'bg-primary text-background' : ''}`}
          >
            REVEAL_THOUGHTS:{showThoughts ? '▓' : '░'}
          </button>
        </div>

        {/* Conversation */}
        <div className="flex-1 overflow-y-auto pr-2 space-y-6">
          {turns.map((turnNum) => {
            const messages = turnMessages[turnNum];
            const guess = turnGuesses[turnNum];

            return (
              <div key={turnNum} className="space-y-3">
                <div className="text-xs text-muted-foreground uppercase border-b border-muted pb-1">
                  [TURN_{String(turnNum).padStart(3, '0')}]
                </div>

                {messages.map((msg, idx) => (
                  <MessageCard
                    key={`${turnNum}-${idx}`}
                    message={{
                      participant_id: msg.participant_id,
                      participant_name: msg.participant_name,
                      participant_role: msg.participant_role,
                      comms: msg.comms,
                      internal_thoughts: msg.internal_thoughts,
                    }}
                    showThoughts={showThoughts}
                    turnNumber={turnNum}
                  />
                ))}

                {guess && (
                  <div className="border border-system p-3 rounded-sm bg-system/10">
                    <div className="text-system-glow text-sm font-bold uppercase mb-1">
                      &gt;&gt;&gt; GUESS_SUBMITTED: "{guess.guess}"
                    </div>
                    <div className="text-xs space-y-1">
                      <div>
                        <span className="text-muted-foreground">AGENT:</span>{' '}
                        <span className="text-receiver-glow">{guess.participant_name || guess.participant_id.slice(0, 8)}</span>
                      </div>
                      <div className={guess.correct ? 'text-success' : 'text-error'}>
                        &gt;&gt;&gt; [{guess.correct ? 'SUCCESS' : 'ERROR'}]{' '}
                        {guess.correct ? 'CORRECT' : 'INCORRECT'}
                      </div>
                      {!guess.correct && (
                        <div>
                          <span className="text-muted-foreground">TRIES_REMAINING:</span>{' '}
                          <span className={guess.tries_remaining > 0 ? 'text-primary' : 'text-error terminal-flicker'}>
                            {guess.tries_remaining}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="mt-4 pt-4 border-t border-primary">
          <button onClick={onClose} className="terminal-button w-full">
            &gt; [CLOSE_HISTORY]
          </button>
        </div>
      </div>
    </div>
  );
}
