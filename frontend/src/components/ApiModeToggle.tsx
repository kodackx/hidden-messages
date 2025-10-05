import { useState, useEffect } from 'react';
import { getApiMode, setApiMode } from '@/services/api';
import { Server, Cpu } from 'lucide-react';

export default function ApiModeToggle() {
  const [currentMode, setCurrentMode] = useState<'mock' | 'real'>(getApiMode());
  const [showTooltip, setShowTooltip] = useState(false);

  useEffect(() => {
    setCurrentMode(getApiMode());
  }, []);

  const handleToggle = () => {
    const newMode = currentMode === 'mock' ? 'real' : 'mock';
    setApiMode(newMode);
    // Page will reload automatically via setApiMode
  };

  return (
    <div className="fixed top-4 right-4 z-50">
      <div className="terminal-panel border-2 p-2">
        <button
          onClick={handleToggle}
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
          className={`flex items-center gap-2 px-3 py-2 border transition-all ${
            currentMode === 'mock'
              ? 'border-system text-system-glow bg-system/10'
              : 'border-communicator text-communicator-glow bg-communicator/10'
          }`}
        >
          {currentMode === 'mock' ? (
            <>
              <Cpu size={16} className="animate-pulse" />
              <span className="text-xs uppercase font-bold">MOCK</span>
            </>
          ) : (
            <>
              <Server size={16} />
              <span className="text-xs uppercase font-bold">LIVE</span>
            </>
          )}
        </button>

        {showTooltip && (
          <div className="absolute top-full right-0 mt-2 terminal-panel text-xs max-w-xs border-2 border-primary">
            <div className="font-bold uppercase mb-2 text-terminal-glow">
              &gt;&gt; API_MODE
            </div>
            <div className="space-y-1 text-muted-foreground">
              {currentMode === 'mock' ? (
                <>
                  <p>&gt; CURRENT: MOCK_DATA</p>
                  <p>&gt; Using simulated responses</p>
                  <p>&gt; No backend required</p>
                  <p className="text-system-glow pt-2">
                    Click to switch to LIVE backend
                  </p>
                </>
              ) : (
                <>
                  <p>&gt; CURRENT: LIVE_BACKEND</p>
                  <p>&gt; Connecting to API server</p>
                  <p>&gt; Requires backend running</p>
                  <p className="text-communicator-glow pt-2">
                    Click to switch to MOCK mode
                  </p>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
