import React, { useState } from 'react';
import { useInvestigation } from '../../context/InvestigationContext.jsx';
import { 
  Shield, 
  Search, 
  Menu, 
  LogOut, 
  Home, 
  Settings, 
  FileText, 
  X, 
  ChevronRight,
  Pin,
  PinOff,
  ClipboardList,
  BarChart
} from 'lucide-react';

export function TopBar() {
  const { 
    currentUser, 
    logout, 
    toggleMobileMenu, 
    navigate,
    globalSearchQuery,
    setGlobalSearchQuery
  } = useInvestigation();


  return (
      <header className="h-16 bg-white border-b border-slate-200 sticky top-0 z-30 flex items-center justify-between px-4 md:px-6 select-none font-sans shadow-sm">
      {/* Left: Brand Logo & Title */}
      <div className="flex items-center space-x-3.5">
        <button 
          onClick={toggleMobileMenu}
          className="md:hidden p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
          title="Toggle Navigation Menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div 
          onClick={() => navigate('dashboard')}
          className="flex items-center space-x-3 cursor-pointer group"
        >
          <div className="w-9 h-9 rounded-lg bg-slate-900 text-white flex items-center justify-center font-bold text-sm shadow-sm group-hover:bg-blue-600 transition-colors">
            <Shield className="w-4.5 h-4.5 text-blue-400 group-hover:text-white transition-colors" />
          </div>
          <div>
            <div className="font-bold text-slate-900 text-sm tracking-tight flex items-center space-x-2">
              <span>OMNIGUARD DMS</span>
            </div>
            <p className="text-[11px] text-slate-500 hidden sm:block">Secure Evidence Lifecycle & Analysis</p>
          </div>
        </div>
      </div>

      {/* Center: Global Search */}
      <div className="hidden lg:flex items-center flex-1 max-w-md mx-6 relative">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3 pointer-events-none" />
          <input 
            type="text" 
            placeholder="Search documents, cases, keywords..." 
            className="w-full bg-white border border-slate-300 rounded-lg pl-10 pr-4 py-2 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 shadow-sm transition-all"
            value={globalSearchQuery}
            onChange={(e) => setGlobalSearchQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && globalSearchQuery.trim()) {
                navigate('search');
              }
            }}
          />
        </div>
      </div>

      {/* Right: Actions & Role Switching */}
      <div className="flex items-center space-x-2.5">
        {/* User Profile & Logout */}
        <div className="flex items-center space-x-1.5 pl-1">
          <div className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center font-bold text-xs shadow-sm" title={`${currentUser.name} (${currentUser.role})`}>
            {currentUser.name ? currentUser.name.charAt(0) : 'U'}
          </div>

          <button 
            onClick={logout}
            className="p-2 text-slate-400 hover:text-rose-600 hover:bg-slate-100 rounded-lg transition-colors"
            title="Sign Out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}

