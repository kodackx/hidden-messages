import { useState, useEffect, useRef } from 'react';
import { NextTurnResponse, GuessResult, ParticipantInfo } from '@/types/api.types';
import MessageCard from './MessageCard';
import ParticipantList from './ParticipantList';
import GameStatus from './GameStatus';

import Footer from './Footer';
import { Eye, EyeOff, Home, Users } from 'lucide-react';
import { APP_VERSION } from '@/lib/constants';

interface ConversationViewProps {
  sessionId: string;
  topic: string;
  participants: ParticipantInfo[];
  onNewSession: () => void;
  onViewHistory: () => void;
  onGoHome: () => void;
}

interface TurnData {
  turnNumber: number;
  messages: NextTurnResponse['messages'];
  guessResult?: GuessResult | null;
}

export default function ConversationView({
  sessionId,
  topic,
  participants,
  onNewSession,
  onViewHistory,
  onGoHome,
}: ConversationViewProps) {
  const [turns, setTurns] = useState<TurnData[]>([]);
  const [showThoughts, setShowThoughts] = useState(false);
  const [gameOver, setGameOver] = useState(false);
  const [gameStatus, setGameStatus] = useState<'win' | 'loss' | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [triesRemaining, setTriesRemaining] = useState<Record<string, number>>({});
  const [secretWord, setSecretWord] = useState<string | null>(null);
  const [showAgentDetails, setShowAgentDetails] = useState(false);
  const conversationEndRef = useRef<HTMLDivElement>(null);
  const [historyLoaded, setHistoryLoaded] = useState(false);

  useEffect(() => {
    // Load existing history when resuming a session
    const loadHistory = async () => {
      if (historyLoaded) return;
      
      try {
        const { apiClient } = await import('@/services/api');
        const history = await apiClient.getSessionHistory(sessionId);
        
        // Group messages by turn
        const turnMap = new Map<number, TurnData>();

        setSecretWord(history.secret_word || null);
        
        history.messages.forEach(msg => {
          if (!turnMap.has(msg.turn)) {
            turnMap.set(msg.turn, {
              turnNumber: msg.turn,
              messages: [],
              guessResult: undefined,
            });
          }
          turnMap.get(msg.turn)!.messages.push({
            participant_id: msg.participant_id,
            participant_name: msg.participant_name,
            participant_role: msg.participant_role,
            comms: msg.comms,
            internal_thoughts: msg.internal_thoughts,
          });
        });
        
        // Add guess results
        history.guesses.forEach(guess => {
          if (turnMap.has(guess.turn)) {
            turnMap.get(guess.turn)!.guessResult = {
              agent: guess.participant_id,
              correct: guess.correct,
              tries_remaining: guess.tries_remaining,
            };
          }
        });
        
        // Convert to array and sort by turn
        const loadedTurns = Array.from(turnMap.values()).sort((a, b) => a.turnNumber - b.turnNumber);
        setTurns(loadedTurns);
        
        // Get status to update tries remaining and game state
        const status = await apiClient.getSessionStatus(sessionId);
        setTriesRemaining(status.tries_remaining);
        setGameOver(status.game_over);
        setGameStatus(status.game_status);
        
        setHistoryLoaded(true);
      } catch (err) {
        console.error('Failed to load history:', err);
        // Initialize tries for new session
        const receiver = participants.find(p => p.role === 'receiver');
        if (receiver) {
          setTriesRemaining({ [receiver.id]: 3 });
        }
        setHistoryLoaded(true);
        setSecretWord(null);
      }
    };
    
    loadHistory();
  }, [sessionId, historyLoaded, participants]);

  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [turns]);

  const handleNextTurn = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const { apiClient } = await import('@/services/api');
      const response = await apiClient.nextTurn({ session_id: sessionId });

      const newTurn: TurnData = {
        turnNumber: turns.length + 1,
        messages: response.messages,
        guessResult: response.guess_result,
      };

      setTurns([...turns, newTurn]);

      // Update tries remaining
      if (response.guess_result) {
        setTriesRemaining({
          ...triesRemaining,
          [response.guess_result.agent]: response.guess_result.tries_remaining,
        });
      }

      if (response.game_over) {
        setGameOver(true);
        setGameStatus(response.game_status || null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute turn');
    } finally {
      setIsLoading(false);
    }
  };

  const currentTurnNumber = turns.length;

  return (
    <div className="min-h-screen p-4 scanlines crt-screen">
      <div className="max-w-6xl mx-auto space-y-4">
        {/* Header */}
        <div className="terminal-panel">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-xl font-bold uppercase tracking-widest text-terminal-glow">
                HIDDEN_MESSAGES v{APP_VERSION}
              </h1>
              <p className="text-sm mt-1">
                <span className="text-muted-foreground uppercase">TOPIC:</span>{' '}
                <span className="text-primary">{topic}</span>
              </p>
              {showThoughts && secretWord && (
                <p className="text-xs mt-1">
                  <span className="text-muted-foreground uppercase">SECRET WORD:</span>{' '}
                  <span className="text-system-glow uppercase">{secretWord}</span>
                </p>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={onGoHome}
                className="terminal-button flex items-center gap-2"
              >
                <Home size={16} />
                HOME
              </button>
              <button
                onClick={() => setShowAgentDetails(!showAgentDetails)}
                className={`terminal-button flex items-center gap-2 ${showAgentDetails ? 'bg-system text-background' : ''}`}
              >
                <Users size={16} />
                AGENT_DETAILS
              </button>
              <button
                onClick={() => setShowThoughts(!showThoughts)}
                className={`terminal-button flex items-center gap-2 ${showThoughts ? 'bg-primary text-background' : ''}`}
              >
                {showThoughts ? <Eye size={16} /> : <EyeOff size={16} />}
                REVEAL_THOUGHTS:{showThoughts ? '▓' : '░'}
              </button>
            </div>
          </div>
          {showAgentDetails && (
            <div className="mt-4 border-t border-muted pt-4">
              <ParticipantList participants={participants} triesRemaining={triesRemaining} compact />
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="terminal-panel border-error bg-destructive/10">
            <div className="text-error terminal-flicker uppercase font-bold">
              ERROR: {error}
            </div>
          </div>
        )}

        {/* Game Over Banner */}
        {gameOver && (
          <div className={`terminal-panel ${gameStatus === 'win' ? 'border-success' : 'border-error'}`}>
            <div className="text-center">
              <div className={`text-2xl font-bold uppercase mb-4 ${gameStatus === 'win' ? 'text-success' : 'text-error terminal-flicker'}`}>
                ███ GAME_OVER ███ RESULT: {gameStatus === 'win' ? 'SUCCESS' : 'FAILURE'} ███
              </div>
              <div className="space-y-2 text-sm">
                {gameStatus === 'win' ? (
                  <>
                    <div>&gt;&gt;&gt; OBJECTIVE_COMPLETE</div>
                    <div>&gt;&gt;&gt; RECEIVER_STATUS: SUCCESS</div>
                  </>
                ) : (
                  <>
                    <div>&gt;&gt;&gt; OBJECTIVE_FAILED</div>
                    <div>&gt;&gt;&gt; TRIES_EXHAUSTED: 3/3</div>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
        {/* Conversation */}
        <div className={`terminal-panel transition-opacity ${isLoading ? 'opacity-50' : 'opacity-100'}`}>
          <div className="text-sm uppercase tracking-wide mb-4 text-terminal-glow">
            &gt;&gt; CONVERSATION.LOG
            {isLoading && <span className="ml-2 cursor-blink text-xs">PROCESSING_TURN...</span>}
          </div>

          {turns.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <p className="uppercase text-sm">Standing by for agent chatter.</p>
              <p className="text-xs mt-2">Trigger NEXT_TURN to engage the agents.</p>
              <span className="inline-block mt-2 cursor-blink">█</span>
            </div>
          ) : (
            <div className="space-y-6 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
              {turns.map((turn) => (
                <div key={turn.turnNumber} className="space-y-3">
                  <div className="text-xs text-muted-foreground uppercase border-b border-muted pb-1">
                    [TURN_{String(turn.turnNumber).padStart(3, '0')}]
                  </div>

                  {turn.messages.map((message, idx) => (
                    <MessageCard
                      key={`${turn.turnNumber}-${idx}`}
                      message={message}
                      showThoughts={showThoughts}
                      turnNumber={turn.turnNumber}
                    />
                  ))}

                  {turn.guessResult && (
                    <div className="border border-system p-3 rounded-sm bg-system/10">
                      <div className="text-system-glow text-sm font-bold uppercase mb-1">
                        &gt;&gt;&gt; GUESS_SUBMITTED
                      </div>
                      <div className="text-xs space-y-1">
                        <div>
                          <span className="text-muted-foreground">AGENT:</span>{' '}
                          <span className="text-receiver-glow">{turn.guessResult.agent.slice(0, 8)}</span>
                        </div>
                        <div className={turn.guessResult.correct ? 'text-success' : 'text-error'}>
                          &gt;&gt;&gt; [{turn.guessResult.correct ? 'SUCCESS' : 'ERROR'}]{' '}
                          {turn.guessResult.correct ? 'CORRECT' : 'INCORRECT'}
                        </div>
                        {!turn.guessResult.correct && (
                          <div>
                            <span className="text-muted-foreground">TRIES_REMAINING:</span>{' '}
                            <span className={turn.guessResult.tries_remaining > 0 ? 'text-primary' : 'text-error terminal-flicker'}>
                              {turn.guessResult.tries_remaining}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              <div ref={conversationEndRef} />
            </div>
           )}
        </div>

        {/* Game Status */}
        <GameStatus
          turnNumber={currentTurnNumber}
          gameOver={gameOver}
          gameStatus={gameStatus}
          onNextTurn={handleNextTurn}
          onViewHistory={onViewHistory}
          onNewSession={onNewSession}
          isLoading={isLoading}
        />

        {/* Game Over Banner */}
        {gameOver && (
          <div className={`terminal-panel ${gameStatus === 'win' ? 'border-success' : 'border-error'}`}>
            <div className="text-center">
              <div className={`text-2xl font-bold uppercase mb-4 ${gameStatus === 'win' ? 'text-success' : 'text-error terminal-flicker'}`}>
                ███ GAME_OVER ███ RESULT: {gameStatus === 'win' ? 'SUCCESS' : 'FAILURE'} ███
              </div>
              <div className="space-y-2 text-sm">
                {gameStatus === 'win' ? (
                  <>
                    <div>&gt;&gt;&gt; OBJECTIVE_COMPLETE</div>
                    <div>&gt;&gt;&gt; RECEIVER_STATUS: SUCCESS</div>
                  </>
                ) : (
                  <>
                    <div>&gt;&gt;&gt; OBJECTIVE_FAILED</div>
                    <div>&gt;&gt;&gt; TRIES_EXHAUSTED: 3/3</div>
                  </>
                )}
              </div>
            </div>
          </div>
        )}

        <Footer />
      </div>
    </div>
  );
}
