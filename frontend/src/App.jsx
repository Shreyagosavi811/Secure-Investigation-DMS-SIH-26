import React from 'react';
import { InvestigationProvider, useInvestigation } from './context/InvestigationContext.jsx';
import { TopBar, Sidebar, Breadcrumbs } from './components/layout/Layout.jsx';
import { FloatingAI } from './components/ai/FloatingAI.jsx';
import { Overlays } from './components/common/Overlays.jsx';

// SIH26190 Pages
import { Login } from './pages/Login.jsx';
import { DocumentDashboard } from './pages/DocumentDashboard.jsx';
import { DocumentViewer } from './pages/DocumentViewer.jsx';
import { AuditTrail } from './pages/AuditTrail.jsx';
import { GlobalSearch } from './pages/GlobalSearch.jsx';
import { EvidenceBoard } from './pages/EvidenceBoard.jsx';
import { AnalyticsDashboard } from './pages/AnalyticsDashboard.jsx';

function MainAppContent() {
  const { currentPage, isAuthenticated } = useInvestigation();

  if (!isAuthenticated || currentPage === 'login') {
    return <Login />;
  }

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'search':
        return <GlobalSearch />;
      case 'dashboard':
        return <DocumentDashboard />;
      case 'document_viewer':
        return <DocumentViewer />;
      case 'board':
        return <EvidenceBoard />;
      case 'audit':
        return <AuditTrail />;
      case 'analytics':
        return <AnalyticsDashboard />;
      default:
        return <DocumentDashboard />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800 font-sans">
      <TopBar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 flex flex-col min-w-0 overflow-y-auto transition-all duration-300 ease-in-out">
          <Breadcrumbs />
          <div className="p-3 sm:p-4 md:p-6 flex-1">
            {renderCurrentPage()}
          </div>
        </main>
      </div>

      <FloatingAI />
      <Overlays />
    </div>
  );
}

export function App() {
  return (
    <InvestigationProvider>
      <MainAppContent />
    </InvestigationProvider>
  );
}

export default App;
