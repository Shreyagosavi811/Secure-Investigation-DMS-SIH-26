import React, { useState, useEffect } from 'react';
import { useInvestigation } from '../context/InvestigationContext';
import { Search, FileText, FolderGit2, Loader2 } from 'lucide-react';
import { EmptyState } from '../components/common/EmptyState';

export function GlobalSearch() {
  const { navigate, globalSearchQuery, setGlobalSearchQuery, showToast } = useInvestigation();
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!globalSearchQuery.trim()) {
      setResults([]);
      return;
    }

    const performSearch = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch authorized cases
        const res = await fetch('/api/cases/', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        if (!res.ok) throw new Error("Search failed");
        
        const data = await res.json();
        const cases = data.cases || [];
        
        const q = globalSearchQuery.toLowerCase();
        let matched = [];

        for (const c of cases) {
          // Check if case matches
          if (c.title?.toLowerCase().includes(q) || c.case_id?.toLowerCase().includes(q)) {
            matched.push({
              type: 'CASE',
              id: c.case_id,
              title: c.title,
              subtitle: c.classification,
              caseId: c.case_id
            });
          }

          // Fetch documents for the case to search them
          try {
            const caseRes = await fetch(`/api/cases/${c.case_id}`, {
              headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (caseRes.ok) {
              const caseData = await caseRes.json();
              const docs = caseData.documents || [];
              for (const d of docs) {
                if (d.title?.toLowerCase().includes(q) || d.type?.toLowerCase().includes(q) || d.document_id?.toLowerCase().includes(q)) {
                  matched.push({
                    type: 'DOCUMENT',
                    id: d.document_id,
                    title: d.title,
                    subtitle: `Case: ${c.case_id} • Type: ${d.type}`,
                    caseId: c.case_id,
                    documentId: d.document_id
                  });
                }
              }
            }
          } catch (e) {
            // Ignore individual case fetch errors
          }
        }

        setResults(matched);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    const delayDebounceFn = setTimeout(() => {
      performSearch();
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [globalSearchQuery]);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col mb-8">
        <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Global Document Search</h1>
        <p className="text-slate-500 mt-1">Search across all authorized cases and documents.</p>
      </div>

      <div className="relative">
        <Search className="w-5 h-5 text-slate-400 absolute left-4 top-4 pointer-events-none" />
        <input 
          type="text" 
          placeholder="Search documents, cases, keywords..." 
          className="w-full bg-white border border-slate-200 rounded-xl pl-12 pr-4 py-3.5 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 shadow-sm transition-all font-medium"
          value={globalSearchQuery}
          onChange={(e) => setGlobalSearchQuery(e.target.value)}
        />
      </div>

      <div className="mt-8">
        {error && <div className="text-red-500 bg-red-50 p-4 rounded-lg font-medium">{error}</div>}
        
        {loading && (
          <div className="flex flex-col items-center justify-center py-12 text-slate-500">
            <Loader2 className="w-8 h-8 animate-spin mb-4 text-slate-400" />
            <p>Searching authorized records...</p>
          </div>
        )}
        
        {!loading && !error && globalSearchQuery && results.length === 0 && (
          <EmptyState 
            type="search" 
            title="No Results Found" 
            message={`We couldn't find any cases or documents matching "${globalSearchQuery}". Try different keywords or check your spelling.`} 
          />
        )}
        
        {!loading && !error && results.length > 0 && (
          <div className="space-y-4">
            {results.map((res, i) => (
              <div 
                key={i}
                onClick={() => {
                  if (res.caseId) {
                    localStorage.setItem('selected_case_id', res.caseId);
                    navigate('document_viewer');
                  }
                }}
                className="human-card p-5 cursor-pointer flex items-center gap-5"
              >
                <div className={`p-3 rounded-xl ${res.type === 'CASE' ? 'bg-indigo-50 text-indigo-600' : 'bg-blue-50 text-blue-600'}`}>
                  {res.type === 'CASE' ? <FolderGit2 className="w-6 h-6" /> : <FileText className="w-6 h-6" />}
                </div>
                <div className="flex-1">
                  <h3 className="font-bold text-slate-800 text-lg">{res.title}</h3>
                  <p className="text-sm text-slate-500 font-medium mt-1">{res.subtitle}</p>
                </div>
                <div className={`shrink-0 badge-pill ${res.type === 'CASE' ? 'badge-light-indigo' : 'badge-light-blue'}`}>
                  {res.type}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

