import React, { useEffect, useState } from 'react';
import { useInvestigation } from '../context/InvestigationContext';
import { Loader2, ShieldCheck, AlertTriangle, Pin, Printer } from 'lucide-react';
import { EmptyState } from '../components/common/EmptyState';
import { EvidenceChain } from '../components/common/EvidenceChain';

export function DocumentViewer() {
  const { setCurrentPage, pinDocument, isDocumentPinned, showToast } = useInvestigation();
  const caseId = localStorage.getItem('selected_case_id');
  const [caseData, setCaseData] = useState(null);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [integrityStatus, setIntegrityStatus] = useState(null);
  const [error, setError] = useState(null);
  
  const [isDocLoading, setIsDocLoading] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);

  useEffect(() => {
    if (!caseId) return;
    fetch(`/api/cases/${caseId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then(async (res) => {
        if (!res.ok) throw new Error("Access Denied");
        return res.json();
      })
      .then(data => setCaseData(data))
      .catch(err => setError(err.message));
  }, [caseId]);

  const viewDocument = (docId) => {
    setIntegrityStatus(null);
    setIsDocLoading(true);
    
    Promise.all([
      fetch(`/api/documents/${docId}`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }).then(res => res.json()),
      fetch(`/api/documents/${docId}/content`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
        .then(res => res.ok ? res.json() : { content: "Content not available" })
        .catch(() => ({ content: "Content not available" }))
    ])
    .then(([metadata, contentData]) => {
      setSelectedDoc({ ...metadata, content: contentData.content });
    })
    .catch(err => console.error(err))
    .finally(() => setIsDocLoading(false));
  };

  const verifyIntegrity = (docId) => {
    setIsVerifying(true);
    fetch(`/api/documents/${docId}/verify`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(res => res.json())
      .then(data => setIntegrityStatus(data))
      .catch(err => console.error(err))
      .finally(() => setIsVerifying(false));
  };

  const simulateTamper = (docId) => {
    if(!window.confirm("DEMO ONLY: This will physically alter the file on disk to simulate a cyber attack. The system will automatically detect the tamper. Proceed?")) return;
    fetch(`/api/documents/${docId}/tamper`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    .then(res => res.json())
    .then(() => {
      showToast('Cyber attack simulated! The file has been maliciously altered.', 'error');
      // Automatically trigger the integrity verification to alert the system immediately
      verifyIntegrity(docId);
    })
    .catch(err => console.error(err));
  };

  if (error) {
    return (
      <div className="max-w-7xl mx-auto h-[calc(100vh-8rem)] flex flex-col justify-center items-center">
        <div className="bg-rose-50 border-2 border-rose-200 rounded-xl p-12 max-w-lg w-full text-center shadow-sm">
          <AlertTriangle className="w-16 h-16 text-rose-500 mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-rose-800 tracking-tight mb-2">ACCESS DENIED</h2>
          <div className="text-sm font-mono bg-white border border-rose-100 text-rose-600 p-3 rounded mb-6 break-all shadow-inner">
            Error 403: You do not have authorization to view {caseId}.
          </div>
          <p className="text-rose-700 text-sm font-medium mb-8">
            This incident has been securely logged in the audit trail.
          </p>
          <button 
            onClick={() => setCurrentPage('dashboard')} 
            className="bg-rose-600 hover:bg-rose-700 text-white font-bold py-2.5 px-6 rounded-lg transition-colors shadow-sm"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!caseData) return (
    <div className="flex flex-col items-center justify-center h-full text-slate-500 py-20">
      <Loader2 className="w-8 h-8 animate-spin mb-4 text-slate-400" />
      <p>Loading case data...</p>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto flex flex-col md:flex-row gap-6 h-[calc(100vh-8rem)]">
      {/* Sidebar: Document List */}
      <div className="w-full md:w-1/3 human-card flex flex-col min-h-[300px] md:min-h-0">
        <div className="p-5 border-b border-slate-100 bg-slate-50/50 rounded-t-xl">
          <button onClick={() => setCurrentPage('dashboard')} className="text-sm font-medium text-blue-600 mb-3 hover:text-blue-800 transition">← Back to Cases</button>
          <h2 className="text-xl font-bold text-slate-800 leading-tight">{caseData.title}</h2>
          <p className="text-xs font-mono text-slate-500 mt-1">{caseData.case_id}</p>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar">
          {(!caseData.documents || caseData.documents.length === 0) ? (
            <div className="mt-8">
              <EmptyState 
                type="documents" 
                title="No Documents" 
                message="This case contains no documents." 
              />
            </div>
          ) : (
            caseData.documents.map(doc => (
              <div 
                key={doc.document_id}
                onClick={() => viewDocument(doc.document_id)}
                className={`p-4 rounded-xl cursor-pointer transition-all border ${selectedDoc?.document_id === doc.document_id ? 'bg-indigo-50/80 border-indigo-200 shadow-sm' : 'hover:bg-slate-50 border-transparent hover:border-slate-200'}`}
              >
                <h3 className="text-sm font-bold text-slate-800">{doc.title}</h3>
                <div className="flex justify-between items-center mt-3">
                  <span className="badge-pill bg-slate-100 text-slate-600 px-2 py-0.5">{doc.type}</span>
                  <span className="text-xs font-mono text-slate-400">{doc.document_id}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main: Document Details */}
      <div className="flex-1 human-card p-6 md:p-8 overflow-y-auto custom-scrollbar relative min-h-[500px] md:min-h-0">
        {isDocLoading ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-400">
            <Loader2 className="w-8 h-8 animate-spin mb-4 text-slate-300" />
            <p>Loading document details...</p>
          </div>
        ) : selectedDoc ? (
          <div>
            <div className="flex justify-between items-start mb-8">
              <div>
                <h2 className="text-3xl font-bold text-slate-800 tracking-tight">{selectedDoc.title}</h2>
                <div className="flex gap-3 mt-4">
                  <span className="badge-pill bg-slate-100 text-slate-700">{selectedDoc.document_type}</span>
                  <span className="badge-pill badge-light-rose">{selectedDoc.classification}</span>
                  <span className="badge-pill badge-light-blue">Owner: {selectedDoc.owner}</span>
                </div>
              </div>
              <div className="flex gap-2">
                <button 
                  onClick={() => window.print()}
                  className="btn-secondary text-slate-700 border-slate-300 shadow-sm flex items-center gap-2 hover:bg-slate-50"
                >
                  <Printer className="w-4 h-4" /> Export PDF
                </button>
                <button 
                  onClick={() => {
                    pinDocument(selectedDoc, caseData.case_id);
                    showToast('Evidence pinned to board', 'success');
                  }}
                  disabled={isDocumentPinned(selectedDoc.document_id)}
                  className={`btn-primary ${isDocumentPinned(selectedDoc.document_id) ? 'opacity-50 cursor-not-allowed' : 'bg-slate-800 hover:bg-slate-900 text-white border-transparent'}`}
                >
                  <Pin className="w-4 h-4" /> {isDocumentPinned(selectedDoc.document_id) ? 'Pinned to Board' : 'Pin Evidence'}
                </button>
                <button 
                  onClick={() => simulateTamper(selectedDoc.document_id)}
                  className="btn-primary bg-rose-600 hover:bg-rose-700 text-white border-transparent shadow-sm flex items-center gap-2"
                >
                  <AlertTriangle className="w-4 h-4" /> Simulate Attack
                </button>
                <button 
                  onClick={() => verifyIntegrity(selectedDoc.document_id)}
                  disabled={isVerifying}
                  className="btn-primary flex items-center gap-2"
                >
                  {isVerifying ? (
                    <><Loader2 className="w-4 h-4 animate-spin" /> Verifying...</>
                  ) : (
                    <><ShieldCheck className="w-4 h-4" /> Verify Integrity</>
                  )}
                </button>
              </div>
            </div>

            {integrityStatus && integrityStatus.status === 'TAMPER_DETECTED' && (
              <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-rose-900/90 backdrop-blur-md animate-in fade-in duration-200">
                <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full overflow-hidden border-4 border-rose-500 animate-in zoom-in-95 duration-300">
                  <div className="bg-rose-600 p-6 flex flex-col items-center justify-center text-white">
                    <AlertTriangle className="w-16 h-16 mb-4 animate-pulse" />
                    <h2 className="text-3xl font-black tracking-wider">TAMPER DETECTED</h2>
                    <p className="text-rose-100 mt-2 font-medium">Critical Security Breach - Cryptographic Signature Mismatch</p>
                  </div>
                  
                  <div className="p-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 text-sm font-sans">
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                        <span className="font-bold uppercase tracking-wider text-xs text-slate-500 block mb-1">Document:</span>
                        <span className="font-semibold text-slate-800 text-lg">{selectedDoc.title}</span>
                      </div>
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                        <span className="font-bold uppercase tracking-wider text-xs text-slate-500 block mb-1">Case ID:</span>
                        <span className="font-semibold text-slate-800">{caseData.case_id}</span>
                      </div>
                    </div>

                    <div className="space-y-4 font-mono text-sm break-all">
                      <div className="p-4 bg-emerald-50 text-emerald-900 rounded-lg border border-emerald-200">
                        <span className="font-bold font-sans uppercase text-xs block mb-1 text-emerald-700">Expected Valid Hash:</span>
                        {integrityStatus.expected_hash}
                      </div>
                      <div className="p-4 bg-rose-50 text-rose-900 rounded-lg border border-rose-200 shadow-inner">
                        <span className="font-bold font-sans uppercase text-xs block mb-1 text-rose-700">Actual Compromised Hash:</span>
                        {integrityStatus.actual_hash}
                      </div>
                    </div>

                    <div className="mt-8 flex justify-end gap-3">
                      <button 
                        onClick={() => setIntegrityStatus(null)}
                        className="px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition-colors"
                      >
                        Acknowledge & Close
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {integrityStatus && integrityStatus.status === 'INTEGRITY_VERIFIED' && (
              <div className="p-6 mb-8 rounded-xl border-2 bg-emerald-50 border-emerald-400 text-emerald-900 shadow-sm">
                <h3 className="font-black flex items-center gap-3 text-xl mb-5 text-emerald-700">
                  <ShieldCheck className="w-6 h-6"/> INTEGRITY VERIFIED ✓
                </h3>
                <div className="font-mono text-sm break-all opacity-80">
                  Hash: {integrityStatus.actual_hash}
                </div>
              </div>
            )}

            {/* Document Content Display */}
            <div className="mb-8 p-6 bg-white border border-slate-200 rounded-xl shadow-sm overflow-x-auto">
              <h3 className="text-lg font-bold text-slate-800 mb-4 border-b border-slate-100 pb-2">Document Content</h3>
              <div className="prose prose-slate max-w-none text-slate-700 whitespace-pre-wrap break-words font-serif leading-relaxed">
                {selectedDoc.content ? selectedDoc.content : <span className="text-slate-400 italic">No content available for this document.</span>}
              </div>
            </div>

            <EvidenceChain 
              selectedDoc={selectedDoc} 
              caseId={caseData.case_id} 
              integrityStatus={integrityStatus} 
            />
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center">
            <EmptyState 
              type="documents" 
              title="No Document Selected" 
              message="Select a document from the case file list to view its contents, metadata, and version history." 
            />
          </div>
        )}
      </div>
    </div>
  );
}
