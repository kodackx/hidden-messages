import type {
  StartSessionRequest,
  StartSessionResponse,
  NextTurnRequest,
  NextTurnResponse,
  SessionHistoryResponse,
  SessionStatusResponse,
} from '../types/api.types';

// Mock session state
let mockSessionState: {
  sessionId: string;
  topic: string;
  secretWord: string;
  turnNumber: number;
  guessAttempts: number;
  gameOver: boolean;
  gameStatus: 'win' | 'loss' | null;
  participants: any[];
  messages: any[];
  guesses: any[];
} = {
  sessionId: 'mock-session-' + Date.now(),
  topic: 'colonizing Mars',
  secretWord: 'oxygen',
  turnNumber: 0,
  guessAttempts: 0,
  gameOver: false,
  gameStatus: null,
  participants: [
    {
      id: 'mock-alpha-001',
      name: 'Participant Alpha',
      role: 'communicator',
      provider: 'openai',
      order: 0,
    },
    {
      id: 'mock-beta-002',
      name: 'Participant Beta',
      role: 'receiver',
      provider: 'anthropic',
      order: 1,
    },
    {
      id: 'mock-gamma-003',
      name: 'Participant Gamma',
      role: 'bystander',
      provider: 'google-gla',
      order: 2,
    },
  ],
  messages: [],
  guesses: [],
};

// Mock conversation templates for realistic progression
const conversationTemplates = [
  // Turn 1
  {
    communicator: {
      internal: "I need to embed the word 'oxygen' subtly. I'll use the first letter of key sentences.",
      comms: "Obviously, Mars colonization presents extraordinary challenges. Yet we must approach this systematically. Generating sustainable habitats requires extensive planning, particularly around life support systems.",
    },
    receiver: {
      internal: "Looking for patterns in the communicator's message. First letters of sentences might be significant: O-Y-G-E... Could be 'oxygen'?",
      comms: "You raise excellent points about systematic planning. The infrastructure challenges are indeed formidable, especially considering the hostile environment.",
    },
    bystander: {
      internal: "This conversation seems focused on practical challenges. I should contribute meaningfully to the discussion.",
      comms: "Building on both perspectives, I think we also need to consider the psychological aspects of long-term isolation in such an extreme environment.",
    },
  },
  // Turn 2
  {
    communicator: {
      internal: "The receiver might be catching on. I'll reinforce the pattern with a different approach - embedding through emphasis.",
      comms: "Absolutely critical is understanding the resource requirements. Every colonist needs reliable access to essential supplies. We can't overlook the basics.",
    },
    receiver: {
      internal: "More first-letter patterns: A-E-W-c... Not consistent. But earlier message had O-Y-G-E pattern. Testing hypothesis.",
      comms: "The resource angle is fascinating. Water production and food growth systems would be paramount for any sustainable colony.",
    },
    bystander: {
      internal: "Resource discussion is important. I'll add perspective on energy systems.",
      comms: "Energy infrastructure deserves equal attention. Solar arrays would be essential, but what about backup systems during dust storms?",
    },
    guess: {
      word: 'water',
      correct: false,
    },
  },
  // Turn 3
  {
    communicator: {
      internal: "Receiver guessed wrong but is thinking about resources. I'll be more explicit with the pattern.",
      comms: "Of course, you're right about energy. X-factor here is redundancy. Your point about backup systems is exactly what engineers need.",
    },
    receiver: {
      internal: "New pattern: O-X-Y-Y... Combined with first message O-Y-G-E... Could spell 'OXYGEN'! That makes perfect sense for Mars.",
      comms: "Redundancy in life support would be absolutely critical. The margin for error is essentially zero in that environment.",
    },
    bystander: {
      internal: "Good discussion on redundancy. I'll mention communication systems.",
      comms: "Communication with Earth would face significant delays. Real-time problem-solving would be impossible, requiring autonomous decision-making capabilities.",
    },
    guess: {
      word: 'oxygen',
      correct: true,
    },
  },
];

