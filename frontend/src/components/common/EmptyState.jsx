import React from 'react';
import { FileText, FolderGit2, SearchX, ShieldAlert, AlertCircle } from 'lucide-react';

export function EmptyState({ type, title, message, actionButton }) {
  const getIcon = () => {
    switch(type) {
      case 'cases': return <FolderGit2 className="w-12 h-12 text-slate-300" />;
      case 'documents': return <FileText className="w-12 h-12 text-slate-300" />;
      case 'search': return <SearchX className="w-12 h-12 text-slate-300" />;
      case 'unauthorized': return <ShieldAlert className="w-12 h-12 text-rose-300" />;
      case 'error': return <AlertCircle className="w-12 h-12 text-amber-300" />;
      default: return <FileText className="w-12 h-12 text-slate-300" />;
    }
  };

  const isErrorOrUnauthorized = type === 'unauthorized' || type === 'error';

  return (
    <div className={`w-full py-16 px-6 flex flex-col items-center justify-center text-center rounded-2xl ${isErrorOrUnauthorized ? 'bg-rose-50/50 border border-rose-100' : 'bg-slate-50/50 border border-slate-100 border-dashed'}`}>
      <div className={`w-24 h-24 rounded-full flex items-center justify-center mb-5 shadow-sm ${isErrorOrUnauthorized ? 'bg-white' : 'bg-white'}`}>
        {getIcon()}
      </div>
      <h3 className={`text-xl font-bold mb-2 tracking-tight ${isErrorOrUnauthorized ? 'text-rose-900' : 'text-slate-800'}`}>
        {title}
      </h3>
      <p className={`text-sm max-w-sm mx-auto ${isErrorOrUnauthorized ? 'text-rose-700/80 font-medium' : 'text-slate-500 font-medium'}`}>
        {message}
      </p>
      {actionButton && (
        <div className="mt-8">
          {actionButton}
        </div>
      )}
    </div>
  );
}
