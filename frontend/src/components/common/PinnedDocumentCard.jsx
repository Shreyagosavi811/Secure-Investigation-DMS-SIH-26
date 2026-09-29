import React, { useEffect, useState } from 'react';
import { useInvestigation } from '../../context/InvestigationContext';
import { FileText, X, ExternalLink, ShieldCheck, Loader2, AlertTriangle } from 'lucide-react';
import { Handle, Position } from '@xyflow/react';

export function PinnedDocumentCard({ data }) {
  const { pin, onUnpin } = data;
  const { navigate } = useInvestigation();
  const [docData, setDocData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setIsLoading(true);
    fetch(`/api/documents/${pin.documentId}`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(async (res) => {
        if (!res.ok) throw new Error("Access Denied or Not Found");
        return res.json();
      })
      .then(data => setDocData(data))
      .catch(err => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [pin.documentId]);

  const openDocument = () => {
    navigate('document_viewer', { caseId: pin.caseId });
  };

  return (
    <div className="human-card border border-slate-200 shadow-md w-72 bg-white flex flex-col overflow-hidden select-none hover:shadow-xl transition-shadow rounded-xl">
      <Handle type="target" position={Position.Top} className="w-2 h-2 bg-blue-500 border-2 border-white" />
      <Handle type="source" position={Position.Bottom} className="w-2 h-2 bg-blue-500 border-2 border-white" />

      {/* Header - now a drag handle */}
      <div className="bg-slate-50 border-b border-slate-100 px-3 py-2 flex justify-between items-center cursor-grab active:cursor-grabbing">
        <div className="flex items-center space-x-2 text-slate-500">
          <FileText className="w-3.5 h-3.5" />
          <span className="text-[10px] font-bold uppercase tracking-wider">{pin.caseId}</span>
        </div>
        <button 
          onClick={(e) => { e.stopPropagation(); onUnpin(pin.documentId); }}
          className="p-1 text-slate-400 hover:text-rose-600 hover:bg-slate-200/50 rounded transition nodrag"
          title="Remove from board"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="p-4 flex-1 flex flex-col min-h-[120px] cursor-grab active:cursor-grabbing">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center flex-1 text-slate-400">
            <Loader2 className="w-5 h-5 animate-spin mb-2" />
            <span className="text-xs">Loading secure data...</span>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center flex-1 text-rose-500 text-center">
            <AlertTriangle className="w-6 h-6 mb-2" />
            <span className="text-xs font-bold">{error}</span>
            <span className="text-[10px] mt-1 text-slate-500">Evidence unavailable</span>
          </div>
        ) : docData ? (
          <>
            <h3 className="font-bold text-slate-800 text-sm leading-tight mb-2 line-clamp-2">
              {docData.title}
            </h3>
            
            <div className="space-y-1.5 mb-4">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-500">Type:</span>
                <span className="badge-pill bg-slate-100 text-slate-700 px-1.5 py-0.5">{docData.document_type}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-500">Owner:</span>
                <span className="font-mono text-slate-700 truncate max-w-[120px]">{docData.owner}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-500">Status:</span>
                <span className="text-emerald-600 flex items-center gap-1 font-medium bg-emerald-50 px-1.5 py-0.5 rounded">
                  <ShieldCheck className="w-3 h-3" /> Secure
                </span>
              </div>
            </div>

            <div className="mt-auto pt-3 border-t border-slate-100 nodrag">
              <button 
                onClick={openDocument}
                className="w-full flex items-center justify-center gap-2 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold rounded-lg transition"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                Open Document
              </button>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}
