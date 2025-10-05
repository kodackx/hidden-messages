import { MessageResponse, Role } from '@/types/api.types';

interface MessageCardProps {
  message: MessageResponse;
  showThoughts: boolean;
  turnNumber: number;
}

const getRoleColor = (role?: Role) => {
  switch (role) {
    case 'communicator':
      return 'bg-communicator';
    case 'receiver':
      return 'bg-receiver';
    case 'bystander':
      return 'bg-bystander';
    default:
      return 'bg-primary';
  }
};

const getRoleTextClass = (role?: Role) => {
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

export default function MessageCard({ message, showThoughts, turnNumber }: MessageCardProps) {
  const roleColor = getRoleColor(message.participant_role);
  const roleTextClass = getRoleTextClass(message.participant_role);
  const displayName = message.participant_name || message.participant_id.slice(0, 8);

  return (
    <div className="border border-muted p-4 rounded-sm mb-3 bg-card/50">
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${roleColor}`} />
          <span className={`font-bold uppercase text-sm ${roleTextClass}`}>
            {displayName}
          </span>
        </div>
        <span className="text-xs text-muted-foreground">
          TURN_{String(turnNumber).padStart(3, '0')}
        </span>
      </div>

      <div className="mb-3">
        <p className="text-sm leading-relaxed whitespace-pre-wrap">
          {message.comms}
        </p>
      </div>

      {showThoughts && message.internal_thoughts && (
        <div className="border-l-2 border-system pl-3 py-2 bg-secondary/30 rounded-sm">
          <div className="text-xs text-system-glow uppercase mb-1 font-bold">
            &lt;INTERNAL_THOUGHTS&gt;
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed whitespace-pre-wrap">
            {message.internal_thoughts}
          </p>
          <div className="text-xs text-system-glow uppercase mt-1 font-bold">
            &lt;/INTERNAL_THOUGHTS&gt;
          </div>
        </div>
      )}
    </div>
  );
}
