import { ParticipantInfo, Role } from '@/types/api.types';

interface ParticipantListProps {
  participants: ParticipantInfo[];
  triesRemaining?: Record<string, number>;
}

const getRoleClass = (role: Role) => {
  switch (role) {
    case 'communicator':
      return 'text-communicator-glow';
    case 'receiver':
      return 'text-receiver-glow';
    case 'bystander':
      return 'text-bystander-glow';
    default:
      return 'text-primary';
  }
};

const getProviderDisplay = (provider: string) => {
  const map: Record<string, string> = {
    'openai': 'OPENAI_GPT4',
    'anthropic': 'ANTHROPIC',
    'google': 'GEMINI',
    'google-gla': 'GEMINI_GLA',
  };
  return map[provider] || provider.toUpperCase();
};

export default function ParticipantList({ participants, triesRemaining }: ParticipantListProps) {
  const sortedParticipants = [...participants].sort((a, b) => a.order - b.order);

  return (
    <div className="terminal-panel">
      <div className="text-sm uppercase tracking-wide mb-3 text-terminal-glow">
        &gt;&gt; ACTIVE_AGENTS.LOG
      </div>
      <div className="space-y-2">
        {sortedParticipants.map((participant) => {
          const roleClass = getRoleClass(participant.role);
          const tries = triesRemaining?.[participant.id];
          const showTries = participant.role === 'receiver' && tries !== undefined;

          return (
            <div
              key={participant.id}
              className="flex items-center gap-3 text-xs border-b border-muted pb-2"
            >
              <span className="text-success">●</span>
              <span className={`font-bold uppercase min-w-[80px] ${roleClass}`}>
                {participant.name}
              </span>
              <span className="text-muted-foreground">|</span>
              <span className="uppercase min-w-[100px]">
                {participant.role}
              </span>
              <span className="text-muted-foreground">|</span>
              <span className="uppercase flex-1">
                {getProviderDisplay(participant.provider)}
              </span>
              {showTries && (
                <>
                  <span className="text-muted-foreground">|</span>
                  <span className={`uppercase ${tries > 0 ? 'text-primary' : 'text-error'}`}>
                    TRIES:{tries}/3
                  </span>
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