export function Sidebar() {
  const { 
    currentPage, 
    currentUser, 
    navigate, 
    isMobileMenuOpen, 
    toggleMobileMenu
  } = useInvestigation();

  const [isHovered, setIsHovered] = useState(false);
  const [isPinned, setIsPinned] = useState(false);

  const isAdmin = currentUser && currentUser.role === 'Admin';
  const isExpanded = isHovered || isPinned;

  const navItems = [
    { 
      id: 'dashboard', 
      label: 'Document Management', 
      icon: Home
    },
    { 
      id: 'search', 
      label: 'Global Search', 
      icon: Search
    },
    { 
      id: 'document_viewer', 
      label: 'Document Viewer', 
      icon: FileText
    },
    { 
      id: 'board', 
      label: 'Evidence Board', 
      icon: ClipboardList
    },
    { 
      id: 'audit', 
      label: 'Security Audit Trail', 
      icon: Shield,
      adminOnly: true
    },
    { 
      id: 'analytics', 
      label: 'System Analytics', 
      icon: BarChart,
      adminOnly: true
    }
  ];

  const renderSidebarContent = (mobile = false) => {
    const showFull = mobile || isExpanded;

    return (
      <div className="p-3 space-y-4 flex-1 overflow-y-auto overflow-x-hidden font-sans text-xs flex flex-col justify-between">
        <div className="space-y-4">
          {/* Header Bar inside Sidebar */}
          <div className="flex items-center justify-between px-2.5 h-7">
            {showFull ? (
              <>
                <div className="flex items-center space-x-1.5">
                  <span className="text-[10px] font-bold uppercase text-slate-400 tracking-wider">
                    Navigation
                  </span>
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-300"></span>
                  <span className="text-[10px] text-slate-400 font-medium">8 Modules</span>
                </div>
                {!mobile && (
                  <button 
                    onClick={() => {
                      const next = !isPinned;
                      setIsPinned(next);
                      showToast(next ? 'Sidebar pinned open' : 'Sidebar set to hover expand', 'info');
                    }}
                    className={`p-1.5 rounded-lg transition-all ${
                      isPinned 
                        ? 'bg-slate-900 text-white shadow-xs' 
                        : 'text-slate-400 hover:text-slate-700 hover:bg-slate-100'
                    }`}
                    title={isPinned ? 'Unpin sidebar (hover mode)' : 'Pin sidebar open'}
                  >
                    {isPinned ? <PinOff className="w-3.5 h-3.5" /> : <Pin className="w-3.5 h-3.5" />}
                  </button>
                )}
                {mobile && (
                  <button onClick={toggleMobileMenu} className="text-slate-400 hover:text-slate-700 p-1 rounded-full">
                    <X className="w-4 h-4" />
                  </button>
                )}
              </>
            ) : (
              <div className="w-full flex justify-center">
                <button 
                  onClick={() => setIsPinned(true)}
                  className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
                  title="Hover to expand or click to pin"
                >
                  <Pin className="w-3.5 h-3.5" />
                </button>
              </div>
            )}
          </div>

          {/* Navigation Items */}
          <nav className="space-y-1">
            {navItems.map(item => {
              if (item.adminOnly && !isAdmin) return null;
              const Icon = item.icon;
              const isActive = currentPage === item.id || (item.id === 'overview' && (currentPage === 'overview' || currentPage === 'analysis'));

              return (
                <button 
                  key={item.id}
                  onClick={() => {
                    navigate(item.id);
                    if (mobile) toggleMobileMenu();
                  }}
                  title={!showFull ? item.label : undefined}
                  className={`w-full flex items-center transition-all duration-150 relative ${
                    showFull ? 'justify-between px-3 py-2 rounded-lg' : 'justify-center p-2.5 rounded-lg'
                  } font-medium group ${
                    isActive 
                      ? 'bg-slate-100 text-slate-900 font-semibold border border-slate-200' 
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  {isActive && <span className="absolute left-0 top-1.5 bottom-1.5 w-1 bg-blue-600 rounded-r-md"></span>}
                  <div className="flex items-center space-x-2.5 min-w-0">
                    <div className={`p-1 rounded-md transition-colors shrink-0 ${
                      isActive 
                        ? 'text-blue-600' 
                        : 'text-slate-400 group-hover:text-slate-600'
                    }`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    {showFull && (
                      <span className="text-xs truncate font-medium tracking-tight">{item.label}</span>
                    )}
                  </div>

                  {showFull && (
                    <div className="flex items-center space-x-1.5 shrink-0 pl-1">
                      {item.isLive && (
                        <span className={`inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-[9px] font-bold tracking-wider uppercase transition-colors ${
                          isActive
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : 'bg-emerald-50/50 text-emerald-600 border border-emerald-100'
                        }`}>
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                          <span>LIVE</span>
                        </span>
                      )}

                      {item.adminOnly && (
                        <span className={`text-[9px] font-bold tracking-wider px-1.5 py-0.5 rounded uppercase transition-colors ${
                          isActive 
                            ? 'bg-amber-50 text-amber-700 border border-amber-200' 
                            : 'bg-amber-50/50 text-amber-600 border border-amber-100'
                        }`}>
                          ADMIN
                        </span>
                      )}

                      {!item.isLive && !item.adminOnly && item.badge && (
                        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded transition-colors ${
                          isActive 
                            ? 'bg-white text-slate-700 border border-slate-200 shadow-sm' 
                            : 'bg-slate-100 text-slate-500 border border-slate-200 group-hover:bg-slate-200'
                        }`}>
                          {item.badge}
                        </span>
                      )}
                    </div>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Bottom Section: Officer Profile */}
        <div className="space-y-3 pt-3 border-t border-slate-200">
          <div className={`border border-slate-200 bg-slate-50 rounded-xl transition-all shadow-sm ${
            showFull ? 'p-2.5' : 'p-2 flex justify-center'
          }`}>
            <div className="flex items-center space-x-2.5">
              <div className="relative shrink-0">
                <div 
                  className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center font-bold text-xs border border-slate-700" 
                  title={`${currentUser.name} (${currentUser.role})`}
                >
                  {currentUser.name ? currentUser.name.charAt(0) : 'O'}
                </div>
                <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 border border-white rounded-full"></span>
              </div>

              {showFull && (
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between">
                    <div className="font-semibold text-slate-900 text-xs truncate">{currentUser.name}</div>
                    <span className="text-[9px] font-semibold text-slate-500 uppercase tracking-wider">{currentUser.role || 'Officer'}</span>
                  </div>
                  <div className="text-[10px] text-slate-500 truncate">Document Management</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <>
      {/* Desktop Hover-Expandable Sidebar (Auto-Adjusts Page Layout) */}
      <aside 
        className={`hidden md:flex flex-col justify-between bg-white border-r border-slate-200/90 h-[calc(100vh-4rem)] sticky top-16 select-none shrink-0 transition-all duration-300 ease-in-out overflow-x-hidden ${
          isExpanded ? 'w-64 shadow-md' : 'w-20 shadow-2xs'
        }`}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {renderSidebarContent(false)}
      </aside>

      {/* Mobile Drawer Overlay */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs md:hidden flex">
          <aside className="w-72 max-w-[85vw] bg-white border-r border-slate-200 flex flex-col justify-between h-full shadow-2xl">
            {renderSidebarContent(true)}
          </aside>
          <div className="flex-1" onClick={toggleMobileMenu}></div>
        </div>
      )}
    </>
  );
}

export function Breadcrumbs() {
  const { currentPage, activeCaseId, activeAnalysisTab, navigate } = useInvestigation();

    const getPageTitle = (page) => {
    switch (page) {
      case 'search': return 'Global Search';
      case 'dashboard': return 'Document Management';
      case 'document_viewer': return 'Document Viewer';
      case 'board': return 'Evidence Board';
      case 'audit': return 'Security Audit Trail';
      default: return page;
    }
  };

  return (
    <div className="bg-white border-b border-slate-200/80 px-4 md:px-6 py-2.5 flex items-center space-x-2 text-xs font-sans text-slate-500">
      <button 
        onClick={() => navigate('dashboard')}
        className="flex items-center space-x-1 hover:text-slate-900 transition-colors font-medium"
      >
        <Home className="w-3.5 h-3.5 text-slate-400" />
        <span>Hub</span>
      </button>

      <ChevronRight className="w-3.5 h-3.5 text-slate-300" />
      <span className="font-semibold text-slate-800">{getPageTitle(currentPage)}</span>
    </div>
  );
}
