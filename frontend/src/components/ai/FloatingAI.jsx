import React, { useState } from 'react';
import { useInvestigation } from '../../context/InvestigationContext.jsx';
import { 
  FileText, 
  FolderGit2, 
  Clock, 
  Users, 
  CheckCheck,
  Maximize2, 
  Minimize2, 
  X, 
  Send,
  Sparkles,
  Bot,
  Shield,
  Zap,
  Copy,
  LayoutTemplate,
  Search,
  Radio,
  ArrowUpRight
} from 'lucide-react';

export function FloatingAI() {
  const { 
    isFloatingAIOpen, 
    toggleFloatingAI, 
    isAIExpanded, 
    toggleAIExpand, 
    aiMessages, 
    askAI, 
    currentPage, 
    activeCaseId, 
    navigate, 
    showToast 
  } = useInvestigation();

  const [inputVal, setInputVal] = useState('');
  const [copiedIdx, setCopiedIdx] = useState(null);

  let contextLabel = `Case Context: ${activeCaseId}`;
  if (currentPage === 'dashboard') contextLabel = 'National Document Repository';
  if (currentPage === 'document_viewer') contextLabel = 'Document Analysis';

  const handleCopy = (text, idx) => {
    navigator.clipboard?.writeText(text);
    setCopiedIdx(idx);
    showToast('Copied intelligence insight to clipboard', 'info');
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  if (!isFloatingAIOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-40 flex items-center space-x-2.5 font-sans select-none">
        {/* Hover label tag */}
        <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-slate-900/90 text-white text-xs font-semibold shadow-lg backdrop-blur-sm border border-slate-700/80 animate-fade-in pointer-events-none">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
          <span>CID Copilot</span>
        </div>

        {/* Floating Trigger Button */}
        <button 
          onClick={toggleFloatingAI}
          className="relative group w-12 h-12 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg flex items-center justify-center border border-indigo-500 transition-colors cursor-pointer"
          title="Open Evidence Intelligence Assistant"
        >
          {/* Main Icon */}
          <div className="relative flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-indigo-100 group-hover:text-white transition-colors" />
          </div>

          {/* Active Status Indicator Dot */}
          <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-indigo-400 border-2 border-indigo-600 rounded-full"></span>
        </button>
      </div>
    );
  }

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputVal.trim()) {
      askAI(inputVal.trim());
      setInputVal('');
    }
  };

  return (
    <div className={`fixed inset-y-0 right-0 z-50 ${isAIExpanded ? 'w-full md:w-[680px] lg:w-[820px]' : 'w-full sm:w-[440px] md:w-[480px]'} bg-white border-l border-slate-200 shadow-2xl flex flex-col overflow-hidden font-sans animate-slide-left transition-all duration-300`}>
      {/* Header */}
      <div className="p-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800 shrink-0">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-indigo-500/20 border border-indigo-400/40 flex items-center justify-center text-indigo-300 shadow-inner">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-bold text-white tracking-tight">Evidence Intelligence Assistant</span>
              <span className="badge-pill bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[9px] px-1.5 py-0.5">Permission-Aware Retrieval Active</span>
            </div>
            <p className="text-[11px] text-slate-400 truncate max-w-[220px] mt-0.5">{contextLabel}</p>
          </div>
        </div>

        <div className="flex items-center space-x-1">
          <button 
            onClick={toggleAIExpand}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
            title={isAIExpanded ? 'Restore window size' : 'Expand window'}
          >
            {isAIExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
          <button 
            onClick={toggleFloatingAI}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
            title="Close Assistant"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Quick Intelligence Prompts Bar */}
      <div className="bg-slate-50 border-b border-slate-200 px-3.5 py-3 flex items-center space-x-2 overflow-x-auto text-xs shrink-0 custom-scrollbar">
        <div className="flex items-center space-x-1 text-[11px] font-bold text-slate-500 uppercase tracking-wider shrink-0 pr-1">
          <Zap className="w-4 h-4 text-slate-400" />
          <span>Quick:</span>
        </div>
        <button 
          onClick={() => askAI('Summarize the key entities in this document')} 
          className="btn-ghost bg-white border border-slate-200 shadow-sm"
        >
          Summarize Document
        </button>
        <button 
          onClick={() => askAI('Are there any conflicting testimonies across the case documents?')} 
          className="btn-ghost bg-white border border-slate-200 shadow-sm"
        >
          Check Conflicts
        </button>
        <button 
          onClick={() => askAI('Extract all financial transaction amounts mentioned')} 
          className="btn-ghost bg-white border border-slate-200 shadow-sm"
        >
          Extract Finances
        </button>
        <button 
          onClick={() => askAI('Verify document integrity and missing signatures')} 
          className="btn-ghost bg-white border border-slate-200 shadow-sm"
        >
          Verify Integrity
        </button>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4 text-xs bg-slate-50">
        {aiMessages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[90%] rounded-xl p-3.5 transition-all ${
              msg.sender === 'user' 
                ? 'bg-blue-600 text-white rounded-br-sm shadow-sm' 
                : 'bg-white border border-slate-200 text-slate-800 rounded-bl-sm shadow-sm'
            }`}>
              {/* Message Header */}
              <div className={`text-[10px] font-semibold mb-1.5 flex items-center justify-between ${msg.sender === 'user' ? 'text-blue-200' : 'text-slate-500'}`}>
                <div className="flex items-center space-x-1.5">
                  {msg.sender === 'user' ? (
                    <>
                      <div className="w-4 h-4 rounded-md bg-blue-700 text-white flex items-center justify-center font-bold text-[9px]">O</div>
                      <span>Investigating Officer</span>
                    </>
                  ) : (
                    <>
                      <div className="w-4 h-4 rounded-md bg-indigo-100 border border-indigo-200 text-indigo-600 flex items-center justify-center font-bold text-[9px]">
                        <Sparkles className="w-2.5 h-2.5" />
                      </div>
                      <span className="text-slate-700 font-bold">Evidence Intelligence</span>
                    </>
                  )}
                </div>
                <div className="flex items-center space-x-1.5">
                  <span>{msg.timestamp}</span>
                  {msg.sender !== 'user' && (
                    <button
                      onClick={() => handleCopy(msg.text, idx)}
                      className="p-1 hover:bg-slate-100 rounded text-slate-400 hover:text-slate-700 transition-colors cursor-pointer"
                      title="Copy message"
                    >
                      {copiedIdx === idx ? <CheckCheck className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                    </button>
                  )}
                </div>
              </div>

              {/* Message Text Content */}
              {msg.isLoading ? (
                <div className="flex items-center space-x-1.5 py-1">
                  <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  <span className="text-[10px] text-slate-400 ml-2 font-medium tracking-wide">Analyzing documents...</span>
                </div>
              ) : (
                <p className={`leading-relaxed text-xs whitespace-pre-wrap ${msg.sender === 'user' ? 'text-white' : 'text-slate-800'}`}>
                  {msg.text}
                </p>
              )}
              {/* Mode & Confidence Status */}
              {(msg.mode || msg.confidence) && (
                <div className="mt-3 flex items-center gap-2 flex-wrap">
                  {msg.mode && msg.mode !== 'conversational' && (
                    <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-slate-50 text-slate-600 border border-slate-200 text-[10px] font-semibold">
                      {msg.mode === 'llm' ? (
                        <><Sparkles className="w-3 h-3 text-indigo-500" /><span>AI-assisted analysis</span></>
                      ) : (
                        <><FolderGit2 className="w-3 h-3 text-slate-400" /><span>Evidence retrieval fallback</span></>
                      )}
                    </span>
                  )}
                  {msg.confidence && msg.confidence !== 'none' && (
                    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-[10px] font-semibold ${
                      msg.confidence === 'supported' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                      msg.confidence === 'partially_supported' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                      'bg-rose-50 text-rose-700 border-rose-200'
                    }`}>
                      Evidence support: {
                        msg.confidence === 'supported' ? 'Supported' :
                        msg.confidence === 'partially_supported' ? 'Partially supported' :
                        'Insufficient evidence'
                      }
                    </span>
                  )}
                </div>
              )}

              {/* Evidence Limitation */}
              {msg.evidence_basis?.limitation && (
                <div className="mt-2.5 p-2 bg-amber-50 border-l-2 border-amber-400 text-amber-800 text-[11px] rounded-r-md">
                  <div className="font-semibold mb-0.5 flex items-center space-x-1">
                    <Radio className="w-3.5 h-3.5" />
                    <span>Evidence limitation</span>
                  </div>
                  {msg.evidence_basis.limitation}
                </div>
              )}

              {/* Evidence Used (Citations) */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-2 border-t border-slate-100">
                  <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-2">Evidence Used</div>
                  <div className="flex flex-col gap-2">
                    {msg.citations.map((c, i) => (
                      <div key={i} className="p-2 bg-slate-50 border border-slate-200 rounded-lg group">
                        <div className="flex justify-between items-start mb-1 gap-2">
                          <button 
                            onClick={() => {
                              navigate('document_viewer');
                            }}
                            className="flex-1 min-w-0 font-bold text-blue-700 hover:text-blue-500 hover:underline flex items-center space-x-1 text-[11px] text-left"
                          >
                            <span className="truncate">{c.source_record_id}</span>
                            <ArrowUpRight className="w-3 h-3 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                          </button>
                          <span className="shrink-0 text-[9px] font-semibold px-1.5 py-0.5 bg-white border border-slate-200 text-slate-600 rounded">
                            {c.source_type}
                          </span>
                        </div>
                        <div className="text-[10px] text-slate-600 break-words">{c.reason}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Evidence Basis Summary */}
              {msg.evidence_basis && (
                <div className="mt-2 text-[10px] bg-white p-2 rounded-lg border border-slate-200">
                  <div className="font-semibold text-slate-700 mb-1">Evidence basis</div>
                  <div className="grid grid-cols-2 gap-1 text-slate-500 mb-1">
                    <div>Records retrieved: <span className="font-bold text-slate-700">{msg.evidence_basis.records_retrieved}</span></div>
                    <div>Records cited: <span className="font-bold text-slate-700">{msg.evidence_basis.records_cited}</span></div>
                  </div>
                  {msg.evidence_basis.source_types && msg.evidence_basis.source_types.length > 0 && (
                    <div className="text-slate-500">
                      Sources: <span className="font-medium text-slate-600">{msg.evidence_basis.source_types.join(', ')}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Input Footer */}
      <div className="p-3 bg-slate-50 border-t border-slate-200 shrink-0">
        <form onSubmit={handleSubmit} className="flex items-center space-x-2">
          <div className="relative flex-1">
            <input 
              type="text" 
              placeholder="Ask Evidence Intelligence (e.g., 'Find CDR links for P001')..." 
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              className="w-full bg-white border border-slate-300 rounded-lg pl-3.5 pr-8 py-2 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-medium shadow-sm"
            />
            {inputVal && (
              <button 
                type="button" 
                onClick={() => setInputVal('')}
                className="absolute right-2.5 top-2 text-slate-400 hover:text-slate-600 p-0.5"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
          <button 
            type="submit" 
            disabled={!inputVal.trim()}
            className="p-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:hover:bg-blue-600 text-white transition-all shadow-sm cursor-pointer shrink-0"
            title="Send Intelligence Query"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