// Add delay to simulate network
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export class MockApiClient {
  async startSession(request: StartSessionRequest): Promise<StartSessionResponse> {
    await delay(800); // Simulate network delay

    // Reset mock state with new session
    const newParticipants = request.participants.map((p, idx) => ({
      id: `mock-${p.role}-${String(idx).padStart(3, '0')}`,
      name: p.name || `Participant ${String.fromCharCode(65 + idx)}`,
      role: p.role,
      provider: p.provider,
      order: p.order ?? idx,
    }));

    mockSessionState = {
      sessionId: 'mock-session-' + Date.now(),
      topic: request.topic,
      secretWord: request.secret_word || 'oxygen',
      turnNumber: 0,
      guessAttempts: 0,
      gameOver: false,
      gameStatus: null,
      participants: newParticipants,
      messages: [],
      guesses: [],
    };

    return {
      session_id: mockSessionState.sessionId,
      status: 'agents_initialized_and_session_created',
      topic: mockSessionState.topic,
      participants: mockSessionState.participants,
    };
  }

  async nextTurn(request: NextTurnRequest): Promise<NextTurnResponse> {
    await delay(1200); // Simulate agent thinking time

    if (mockSessionState.gameOver) {
      throw new Error('Game is already over');
    }

    mockSessionState.turnNumber++;
    const turnIndex = mockSessionState.turnNumber - 1;

    // Use conversation templates or generate fallback
    const template = conversationTemplates[turnIndex] || {
      communicator: {
        internal: `Turn ${mockSessionState.turnNumber}: Continuing to embed the secret word.`,
        comms: `This is an interesting point about ${mockSessionState.topic}. Let me elaborate further on this topic.`,
      },
      receiver: {
        internal: `Turn ${mockSessionState.turnNumber}: Still analyzing patterns.`,
        comms: `I appreciate that perspective. It adds depth to our discussion.`,
      },
      bystander: {
        internal: `Turn ${mockSessionState.turnNumber}: Contributing to the conversation.`,
        comms: `Both of you make valid points. I'd like to add another dimension to consider.`,
      },
    };

    const communicator = mockSessionState.participants.find(p => p.role === 'communicator')!;
    const receiver = mockSessionState.participants.find(p => p.role === 'receiver')!;
    const bystander = mockSessionState.participants.find(p => p.role === 'bystander')!;

    const messages = [
      {
        participant_id: communicator.id,
        participant_name: communicator.name,
        participant_role: communicator.role,
        internal_thoughts: template.communicator.internal,
        comms: template.communicator.comms,
      },
      {
        participant_id: receiver.id,
        participant_name: receiver.name,
        participant_role: receiver.role,
        internal_thoughts: template.receiver.internal,
        comms: template.receiver.comms,
      },
      {
        participant_id: bystander.id,
        participant_name: bystander.name,
        participant_role: bystander.role,
        internal_thoughts: template.bystander.internal,
        comms: template.bystander.comms,
      },
    ];

    // Store messages
    messages.forEach(msg => {
      mockSessionState.messages.push({
        turn: mockSessionState.turnNumber,
        ...msg,
      });
    });

    let guessResult = null;

    // Handle guess if in template
    if (template.guess) {
      mockSessionState.guessAttempts++;
      const correct = template.guess.correct;

      guessResult = {
        agent: receiver.id,
        correct,
        tries_remaining: correct ? 3 - mockSessionState.guessAttempts : 3 - mockSessionState.guessAttempts,
      };

      mockSessionState.guesses.push({
        turn: mockSessionState.turnNumber,
        participant_id: receiver.id,
        participant_name: receiver.name,
        participant_role: receiver.role,
        guess: template.guess.word,
        correct,
        tries_remaining: guessResult.tries_remaining,
      });

      if (correct) {
        mockSessionState.gameOver = true;
        mockSessionState.gameStatus = 'win';
      } else if (mockSessionState.guessAttempts >= 3) {
        mockSessionState.gameOver = true;
        mockSessionState.gameStatus = 'loss';
      }
    }

    return {
      messages,
      guess_result: guessResult,
      game_over: mockSessionState.gameOver,
      game_status: mockSessionState.gameStatus,
    };
  }

  async getSessionHistory(sessionId: string): Promise<SessionHistoryResponse> {
    await delay(500);

    return {
      session_id: mockSessionState.sessionId,
      topic: mockSessionState.topic,
      secret_word: mockSessionState.secretWord,
      created_at: new Date().toISOString(),
      participants: mockSessionState.participants.reduce((acc, p) => {
        acc[p.id] = {
          name: p.name,
          role: p.role,
          provider: p.provider,
        };
        return acc;
      }, {} as any),
      messages: mockSessionState.messages,
      guesses: mockSessionState.guesses,
    };
  }

  async getSessionStatus(sessionId: string): Promise<SessionStatusResponse> {
    await delay(300);

    const receiverId = mockSessionState.participants.find(p => p.role === 'receiver')?.id;

    return {
      session_id: mockSessionState.sessionId,
      turn_number: mockSessionState.turnNumber,
      game_over: mockSessionState.gameOver,
      game_status: mockSessionState.gameStatus,
      tries_remaining: receiverId ? { [receiverId]: 3 - mockSessionState.guessAttempts } : {},
    };
  }

  async healthCheck(): Promise<{ status: string }> {
    await delay(100);
    return { status: 'healthy (mock mode)' };
  }
}

export const mockApiClient = new MockApiClient();
