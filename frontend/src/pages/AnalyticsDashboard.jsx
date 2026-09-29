import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, ShieldAlert, FileText, FolderOpen, Loader2 } from 'lucide-react';

export function AnalyticsDashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/analytics/summary', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(res => {
        if (!res.ok) throw new Error("Analytics access denied. Ensure you are an administrator.");
        return res.json();
      })
      .then(setData)
      .catch(err => setError(err.message));
  }, []);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-rose-500 py-20">
        <ShieldAlert className="w-12 h-12 mb-4" />
        <h2 className="text-xl font-bold">Access Denied</h2>
        <p>{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-slate-500 py-20">
        <Loader2 className="w-8 h-8 animate-spin mb-4" />
        <p>Loading analytics data...</p>
      </div>
    );
  }

  const COLORS = ['#10b981', '#f43f5e'];

  return (
    <div className="max-w-7xl mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800">System Analytics</h1>
        <p className="text-slate-500 mt-2">Overview of security health and platform utilization.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="human-card p-6 flex items-center gap-4 border-l-4 border-blue-500">
          <div className="bg-blue-100 p-3 rounded-xl"><FolderOpen className="w-6 h-6 text-blue-600" /></div>
          <div>
            <p className="text-sm font-semibold text-slate-500 uppercase tracking-wide">Total Cases</p>
            <h3 className="text-3xl font-black text-slate-800">{data.summary.total_cases}</h3>
          </div>
        </div>
        
        <div className="human-card p-6 flex items-center gap-4 border-l-4 border-indigo-500">
          <div className="bg-indigo-100 p-3 rounded-xl"><FileText className="w-6 h-6 text-indigo-600" /></div>
          <div>
            <p className="text-sm font-semibold text-slate-500 uppercase tracking-wide">Documents</p>
            <h3 className="text-3xl font-black text-slate-800">{data.summary.total_documents}</h3>
          </div>
        </div>

        <div className="human-card p-6 flex items-center gap-4 border-l-4 border-emerald-500">
          <div className="bg-emerald-100 p-3 rounded-xl"><Activity className="w-6 h-6 text-emerald-600" /></div>
          <div>
            <p className="text-sm font-semibold text-slate-500 uppercase tracking-wide">System Actions</p>
            <h3 className="text-3xl font-black text-slate-800">{data.activity_breakdown.reduce((acc, curr) => acc + curr.value, 0)}</h3>
          </div>
        </div>

        <div className="human-card p-6 flex items-center gap-4 border-l-4 border-rose-500">
          <div className="bg-rose-100 p-3 rounded-xl"><ShieldAlert className="w-6 h-6 text-rose-600" /></div>
          <div>
            <p className="text-sm font-semibold text-slate-500 uppercase tracking-wide">Tamper Alerts</p>
            <h3 className="text-3xl font-black text-rose-600">{data.summary.tamper_alerts}</h3>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="human-card p-6 border border-slate-200">
          <h3 className="text-lg font-bold text-slate-800 mb-6">Activity Audit Logs</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.activity_breakdown}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                <Tooltip cursor={{fill: '#f1f5f9'}} contentStyle={{borderRadius: '0.75rem', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="human-card p-6 border border-slate-200">
          <h3 className="text-lg font-bold text-slate-800 mb-6">File Integrity Status</h3>
          <div className="h-80 flex flex-col justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.integrity_stats}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={120}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {data.integrity_stats.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{borderRadius: '0.75rem', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                <Legend verticalAlign="bottom" height={36} iconType="circle" />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
