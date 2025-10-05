import { getApiMode } from '@/services/api';
import { APP_VERSION } from '@/lib/constants';

const Footer = () => {
  const apiMode = getApiMode();
  
  return (
    <div className="mt-8 text-center text-terminal-green-dim text-sm">
      <div className="mb-4 flex items-center justify-center gap-2">
        <div className="h-px bg-terminal-green-dim/30 flex-1"></div>
        <span className="text-xs">///</span>
        <div className="h-px bg-terminal-green-dim/30 flex-1"></div>
      </div>
      <p className="uppercase tracking-wider">
        [HIDDEN_MESSAGES_PROJECT_2025] v{APP_VERSION}
      </p>
      <p className="mt-1 text-xs">
        <span className={apiMode === 'mock' ? 'text-system-glow' : 'text-communicator-glow'}>
          [{apiMode === 'mock' ? 'MOCK_MODE' : 'LIVE_API'}]
        </span>
      </p>
    </div>
  );
};

export default Footer;
