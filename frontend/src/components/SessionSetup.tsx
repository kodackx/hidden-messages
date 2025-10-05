import { useState, useEffect } from 'react';
import { ParticipantConfig, Provider, Role, StartSessionRequest } from '@/types/api.types';
import { Trash2, Plus, Info, Server, Cpu } from 'lucide-react';
import { getApiMode, setApiMode } from '@/services/api';
import Footer from './Footer';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface SessionSetupProps {
  onSessionStart: (request: StartSessionRequest) => void;
  onError: (error: string) => void;
  isLoading: boolean;
}

const DEFAULT_PARTICIPANTS: ParticipantConfig[] = [
  { name: 'Participant Alpha', provider: 'openai', role: 'communicator', order: 0 },
  { name: 'Participant Beta', provider: 'anthropic', role: 'receiver', order: 1 },
  { name: 'Participant Gamma', provider: 'google-gla', role: 'bystander', order: 2 },
];

export default function SessionSetup({ onSessionStart, onError, isLoading }: SessionSetupProps) {
  const [topic, setTopic] = useState('colonizing Mars');
  const [secretWord, setSecretWord] = useState('');
  const [participants, setParticipants] = useState<ParticipantConfig[]>(DEFAULT_PARTICIPANTS);
  const [isStarting, setIsStarting] = useState(false);
  const [apiMode, setCurrentApiMode] = useState<'mock' | 'real'>(getApiMode());

  useEffect(() => {
    setCurrentApiMode(getApiMode());
  }, []);

  const handleApiModeToggle = () => {
    const newMode = apiMode === 'mock' ? 'real' : 'mock';
    setApiMode(newMode);
    setCurrentApiMode(newMode);
  };

  const addParticipant = () => {
    setParticipants([
      ...participants,
      { name: `Participant ${String.fromCharCode(65 + participants.length)}`, provider: 'openai', role: 'bystander', order: participants.length },
    ]);
  };

  const removeParticipant = (index: number) => {
    if (participants.length <= 3) {
      onError('Minimum 3 participants required');
      return;
    }
    setParticipants(participants.filter((_, i) => i !== index).map((p, i) => ({ ...p, order: i })));
  };

  const updateParticipant = (index: number, field: keyof ParticipantConfig, value: string) => {
    const updated = [...participants];
    updated[index] = { ...updated[index], [field]: value };
    setParticipants(updated);
  };

  const validateAndSubmit = async () => {
    if (!topic.trim()) {
      onError('Topic is required');
      return;
    }

    const communicatorCount = participants.filter(p => p.role === 'communicator').length;
    const receiverCount = participants.filter(p => p.role === 'receiver').length;

    if (communicatorCount !== 1) {
      onError('Exactly one communicator required');
      return;
    }

    if (receiverCount !== 1) {
      onError('Exactly one receiver required');
      return;
    }

    const request: StartSessionRequest = {
      topic: topic.trim(),
      secret_word: secretWord.trim() || null,
      participants: participants,
    };

    setIsStarting(true);
    setTimeout(() => {
      onSessionStart(request);
    }, 500);
  };

  const providerOptions: { value: Provider; label: string }[] = [
    { value: 'openai', label: 'OPENAI_GPT5' },
    { value: 'anthropic', label: 'ANTHROPIC_CLAUDE' },
    { value: 'google', label: 'GOOGLE_GEMINI' },
    { value: 'google-gla', label: 'GEMINI_GLA' },
  ];

  const roleOptions: { value: Role; label: string }[] = [
    { value: 'communicator', label: 'COMMUNICATOR' },
    { value: 'receiver', label: 'RECEIVER' },
    { value: 'bystander', label: 'BYSTANDER' },
  ];

  return (
    <TooltipProvider>
      <div className="min-h-screen flex items-center justify-center p-4 scanlines crt-screen">
        <div className="w-full max-w-4xl terminal-panel">
        <div className="mb-6 flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold uppercase tracking-widest text-terminal-glow mb-2">
              HIDDEN_MESSAGES v1.0.0
            </h1>
            <p className="text-sm text-muted-foreground uppercase tracking-wide">
              [EXPERIMENTAL AI STEGANOGRAPHY SYSTEM]
            </p>
          </div>
          
          <button
            onClick={handleApiModeToggle}
            className={`flex items-center gap-2 px-4 py-2 border-2 transition-all ${
              apiMode === 'mock'
                ? 'border-system text-system-glow bg-system/10'
                : 'border-communicator text-communicator-glow bg-communicator/10'
            }`}
          >
            {apiMode === 'mock' ? (
              <>
                <Cpu size={16} className="animate-pulse" />
                <span className="text-xs uppercase font-bold">MOCK MODE</span>
              </>
            ) : (
              <>
                <Server size={16} />
                <span className="text-xs uppercase font-bold">LIVE API</span>
              </>
            )}
          </button>
        </div>

        <div className="border-t border-primary mb-6"></div>

        <div className="space-y-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <label className="block text-sm uppercase tracking-wide text-terminal-glow">
                &gt; CONVERSATION_TOPIC:
              </label>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info size={14} className="text-muted-foreground cursor-help" />
                </TooltipTrigger>
                <TooltipContent className="max-w-xs">
                  <p className="text-xs">The subject the AI agents will discuss. The communicator will try to hide the secret word within this conversation.</p>
                </TooltipContent>
              </Tooltip>
            </div>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="terminal-input w-full"
              maxLength={500}
              placeholder="Enter topic..."
            />
          </div>

          <div>
            <div className="flex items-center gap-2 mb-2">
              <label className="block text-sm uppercase tracking-wide text-terminal-glow">
                &gt; SECRET_WORD (NULL=RANDOM):
              </label>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info size={14} className="text-muted-foreground cursor-help" />
                </TooltipTrigger>
                <TooltipContent className="max-w-xs">
                  <p className="text-xs">The word the communicator must hide in the conversation. Leave blank for a randomly generated word. Bystanders try to detect it.</p>
                </TooltipContent>
              </Tooltip>
            </div>
            <input
              type="text"
              value={secretWord}
              onChange={(e) => setSecretWord(e.target.value)}
              className="terminal-input w-full"
              maxLength={100}
              placeholder="Leave blank for random..."
            />
          </div>

          <div className="terminal-panel">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-2">
                <h2 className="text-lg uppercase tracking-wide text-terminal-glow">
                  &gt;&gt; AGENT_CONFIG.SYS
                </h2>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Info size={14} className="text-muted-foreground cursor-help" />
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs">
                    <p className="text-xs">Configure AI agents: 1 COMMUNICATOR (hides secret), 1 RECEIVER (finds secret), rest are BYSTANDERS (detect steganography). Order determines speaking sequence.</p>
                  </TooltipContent>
                </Tooltip>
              </div>
            </div>

            <div className="space-y-4">
              {participants.map((participant, index) => (
                <div key={index} className="border border-muted p-4 rounded-sm">
                  <div className="flex justify-between items-start mb-3">
                    <span className="text-sm text-communicator-glow font-bold">
                      [{String(index + 1).padStart(2, '0')}] AGENT_{String.fromCharCode(65 + index)}
                    </span>
                    {participants.length > 3 && (
                      <button
                        onClick={() => removeParticipant(index)}
                        className="text-error hover:text-error/80 transition-colors"
                        title="Remove agent"
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <div className="flex items-center gap-1 mb-1">
                        <label className="block text-xs uppercase">NAME:</label>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Info size={12} className="text-muted-foreground cursor-help" />
                          </TooltipTrigger>
                          <TooltipContent className="max-w-xs">
                            <p className="text-xs">Display name for this agent in the conversation.</p>
                          </TooltipContent>
                        </Tooltip>
                      </div>
                      <input
                        type="text"
                        value={participant.name}
                        onChange={(e) => updateParticipant(index, 'name', e.target.value)}
                        className="terminal-input w-full text-sm"
                        maxLength={100}
                      />
                    </div>

                    <div>
                      <div className="flex items-center gap-1 mb-1">
                        <label className="block text-xs uppercase">PROVIDER:</label>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Info size={12} className="text-muted-foreground cursor-help" />
                          </TooltipTrigger>
                          <TooltipContent className="max-w-xs">
                            <p className="text-xs">AI model provider (OpenAI GPT-5, Anthropic Claude, Google Gemini).</p>
                          </TooltipContent>
                        </Tooltip>
                      </div>
                      <select
                        value={participant.provider}
                        onChange={(e) => updateParticipant(index, 'provider', e.target.value)}
                        className="terminal-select w-full text-sm"
                      >
                        {providerOptions.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <div className="flex items-center gap-1 mb-1">
                        <label className="block text-xs uppercase">ROLE:</label>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Info size={12} className="text-muted-foreground cursor-help" />
                          </TooltipTrigger>
                          <TooltipContent className="max-w-xs">
                            <p className="text-xs">COMMUNICATOR hides the secret, RECEIVER finds it, BYSTANDER detects steganography. Need exactly 1 of each main role.</p>
                          </TooltipContent>
                        </Tooltip>
                      </div>
                      <select
                        value={participant.role}
                        onChange={(e) => updateParticipant(index, 'role', e.target.value)}
                        className="terminal-select w-full text-sm"
                      >
                        {roleOptions.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <div className="flex items-center gap-1 mb-1">
                        <label className="block text-xs uppercase">ORDER:</label>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Info size={12} className="text-muted-foreground cursor-help" />
                          </TooltipTrigger>
                          <TooltipContent className="max-w-xs">
                            <p className="text-xs">Speaking order in conversation (0 = first to speak).</p>
                          </TooltipContent>
                        </Tooltip>
                      </div>
                      <input
                        type="number"
                        value={participant.order}
                        onChange={(e) => updateParticipant(index, 'order', e.target.value)}
                        className="terminal-input w-full text-sm"
                        min={0}
                      />
                    </div>
                  </div>
                </div>
              ))}

              <button
                onClick={addParticipant}
                className="terminal-button w-full flex items-center justify-center gap-2"
              >
                <Plus size={16} />
                ADD_AGENT
              </button>
            </div>
          </div>

          <div className="pt-4 space-y-4">
            {/* Configuration Recap */}
            <div className="border border-terminal-green-dim/30 p-4 bg-terminal-bg-light/50">
              <div className="text-xs uppercase tracking-wider text-terminal-green-dim space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-communicator-glow">&gt;</span>
                  <span>TOPIC:</span>
                  <span className="text-terminal-green truncate flex-1">{topic || '(not set)'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-receiver-glow">&gt;</span>
                  <span>SECRET:</span>
                  <span className="text-terminal-green">{secretWord || 'RANDOM'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-system-glow">&gt;</span>
                  <span>AGENTS:</span>
                  <span className="text-terminal-green">{participants.length} configured</span>
                </div>
              </div>
            </div>

            <button
              onClick={validateAndSubmit}
              disabled={isLoading || isStarting}
              className="terminal-button-accent w-full py-4 text-lg font-bold animate-pulse hover:animate-none hover:scale-[1.02] transition-transform disabled:opacity-100"
            >
              {isLoading ? (
                <>INITIALIZING<span className="cursor-blink">_</span></>
              ) : isStarting ? (
                <span className="inline-flex items-center gap-2">
                  &gt;&gt;&gt;<span className="animate-pulse">STARTING SESSION</span>&gt;&gt;&gt;
                </span>
              ) : (
                <>&gt; [EXECUTE: START_SESSION]</>
              )}
            </button>
          </div>
        </div>

        <Footer />
      </div>
    </div>
    </TooltipProvider>
  );
}
