import React, { createContext, useContext, useState } from 'react';

const InvestigationContext = createContext();

export function InvestigationProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const saved = localStorage.getItem('sih_currentUser');
      return saved ? JSON.parse(saved) : { name: 'Investigator', role: 'Investigator' };
    } catch {
      return { name: 'Investigator', role: 'Investigator' };
    }
  });
  
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [activeCaseId, setActiveCaseId] = useState(localStorage.getItem('selected_case_id') || null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const [isFloatingAIOpen, setIsFloatingAIOpen] = useState(false);
  const [isAIExpanded, setIsAIExpanded] = useState(false);
  const [aiMessages, setAiMessages] = useState([
    {
      sender: 'ai',
      text: 'Namaste! I am your AI Evidence Assistant. How can I help you analyze this case today?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      evidence: []
    }
  ]);

  const [toasts, setToasts] = useState([]);
  const [activeModal, setActiveModal] = useState(null);
  const [modalData, setModalData] = useState(null);

  const [globalSearchQuery, setGlobalSearchQuery] = useState('');

  const [pinnedDocuments, setPinnedDocuments] = useState(() => {
    try {
      const saved = localStorage.getItem('sih_pinnedDocuments');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const pinDocument = (doc, caseId) => {
    if (!pinnedDocuments.some(p => p.documentId === doc.document_id)) {
      const newPins = [...pinnedDocuments, {
        documentId: doc.document_id,
        caseId: caseId,
        x: 100 + Math.random() * 100,
        y: 100 + Math.random() * 100
      }];
      setPinnedDocuments(newPins);
      localStorage.setItem('sih_pinnedDocuments', JSON.stringify(newPins));
    }
  };

  const unpinDocument = (documentId) => {
    const newPins = pinnedDocuments.filter(p => p.documentId !== documentId);
    setPinnedDocuments(newPins);
    localStorage.setItem('sih_pinnedDocuments', JSON.stringify(newPins));
  };

  const isDocumentPinned = (documentId) => {
    return pinnedDocuments.some(p => p.documentId === documentId);
  };

  const updateBoardPosition = (documentId, x, y) => {
    const newPins = pinnedDocuments.map(p => 
      p.documentId === documentId ? { ...p, x, y } : p
    );
    setPinnedDocuments(newPins);
    localStorage.setItem('sih_pinnedDocuments', JSON.stringify(newPins));
  };

  const showToast = (message, type = 'success') => {
    const id = Date.now() + Math.random();
    setToasts(prev => [...prev.filter(t => t.message !== message).slice(-1), { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 2500);
  };
  const removeToast = (id) => setToasts(prev => prev.filter(t => t.id !== id));

  const navigate = (page, params = {}) => {
    if (params.caseId) {
      setActiveCaseId(params.caseId);
      localStorage.setItem('selected_case_id', params.caseId);
    }
    setCurrentPage(page);
    setIsMobileMenuOpen(false);
  };

  const login = (name) => {
    setIsAuthenticated(true);
    setCurrentUser({ name: name, role: localStorage.getItem('role') || 'Investigator' });
    setCurrentPage('dashboard');
    showToast(`Welcome back, ${name}`, 'success');
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    setIsAuthenticated(false);
    setCurrentPage('login');
  };

  const setUserRole = (role) => {
    setCurrentUser(prev => ({ ...prev, role }));
  };

  const askAI = async (queryText) => {
    if (!queryText.trim()) return;

    const userMsg = { sender: 'user', text: queryText, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) };
    const loadingId = Date.now();
    setAiMessages(prev => [...prev, userMsg, { id: loadingId, sender: 'ai', text: 'Analyzing documents...', isLoading: true, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);

    try {
      const response = await fetch('/api/ai/query', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ query: queryText, scenario_id: 'S01' })
      });
      
      if (!response.ok) throw new Error('Backend error or unauthorized');
      
      const data = await response.json();
      if (data.status === 'success' && data.llm_response) {
        setAiMessages(prev => prev.map(msg => msg.id === loadingId ? {
          sender: 'ai',
          text: data.llm_response.answer || 'No answer provided.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          citations: data.llm_response.citations || [],
          evidence_basis: data.llm_response.evidence_basis || null,
          confidence: data.llm_response.confidence || 'insufficient',
          mode: data.llm_response.mode || 'retrieval'
        } : msg));
      } else throw new Error('Malformed response');
    } catch (err) {
      setAiMessages(prev => prev.map(msg => msg.id === loadingId ? {
        sender: 'ai',
        text: 'AI analysis is temporarily unavailable or access was denied.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        mode: 'error', confidence: 'insufficient'
      } : msg));
    }
  };

  return (
    <InvestigationContext.Provider value={{
      currentUser, isAuthenticated, login, logout, setUserRole,
      currentPage, setCurrentPage, activeCaseId, setActiveCaseId, navigate,
      isMobileMenuOpen, toggleMobileMenu: () => setIsMobileMenuOpen(!isMobileMenuOpen),
      isFloatingAIOpen, toggleFloatingAI: () => setIsFloatingAIOpen(!isFloatingAIOpen),
      isAIExpanded, toggleAIExpand: () => setIsAIExpanded(!isAIExpanded),
      aiMessages, askAI, toasts, showToast, removeToast,
      activeModal, modalData, openModal: (m, d) => { setActiveModal(m); setModalData(d); }, closeModal: () => { setActiveModal(null); setModalData(null); },
      globalSearchQuery, setGlobalSearchQuery,
      pinnedDocuments, pinDocument, unpinDocument, isDocumentPinned, updateBoardPosition
    }}>
      {children}
    </InvestigationContext.Provider>
  );
}

export function useInvestigation() {
  const context = useContext(InvestigationContext);
  if (!context) throw new Error('useInvestigation must be used within an InvestigationProvider');
  return context;
}
