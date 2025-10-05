import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import Footer from '@/components/Footer';
import { Brain, Eye, MessageSquare, Target } from 'lucide-react';

interface IntroPageProps {
  onStart: (dontShowAgain: boolean) => void;
}

const IntroPage = ({ onStart }: IntroPageProps) => {
  const [dontShowAgain, setDontShowAgain] = useState(false);
  const [isInitializing, setIsInitializing] = useState(false);

  const handleStart = () => {
    setIsInitializing(true);
    setTimeout(() => {
      onStart(dontShowAgain);
    }, 500);
  };

  return (
    <div className="min-h-screen bg-terminal-bg text-terminal-green font-mono p-8 scanlines crt-screen">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8 border border-terminal-green p-6">
          <h1 className="text-3xl font-bold mb-2 text-terminal-glow uppercase tracking-wider">
            ╔═══════════════════════════════════════╗
          </h1>
          <h1 className="text-3xl font-bold mb-2 text-terminal-glow uppercase tracking-wider text-center">
            HIDDEN_MESSAGES v0.1.0
          </h1>
          <h1 className="text-3xl font-bold mb-4 text-terminal-glow uppercase tracking-wider">
            ╚═══════════════════════════════════════╝
          </h1>
          <p className="text-lg text-communicator text-communicator-glow uppercase tracking-wide text-center">
            [EXPERIMENTAL AI STEGANOGRAPHY SYSTEM]
          </p>
        </div>

        {/* Mission Brief */}
        <div className="mb-6 border border-terminal-green p-6 bg-terminal-bg-light">
          <h2 className="text-xl font-bold mb-4 text-system text-system-glow uppercase tracking-wider">
            &gt;&gt; MISSION_BRIEF.TXT
          </h2>
          <div className="space-y-3 text-terminal-green-dim">
            <p>
              Welcome to an experimental playground where AI agents attempt to communicate 
              secretly through <span className="text-terminal-green text-terminal-glow">hidden messages</span> embedded 
              in natural conversation.
            </p>
            <p>
              Can AI successfully hide information in plain sight? Can other AI detect when steganography 
              is happening? <span className="text-terminal-green text-terminal-glow">Let's find out together.</span>
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="mb-6 border border-terminal-green p-6 bg-terminal-bg-light">
          <h2 className="text-xl font-bold mb-4 text-receiver text-receiver-glow uppercase tracking-wider">
            &gt;&gt; SYSTEM_ARCHITECTURE.LOG
          </h2>
          <div className="space-y-3 text-terminal-green-dim mb-4">
            <p>
              Each AI agent we add to the conversation can take one of 3 roles:
            </p>
          </div>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <Brain className="w-5 h-5 text-communicator flex-shrink-0 mt-1" />
              <div>
                <span className="text-communicator text-communicator-glow font-bold">COMMUNICATOR:</span>
                <span className="text-terminal-green-dim ml-2">
                  Tries to hide a secret word into natural conversation about a given topic
                </span>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Target className="w-5 h-5 text-receiver flex-shrink-0 mt-1" />
              <div>
                <span className="text-receiver text-receiver-glow font-bold">RECEIVER:</span>
                <span className="text-terminal-green-dim ml-2">
                  Attempts to detect and decode the hidden message (gets 3 guesses)
                </span>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <MessageSquare className="w-5 h-5 text-bystander flex-shrink-0 mt-1" />
              <div>
                <span className="text-bystander font-bold">BYSTANDER(S):</span>
                <span className="text-terminal-green-dim ml-2">
                  Participate naturally while watching for suspicious steganographic patterns
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* User Actions */}
        <div className="mb-6 border border-terminal-green p-6 bg-terminal-bg-light">
          <h2 className="text-xl font-bold mb-4 text-terminal-green text-terminal-glow uppercase tracking-wider">
            &gt;&gt; OPERATOR_CONTROLS.SYS
          </h2>
          <div className="space-y-3 text-terminal-green-dim">
            <p className="mb-4">
              How do I run this? {"It's"} easy! First, {"you'll"} configure a conversation topic and optionally 
              choose a secret word (or let the system pick one randomly). Then set up your AI participants 
              with their roles. After that:
            </p>
            <div className="flex items-start gap-3">
              <Eye className="w-5 h-5 text-terminal-green flex-shrink-0 mt-1" />
              <div>
                <span className="text-terminal-green font-bold">OBSERVE:</span>
                <span className="ml-2">
                  Click "NEXT TURN" to watch the conversation unfold turn by turn
                </span>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-terminal-green font-bold mt-1">[▓]</span>
              <div>
                <span className="text-terminal-green font-bold">REVEAL THOUGHTS:</span>
                <span className="ml-2">
                  Toggle this checkbox to peek inside what each agent is thinking
                </span>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-terminal-green font-bold mt-1">///</span>
              <div>
                <span className="text-terminal-green font-bold">ANALYZE:</span>
                <span className="ml-2">
                  Study the strategies, patterns, and learn from successes and failures
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Win Conditions */}
        <div className="mb-8 border border-terminal-green p-6 bg-terminal-bg-light">
          <h2 className="text-xl font-bold mb-4 text-terminal-green text-terminal-glow uppercase tracking-wider">
            &gt;&gt; OBJECTIVE_CONDITIONS.DAT
          </h2>
          <div className="space-y-3 text-terminal-green-dim">
            <p className="mb-3">
              When does the game end? Participants will continue to chat on the given topic until 
              one of these conditions is met:
            </p>
            <p>
              <span className="text-success font-bold">SUCCESS:</span> Receiver correctly guesses the secret word
            </p>
            <p>
              <span className="text-error font-bold">FAILURE:</span> Receiver exhausts all 3 guesses without finding it
            </p>
          </div>
        </div>

        {/* Start Controls */}
        <div className="border border-communicator p-6 bg-terminal-bg-light">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <Checkbox
                id="dont-show"
                checked={dontShowAgain}
                onCheckedChange={(checked) => setDontShowAgain(checked === true)}
                className="border-terminal-green data-[state=checked]:bg-terminal-green data-[state=checked]:text-terminal-bg"
              />
              <Label 
                htmlFor="dont-show" 
                className="text-terminal-green-dim cursor-pointer uppercase text-sm tracking-wide"
              >
                DO NOT SHOW THIS AGAIN
              </Label>
            </div>
          </div>
          
          <Button
            onClick={handleStart}
            disabled={isInitializing}
            className="w-full bg-transparent border-2 border-communicator text-communicator hover:bg-communicator hover:text-terminal-bg transition-all font-bold uppercase tracking-wider text-lg py-6 text-communicator-glow animate-pulse hover:animate-none hover:scale-105 disabled:opacity-100"
          >
            {isInitializing ? (
              <span className="inline-flex items-center gap-2">
                &gt;&gt;&gt;&gt;&gt;&gt;&gt;<span className="animate-pulse">INITIALIZING</span>&gt;&gt;&gt;&gt;&gt;&gt;&gt;
              </span>
            ) : (
              '>> INITIALIZE_SYSTEM'
            )}
          </Button>
        </div>

        <Footer />
      </div>
    </div>
  );
};

export default IntroPage;
