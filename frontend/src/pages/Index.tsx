import { useState, useEffect } from 'react';
import { ParticipantInfo, StartSessionRequest } from '@/types/api.types';
import IntroPage from '@/components/IntroPage';
import SessionSetup from '@/components/SessionSetup';
import ConversationView from '@/components/ConversationView';
import HistoryModal from '@/components/HistoryModal';
import { toast } from 'sonner';

type AppState = 'intro' | 'setup' | 'conversation';

const INTRO_DISMISSED_KEY = 'hiddenMessages_introDismissed';

const Index = () => {
  const [appState, setAppState] = useState<AppState>('intro');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [topic, setTopic] = useState<string>('');
  const [participants, setParticipants] = useState<ParticipantInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  // Check if intro should be shown on mount
  useEffect(() => {
    const introDismissed = localStorage.getItem(INTRO_DISMISSED_KEY);
    if (introDismissed === 'true') {
      setAppState('setup');
    }
  }, []);

  const handleIntroComplete = (dontShowAgain: boolean) => {
    if (dontShowAgain) {
      localStorage.setItem(INTRO_DISMISSED_KEY, 'true');
    }
    setAppState('setup');
  };

  const handleSessionStart = async (request: StartSessionRequest) => {
    setIsLoading(true);
    try {
      const { apiClient } = await import('@/services/api');
      const response = await apiClient.startSession(request);
      
      setSessionId(response.session_id);
      setTopic(response.topic);
      setParticipants(response.participants);
      setAppState('conversation');
      setIsLoading(false);
      
      toast.success('Session initialized successfully', {
        description: `Session ID: ${response.session_id.slice(0, 8)}...`,
      });
    } catch (err) {
      handleError(err instanceof Error ? err.message : 'Failed to start session');
    }
  };

  const handleResumeSession = async (sessionIdToResume: string) => {
    setIsLoading(true);
    try {
      const { apiClient } = await import('@/services/api');
      const statusResponse = await apiClient.getSessionStatus(sessionIdToResume);
      
      setSessionId(statusResponse.session_id);
      setTopic(statusResponse.topic);
      setParticipants(statusResponse.participants);
      setAppState('conversation');
      setIsLoading(false);
      
      toast.success('Session resumed', {
        description: `ID: ${statusResponse.session_id.slice(0, 8)}...`,
      });
    } catch (err) {
      handleError(err instanceof Error ? err.message : 'Failed to resume session');
    }
  };

  const handleError = (error: string) => {
    setIsLoading(false);
    toast.error('Error', { description: error });
  };

  const handleNewSession = () => {
    if (confirm('Are you sure you want to start a new session? Current progress will be lost.')) {
      setAppState('setup');
      setSessionId(null);
      setTopic('');
      setParticipants([]);
      setShowHistory(false);
    }
  };

  const handleGoHome = () => {
    setAppState('setup');
    setSessionId(null);
    setTopic('');
    setParticipants([]);
    setShowHistory(false);
    setIsLoading(false);
  };

  const handleViewHistory = () => {
    if (sessionId) {
      setShowHistory(true);
    }
  };

  return (
    <>
      {appState === 'intro' ? (
        <IntroPage onStart={handleIntroComplete} />
      ) : appState === 'setup' ? (
        <SessionSetup
          onSessionStart={handleSessionStart}
          onResumeSession={handleResumeSession}
          onError={handleError}
          isLoading={isLoading}
        />
      ) : sessionId ? (
        <ConversationView
          sessionId={sessionId}
          topic={topic}
          participants={participants}
          onNewSession={handleNewSession}
          onViewHistory={handleViewHistory}
          onGoHome={handleGoHome}
        />
      ) : null}

      {showHistory && sessionId && (
        <HistoryModal
          sessionId={sessionId}
          onClose={() => setShowHistory(false)}
        />
      )}
    </>
  );
};

export default Index;
