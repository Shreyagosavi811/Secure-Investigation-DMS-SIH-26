import React, { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { EmptyState } from '../components/common/EmptyState';

export function AuditTrail() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/audit/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then(async res => {
        if (!res.ok) throw new Error("Access Denied or insufficient permissions");
        return res.json();
      })
      .then(data => {
        if(data.events) setEvents(data.events);
      })
      .catch(err => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (error) {
    return (
      <div className="max-w-7xl mx-auto p-4 md:p-6">
        <EmptyState 
          type="error"
          title="Access Denied"
          message={error}
        />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Security Audit Trail</h1>
        <p className="text-slate-500 mt-1">Immutable ledger of all system access and verification events.</p>
      </div>

      <div className="human-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600 relative">
            <thead className="bg-slate-50/90 backdrop-blur-sm border-b border-slate-200 text-xs uppercase text-slate-500 font-bold tracking-wider sticky top-0 z-10 shadow-sm">
              <tr>
                <th className="px-6 py-4">Timestamp</th>
                <th className="px-6 py-4">User</th>
                <th className="px-6 py-4">Role</th>
                <th className="px-6 py-4">Action</th>
                <th className="px-6 py-4">Resource</th>
                <th className="px-6 py-4">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-slate-500">
                    <div className="flex flex-col items-center justify-center">
                      <Loader2 className="w-6 h-6 animate-spin mb-3 text-slate-400" />
                      <p>Loading audit events...</p>
                    </div>
                  </td>
                </tr>
              ) : events.length === 0 ? (
                <tr>
                  <td colSpan="6" className="p-0">
                    <EmptyState 
                      type="documents"
                      title="No Audit Events"
                      message="There are no audit events available or you do not have permission to view them."
                    />
                  </td>
                </tr>
              ) : (
                events.map(event => (
                  <tr key={event.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-slate-500">{new Date(event.timestamp).toLocaleString()}</td>
                    <td className="px-6 py-4 font-bold text-slate-800">{event.username}</td>
                    <td className="px-6 py-4">
                      <span className="badge-pill bg-slate-100 text-slate-600 border border-slate-200">{event.role}</span>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs">{event.action}</td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-500">{event.document_id || event.case_id || 'N/A'}</td>
                    <td className="px-6 py-4">
                      <span className={`badge-pill ${
                        event.result === 'SUCCESS' || event.result === 'INTEGRITY_VERIFIED' 
                        ? 'badge-light-green' 
                        : event.result.includes('DENIED') || event.result.includes('TAMPER')
                        ? 'badge-light-rose'
                        : 'bg-slate-100 text-slate-700 border border-slate-200'
                      }`}>
                        {event.result}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
