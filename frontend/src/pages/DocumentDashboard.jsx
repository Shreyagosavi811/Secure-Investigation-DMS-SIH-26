import React, { useEffect, useState } from 'react';
import { useInvestigation } from '../context/InvestigationContext';
import { Loader2 } from 'lucide-react';
import { EmptyState } from '../components/common/EmptyState';

export function DocumentDashboard() {
  const { setCurrentPage } = useInvestigation();
  const [cases, setCases] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch('/api/cases/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch cases");
        return res.json();
      })
      .then(data => {
        if(data.cases) setCases(data.cases);
      })
      .catch(err => console.error(err))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Welcome to OmniGuard</h1>
        <p className="text-slate-500 mt-2 text-base">Select a case below to securely view evidence, read investigation reports, and analyze data.</p>
      </div>
      
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20 text-slate-500">
          <Loader2 className="w-8 h-8 animate-spin mb-4 text-slate-400" />
          <p>Loading authorized records...</p>
        </div>
      ) : cases.length === 0 ? (
        <EmptyState 
          type="cases" 
          title="No Cases Available" 
          message="You do not currently have access to any cases. Please contact your administrator if you believe this is an error."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cases.map((c) => (
            <div key={c.case_id} className="human-card p-6 flex flex-col h-full">
              <div className="flex-1">
                <h2 className="text-xl font-bold text-slate-800 leading-tight mb-1">{c.title}</h2>
                <p className="text-xs font-mono text-slate-400 mb-4">{c.case_id}</p>
                <p className="text-sm text-slate-600 line-clamp-3">{c.description}</p>
              </div>
              <div className="mt-6 flex justify-between items-center pt-4 border-t border-slate-100">
                <span className="badge-pill badge-light-indigo px-3 py-1 bg-indigo-50 text-indigo-700">{c.classification}</span>
                <button 
                  onClick={() => {
                    localStorage.setItem('selected_case_id', c.case_id);
                    setCurrentPage('document_viewer');
                  }}
                  className="btn-ghost text-blue-600"
                >
                  View Documents &rarr;
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
