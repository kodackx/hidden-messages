import React, { Component, ErrorInfo, ReactNode } from 'react';
import { RotateCcw } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-background scanlines crt-screen p-4">
          <div className="terminal-panel max-w-2xl w-full border-error">
            <h1 className="text-3xl font-bold uppercase mb-4 text-error terminal-flicker">
              ███ SYSTEM_ERROR ███
            </h1>
            
            <div className="mb-6 space-y-2 text-sm">
              <p className="text-muted-foreground uppercase">
                &gt;&gt; FATAL_EXCEPTION_CAUGHT
              </p>
              {this.state.error && (
                <div className="bg-secondary p-3 rounded-sm border border-error">
                  <p className="text-error font-mono text-xs break-all">
                    {this.state.error.message}
                  </p>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                &gt; The application encountered an unexpected error.
              </p>
              <p className="text-sm text-muted-foreground">
                &gt; Click below to restart the system.
              </p>
            </div>

            <button
              onClick={this.handleReset}
              className="terminal-button-danger w-full mt-6 flex items-center justify-center gap-2"
            >
              <RotateCcw size={16} />
              REBOOT_SYSTEM
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
