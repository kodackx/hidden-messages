import { useState, useEffect } from 'react';
import { SessionListItem } from '@/types/api.types';
import { Clock, MessageSquare, CheckCircle2, XCircle, Play } from 'lucide-react';
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

  const handleResumeClick = (sessionId: string) => {
    setResumingSessionId(sessionId);
    onResumeSession(sessionId);
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
    <div className="terminal-panel mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg uppercase tracking-wide text-terminal-glow">
          &gt;&gt; PREVIOUS_SESSIONS
        </h2>
        <span className="text-xs text-muted-foreground uppercase">
          [{sessions.length} FOUND]
        </span>
      </div>

      <div className="space-y-3 max-h-[300px] overflow-y-auto custom-scrollbar">
        {sessions.map((session) => {
          const isThisSessionResuming = resumingSessionId === session.session_id;
          return (
          <div
            key={session.session_id}
            className={`border border-muted p-3 transition-all group ${
              isResuming && !isThisSessionResuming ? 'opacity-50 cursor-not-allowed' : 'hover:border-terminal-green-dim cursor-pointer'
            }`}
            onClick={() => !isResuming && handleResumeClick(session.session_id)}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-sm font-bold text-terminal-green truncate">
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
                    <span className="text-xs px-1.5 py-0.5 border border-system text-system-glow">
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

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (!isResuming) handleResumeClick(session.session_id);
                }}
                disabled={isResuming}
                className="flex items-center gap-1 px-2 py-1 border border-terminal-green-dim text-terminal-green-dim hover:bg-terminal-green-dim/10 transition-colors text-xs uppercase opacity-0 group-hover:opacity-100 disabled:opacity-50"
              >
                {isThisSessionResuming ? (
                  <>
                    <span className="cursor-blink">LOADING</span>
                  </>
                ) : (
                  <>
                    <Play size={12} />
                    <span>RESUME</span>
                  </>
                )}
              </button>
            </div>
          </div>
          );
        })}
      </div>
      
      {/* Loading Overlay */}
      {isResuming && resumingSessionId && (
        <div className="mt-4 border border-terminal-green p-4 bg-terminal-green/5 animate-pulse">
          <div className="flex items-center justify-center gap-2 text-terminal-glow uppercase tracking-wide text-sm">
            <span>&gt;&gt;&gt; LOADING SESSION DATA</span>
            <span className="cursor-blink">_</span>
          </div>
          <p className="text-center text-xs text-terminal-green-dim mt-2 uppercase">
            PLEASE WAIT, DO NOT NAVIGATE AWAY
          </p>
        </div>
      )}
    </div>
  );
}
