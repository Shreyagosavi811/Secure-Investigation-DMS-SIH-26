import React from 'react';
import { useInvestigation } from '../../context/InvestigationContext.jsx';
import { 
  X, 
  CheckCircle, 
  Info, 
  AlertTriangle 
} from 'lucide-react';

/* 1. TOAST NOTIFICATIONS CONTAINER */
export function ToastContainer() {
  const { toasts, removeToast } = useInvestigation();

  if (!toasts || toasts.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end space-y-2 pointer-events-none max-w-sm w-full px-4">
      {toasts.map(toast => (
        <div 
          key={toast.id}
          className="pointer-events-auto w-full max-w-sm px-3.5 py-2.5 rounded-xl bg-slate-900/95 text-white border border-slate-700/80 font-sans text-xs shadow-2xl flex items-center justify-between gap-3 backdrop-blur-md transition-all animate-slide-up"
        >
          <div className="flex items-center space-x-2.5 min-w-0">
            {toast.type === 'warning' ? (
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
            ) : toast.type === 'error' ? (
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            ) : toast.type === 'success' ? (
              <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <Info className="w-4 h-4 text-blue-400 shrink-0" />
            )}
            <span className="font-medium text-slate-100 truncate">{toast.message}</span>
          </div>
          <button 
            type="button"
            onClick={() => removeToast && removeToast(toast.id)}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors shrink-0 cursor-pointer"
            title="Dismiss"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
    </div>
  );
}

/* 2. GLOBAL MODAL CONTAINER */
export function GlobalModal() {
  const { activeModal, modalData, closeModal } = useInvestigation();

  if (!activeModal) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4 animate-fade-in">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden animate-slide-up border border-slate-200">
        <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <h2 className="text-lg font-bold text-slate-800 tracking-tight">{modalData?.title || 'Dialog'}</h2>
          <button 
            onClick={closeModal}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6 text-sm text-slate-600">
          {modalData?.content || 'Modal content'}
        </div>
        {modalData?.actions && (
          <div className="p-4 bg-slate-50 border-t border-slate-100 flex justify-end space-x-3">
            {modalData.actions}
          </div>
        )}
      </div>
    </div>
  );
}

/* 3. COMBINED ROOT OVERLAYS EXPORT */
export function Overlays() {
  return (
    <>
      <GlobalModal />
      <ToastContainer />
    </>
  );
}

export default Overlays;
