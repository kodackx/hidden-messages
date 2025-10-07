import { useState, useEffect } from 'react';
import { SessionListItem } from '@/types/api.types';
import { Clock, MessageSquare, XCircle } from 'lucide-react';
import { apiClient } from '@/services/api';
import { toast } from 'sonner';

interface SessionListProps {
  onResumeSession: (sessionId: string) => void;
  isResuming?: boolean;
}

export default function SessionList({ onResumeSession, isResuming = false }: SessionListProps) {
  const [sessions, setSessions] = useState<SessionListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resumingSessionId, setResumingSessionId] = useState<string | null>(null);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiClient.listSessions();
      setSessions(response.sessions);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load sessions';
      setError(errorMsg);
      toast.error('Error loading sessions', { description: errorMsg });
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  useEffect(() => {
    if (!isResuming) {
      setResumingSessionId(null);
    }
  }, [isResuming]);

  const handleSessionSelect = (sessionId: string) => {
    if (isResuming) return;
    setSelectedSessionId(sessionId);
  };

  const handleResumeExecute = () => {
    if (!selectedSessionId) return;
    setResumingSessionId(selectedSessionId);
    onResumeSession(selectedSessionId);
  };

  if (isLoading) {
    return (
      <div className="terminal-panel mb-6">
        <div className="flex items-center justify-center py-8">
          <div className="text-terminal-glow uppercase tracking-wide animate-pulse">
            &gt; LOADING SESSIONS<span className="cursor-blink">_</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="terminal-panel mb-6 border-error/50">
        <div className="flex items-center gap-2 text-error text-sm">
          <XCircle size={16} />
          <span>ERROR: {error}</span>
        </div>
      </div>
    );
  }

  if (sessions.length === 0) {
    return null;
  }

  return (
    <div className="terminal-panel mb-6 border-[hsl(var(--receiver))]/50 bg-[hsl(var(--receiver))]/5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg uppercase tracking-wide text-receiver-glow">
          &gt;&gt; PREVIOUS_SESSIONS
        </h2>
        <span className="text-xs text-muted-foreground uppercase">
          [{sessions.length} FOUND]
        </span>
      </div>

      <div className="space-y-3 max-h-[300px] overflow-y-auto custom-scrollbar">
        {sessions.map((session) => {
          const isSelected = selectedSessionId === session.session_id;
          const isThisSessionResuming = resumingSessionId === session.session_id;
          return (
          <div
            key={session.session_id}
            className={`border p-3 transition-all group ${
              isSelected
                ? 'border-[hsl(var(--receiver))] bg-[hsl(var(--receiver))]/10 shadow-[0_0_12px_hsla(var(--receiver),0.25)]'
                : 'border-[hsl(var(--receiver))]/30 bg-transparent'
            } ${
              isResuming && !isThisSessionResuming
                ? 'opacity-50 cursor-not-allowed'
                : 'hover:border-[hsl(var(--receiver))] hover:bg-[hsl(var(--receiver))]/10 cursor-pointer'
            }`}
            onClick={() => handleSessionSelect(session.session_id)}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-sm font-bold text-[hsl(var(--receiver))] truncate">
                    {session.topic}
                  </h3>
                  {session.game_over && (
                    <span className={`text-xs px-1.5 py-0.5 border ${
                      session.game_status === 'success'
                        ? 'border-success text-success-glow'
                        : 'border-error text-error-glow'
                    }`}>
                      {session.game_status === 'success' ? 'WON' : 'LOST'}
                    </span>
                  )}
                  {!session.game_over && (
                    <span className="text-xs px-1.5 py-0.5 border border-[hsl(var(--receiver))]/70 text-[hsl(var(--receiver))]">
                      IN PROGRESS
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Clock size={12} />
                    <span>{formatDate(session.created_at)}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <MessageSquare size={12} />
                    <span>{session.message_count} msgs</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="uppercase tracking-wide">
                      ID: {session.session_id.slice(0, 8)}...
                    </span>
                  </div>
                </div>
              </div>
              {isSelected && !isResuming && (
                <span className="text-xs px-2 py-1 border border-[hsl(var(--receiver))] text-[hsl(var(--receiver))] uppercase tracking-wide">
                  SELECTED
                </span>
              )}
              {isThisSessionResuming && (
                <span className="text-xs px-2 py-1 border border-[hsl(var(--receiver))] text-[hsl(var(--receiver))] uppercase tracking-wide animate-pulse">
                  RESUMING
                </span>
              )}
            </div>
          </div>
          );
        })}
      </div>

      <button
        onClick={handleResumeExecute}
        disabled={!selectedSessionId || isResuming}
        className={`terminal-button-receiver w-full mt-4 py-4 text-lg font-bold uppercase tracking-wide transition-transform disabled:opacity-100 disabled:cursor-not-allowed flex items-center justify-center ${
          !selectedSessionId || isResuming ? '' : 'animate-pulse hover:animate-none hover:scale-[1.02]'
        } ${isResuming && resumingSessionId ? 'flex-col gap-3 items-start px-6 text-left bg-[hsl(var(--receiver))] text-[hsl(var(--terminal-bg))]' : ''}`}
      >
        {isResuming && resumingSessionId ? (
          <div className="w-full space-y-2">
            <div className="flex items-center justify-between text-xs tracking-widest">
              <span>&gt;&gt;&gt; RESUME_SESSION</span>
              <span>ID {resumingSessionId.slice(0, 8)}...</span>
            </div>
            <div className="flex flex-col gap-1 text-sm font-normal">
              <span className="inline-flex items-center gap-2">
                <span className="animate-pulse">RUNNING</span>
                <span>hidden_messages resume --wait</span>
              </span>
              <span className="text-xs uppercase tracking-wide">
                Stand by while we load the conversation
              </span>
            </div>
          </div>
        ) : (
          <>&gt; [EXECUTE: RESUME_SESSION]</>
        )}
      </button>
    </div>
  );
}
