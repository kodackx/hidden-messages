import { ArrowRight, History, RotateCcw } from 'lucide-react';

interface GameStatusProps {
  turnNumber: number;
  gameOver: boolean;
  gameStatus: 'win' | 'loss' | null;
  onNextTurn: () => void;
  onViewHistory: () => void;
  onNewSession: () => void;
  isLoading: boolean;
}

export default function GameStatus({
  turnNumber,
  gameOver,
  gameStatus,
  onNextTurn,
  onViewHistory,
  onNewSession,
  isLoading,
}: GameStatusProps) {
  return (
    <div className="terminal-panel">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
        <div className="flex items-center gap-4">
          <div className="text-sm">
            <span className="text-muted-foreground uppercase">TURN:</span>{' '}
            <span className="text-primary text-terminal-glow font-bold">
              {String(turnNumber).padStart(3, '0')}
            </span>
          </div>
          <div className="text-muted-foreground">|</div>
          <div className="text-sm">
            <span className="text-muted-foreground uppercase">STATUS:</span>{' '}
            <span className={`uppercase font-bold ${gameOver ? 'text-error terminal-flicker' : 'text-success'}`}>
              {gameOver ? 'COMPLETE' : 'IN_PROGRESS'}
            </span>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={onNextTurn}
            disabled={gameOver || isLoading}
            className="terminal-button-accent flex items-center gap-2"
          >
            <ArrowRight size={14} />
            {isLoading ? (
              <>PROCESSING<span className="cursor-blink">_</span></>
            ) : (
              'EXEC: NEXT_TURN'
            )}
          </button>
          <button
            onClick={onViewHistory}
            className="terminal-button flex items-center gap-2"
          >
            <History size={14} />
            FULL_HISTORY
          </button>
          <button
            onClick={onNewSession}
            className="terminal-button flex items-center gap-2"
          >
            <RotateCcw size={14} />
            NEW_SESSION
          </button>
        </div>
      </div>
    </div>
  );
}
