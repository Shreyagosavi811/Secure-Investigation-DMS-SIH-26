import React from 'react';
import { ShieldAlert, RotateCcw, Home } from 'lucide-react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-6 text-slate-100 font-sans text-xs">
          <div className="bg-slate-950 border border-slate-800 rounded-2xl max-w-xl w-full p-8 shadow-2xl space-y-6">
            <div className="flex items-center space-x-3 text-red-400">
              <div className="w-12 h-12 rounded-xl bg-red-950/60 border border-red-800 flex items-center justify-center">
                <ShieldAlert className="w-6 h-6 text-red-500" />
              </div>
              <div>
                <h2 className="text-base font-bold text-white">Application Exception Intercepted</h2>
                <p className="text-[11px] text-slate-400">OmniGuard Runtime Error Shield</p>
              </div>
            </div>

            <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl space-y-2 text-slate-300">
              <div className="text-[11px] font-bold text-red-400 uppercase">Error Details:</div>
              <div className="text-xs font-mono text-red-300 break-words whitespace-pre-wrap">
                {this.state.error?.toString()}
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <button 
                onClick={() => {
                  try {
                    localStorage.clear();
                  } catch (e) {}
                  this.handleReset();
                }}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold rounded-xl transition-all"
              >
                Reset Saved State & Reload
              </button>

              <button 
                onClick={this.handleReset}
                className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-md flex items-center space-x-2 transition-all"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Reload Application</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
