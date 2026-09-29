import React, { useEffect, useState } from 'react';
import { 
  History, 
  ShieldCheck, 
  AlertTriangle, 
  Eye, 
  FilePlus, 
  Lock,
  Activity,
  FileText
} from 'lucide-react';

export function EvidenceChain({ selectedDoc, caseId, integrityStatus }) {
  const [auditEvents, setAuditEvents] = useState([]);
  const [auditRestricted, setAuditRestricted] = useState(false);
  const [isLoadingAudit, setIsLoadingAudit] = useState(false);

  useEffect(() => {
    if (!caseId || !selectedDoc) return;
    
    setIsLoadingAudit(true);
    setAuditRestricted(false);

    fetch(`/api/audit/?case_id=${caseId}&limit=200`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(async (res) => {
        if (res.status === 403) {
          setAuditRestricted(true);
          return null;
        }
        if (!res.ok) throw new Error("Failed to fetch audit events");
        return res.json();
      })
      .then(data => {
        if (data && data.events) {
          // Filter to just this document
          setAuditEvents(data.events.filter(e => e.document_id === selectedDoc.document_id));
        } else {
          setAuditEvents([]);
        }
      })
      .catch(err => console.error("Audit fetch error:", err))
      .finally(() => setIsLoadingAudit(false));
  }, [caseId, selectedDoc]);

  // Aggregate Timeline Data
  const timeline = [];

  // 1. Versions
  if (selectedDoc && selectedDoc.versions) {
    selectedDoc.versions.forEach((v) => {
      timeline.push({
        id: `ver-${v.version_id}`,
        type: 'version',
        timestamp: new Date(v.created_at),
        data: v
      });
    });
  }

  // 2. Integrity Status (Current)
  // If we have an integrity status, treat it as a point in time if possible.
  // We don't have a distinct history of integrity checks in the frontend state, 
  // just the *current* check result. We'll add it to the top (now) or based on audit if available.
  if (integrityStatus) {
    // If the audit log has VERIFY_INTEGRITY, the audit event will show it.
    // However, the user specifically requested to show the *current* integrity status in the timeline or as a distinct block.
    // Let's place it at the current time since it was just run.
    timeline.push({
      id: `int-current-${Date.now()}`,
      type: 'integrity',
      timestamp: new Date(), // It was verified right now in the UI session
      data: integrityStatus
    });
  }

  // 3. Audit Events
  auditEvents.forEach(e => {
    timeline.push({
      id: `audit-${e.id}`,
      type: 'audit',
      timestamp: new Date(e.timestamp),
      data: e
    });
  });

  // Sort chronological (descending - newest first)
  timeline.sort((a, b) => b.timestamp - a.timestamp);

  // Deriving Last Activity
  const lastActivity = timeline.length > 0 ? timeline[0].timestamp : null;

  return (
    <div className="flex flex-col h-full">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-600" />
            Evidence Chain
          </h3>
          <p className="text-xs text-slate-500 mt-1">Trace the document's lifecycle, versions, integrity checks, and recorded activities.</p>
        </div>
        <div className="hidden md:flex bg-slate-900 text-white text-[10px] uppercase font-bold tracking-wider px-3 py-1.5 rounded-full items-center gap-1.5 shadow-sm">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          Authorization Enforced
        </div>
      </div>

      {/* Summary Panel */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Versions</span>
          <span className="text-lg font-bold text-slate-800">{selectedDoc?.versions?.length || 0}</span>
        </div>
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Audit Activity</span>
          {auditRestricted ? (
            <span className="text-xs font-semibold text-rose-600 flex items-center gap-1 mt-1"><Lock className="w-3.5 h-3.5"/> Restricted</span>
          ) : (
            <span className="text-lg font-bold text-slate-800">{isLoadingAudit ? '...' : auditEvents.length}</span>
          )}
        </div>
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Integrity</span>
          {integrityStatus ? (
            integrityStatus.status === 'INTEGRITY_VERIFIED' 
              ? <span className="text-xs font-bold text-emerald-600 flex items-center gap-1 mt-1"><ShieldCheck className="w-3.5 h-3.5"/> Verified</span>
              : <span className="text-xs font-bold text-rose-600 flex items-center gap-1 mt-1"><AlertTriangle className="w-3.5 h-3.5"/> Failed</span>
          ) : (
            <span className="text-xs font-medium text-slate-500 mt-1 block">Unverified</span>
          )}
        </div>
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Last Activity</span>
          <span className="text-xs font-medium text-slate-700">
            {lastActivity ? lastActivity.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }) : 'None'}
          </span>
        </div>
      </div>

      {/* Timeline */}
      <div className="relative flex-1">
        {timeline.length === 0 ? (
          <div className="py-8 text-center border-t border-slate-100">
            <span className="text-slate-400 text-sm">No recorded activity. Document activity will appear here as actions are performed.</span>
          </div>
        ) : (
          <div className="absolute left-4 top-2 bottom-0 w-0.5 bg-slate-200"></div>
        )}

        <div className="space-y-6 max-h-[600px] overflow-y-auto custom-scrollbar pr-2 pb-4">
          {timeline.map((item, index) => {
            const isFirst = index === 0;

            if (item.type === 'version') {
              const v = item.data;
              return (
                <div key={item.id} className="relative pl-10">
                  <div className={`absolute left-[11px] top-1.5 w-2.5 h-2.5 rounded-full border-2 border-white z-10 ${isFirst ? 'bg-blue-600 ring-4 ring-blue-100' : 'bg-slate-400'}`}></div>
                  <div className="human-card border border-slate-200 bg-white p-4 rounded-xl shadow-sm hover:border-slate-300 transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-bold text-slate-800 text-sm flex items-center gap-2">
                        <FilePlus className="w-4 h-4 text-blue-500" />
                        Version {v.version_number} Created
                      </h4>
                      <span className="text-[10px] font-medium text-slate-500">{item.timestamp.toLocaleString()}</span>
                    </div>
                    <div className="text-xs text-slate-600 space-y-1">
                      <p><span className="font-semibold text-slate-500">Created by:</span> {v.created_by}</p>
                      <p><span className="font-semibold text-slate-500">Change:</span> {v.change_description}</p>
                      <div className="mt-2 bg-slate-50 border border-slate-100 p-2 rounded text-[10px] font-mono text-slate-500 break-all">
                        SHA-256: {v.sha256_hash}
                      </div>
                    </div>
                  </div>
                </div>
              );
            }

            if (item.type === 'integrity') {
              const stat = item.data;
              const isVerified = stat.status === 'INTEGRITY_VERIFIED';
              return (
                <div key={item.id} className="relative pl-10">
                  <div className={`absolute left-[11px] top-1.5 w-2.5 h-2.5 rounded-full border-2 border-white z-10 ${isVerified ? 'bg-emerald-500' : 'bg-rose-500'}`}></div>
                  <div className={`border p-4 rounded-xl shadow-sm ${isVerified ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'}`}>
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-bold text-sm flex items-center gap-2">
                        {isVerified ? <ShieldCheck className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
                        {isVerified ? 'Integrity Verified ✓' : 'Integrity Verification Failed'}
                      </h4>
                      <span className="text-[10px] font-medium opacity-70">Current Session</span>
                    </div>
                    <div className="text-xs space-y-1 opacity-90 font-mono break-all mt-3">
                      <p><span className="font-semibold font-sans">Version Checked:</span> {stat.version_number}</p>
                      <p><span className="font-semibold font-sans mt-1 block">Expected:</span> {stat.expected_hash}</p>
                      <p><span className="font-semibold font-sans mt-1 block">Actual:</span> {stat.actual_hash}</p>
                    </div>
                  </div>
                </div>
              );
            }

            if (item.type === 'audit') {
              const e = item.data;
              const isDenied = e.result === 'ACCESS_DENIED';
              const isVerify = e.action === 'VERIFY_INTEGRITY';
              const isView = e.action === 'VIEW_DOCUMENT';
              
              let Icon = FileText;
              if (isDenied) Icon = AlertTriangle;
              if (isVerify) Icon = ShieldCheck;
              if (isView) Icon = Eye;

              return (
                <div key={item.id} className="relative pl-10">
                  <div className="absolute left-[11px] top-1.5 w-2.5 h-2.5 rounded-full border-2 border-white z-10 bg-slate-300"></div>
                  <div className={`p-3 rounded-lg border ${isDenied ? 'bg-rose-50 border-rose-100' : 'bg-slate-50 border-slate-100'}`}>
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-2">
                        <Icon className={`w-3.5 h-3.5 ${isDenied ? 'text-rose-500' : 'text-slate-400'}`} />
                        <span className={`text-xs font-bold ${isDenied ? 'text-rose-700' : 'text-slate-700'}`}>{e.action}</span>
                      </div>
                      <span className="text-[10px] text-slate-500">{item.timestamp.toLocaleString()}</span>
                    </div>
                    <div className="mt-1.5 text-[11px] text-slate-600 flex gap-4">
                      <span><span className="font-medium">User:</span> {e.username} ({e.role})</span>
                      <span><span className="font-medium">Outcome:</span> <span className={isDenied ? 'text-rose-600 font-bold' : ''}>{e.result}</span></span>
                      {e.version && <span><span className="font-medium">Ver:</span> {e.version}</span>}
                    </div>
                  </div>
                </div>
              );
            }

            return null;
          })}
        </div>
      </div>
    </div>
  );
}
