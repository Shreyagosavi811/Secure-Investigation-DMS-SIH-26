import React, { useMemo, useCallback } from 'react';
import { useInvestigation } from '../context/InvestigationContext';
import { PinnedDocumentCard } from '../components/common/PinnedDocumentCard';
import { EmptyState } from '../components/common/EmptyState';
import { ClipboardList, Network } from 'lucide-react';
import { ReactFlow, Background, Controls, MiniMap, useNodesState, useEdgesState, applyNodeChanges } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const nodeTypes = {
  documentCard: PinnedDocumentCard,
};

export function EvidenceBoard() {
  const { pinnedDocuments, unpinDocument, activeCaseId, navigate, updateBoardPosition } = useInvestigation();

  const casePins = useMemo(() => {
    return pinnedDocuments.filter(p => p.caseId === activeCaseId);
  }, [pinnedDocuments, activeCaseId]);

  // Define the central Hub Node
  const initialNodes = useMemo(() => {
    if (!activeCaseId) return [];
    
    const nodes = [
      {
        id: 'case-hub',
        type: 'default',
        position: { x: 500, y: 300 },
        data: { 
          label: (
            <div className="font-bold text-center text-slate-800 p-2">
              <Network className="w-6 h-6 mx-auto mb-2 text-blue-600" />
              CASE FILE
              <div className="text-xs font-mono text-slate-500 mt-1">{activeCaseId}</div>
            </div>
          )
        },
        style: {
          background: '#ffffff',
          border: '2px solid #3b82f6',
          borderRadius: '16px',
          width: 150,
          boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
        }
      }
    ];

    // Add Document Nodes
    casePins.forEach((pin, index) => {
      nodes.push({
        id: pin.documentId,
        type: 'documentCard',
        // Start them scattered around the center if no position saved
        position: { 
          x: pin.x || (500 + Math.cos(index) * 400), 
          y: pin.y || (300 + Math.sin(index) * 300) 
        },
        data: { pin, onUnpin: unpinDocument }
      });
    });

    return nodes;
  }, [casePins, activeCaseId, unpinDocument]);

  const initialEdges = useMemo(() => {
    return casePins.map(pin => ({
      id: `e-hub-${pin.documentId}`,
      source: 'case-hub',
      target: pin.documentId,
      animated: true,
      style: { stroke: '#94a3b8', strokeWidth: 2 }
    }));
  }, [casePins]);

  const [nodes, setNodes] = useNodesState(initialNodes);
  const [edges, setEdges] = useEdgesState(initialEdges);

  // Only reset nodes when the actual list of pinned documents changes (add/remove) or case changes
  const pinsSignature = useMemo(() => casePins.map(p => p.documentId).join(','), [casePins]);

  React.useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pinsSignature, activeCaseId]);

  // Handle Dragging
  const onNodesChange = useCallback(
    (changes) => {
      setNodes((nds) => applyNodeChanges(changes, nds));
      // Save position to context when dragging stops
      changes.forEach(change => {
        if (change.type === 'position' && change.dragging === false && change.id !== 'case-hub') {
          const node = nodes.find(n => n.id === change.id);
          if (node) {
            updateBoardPosition(change.id, node.position.x, node.position.y);
          }
        }
      });
    },
    [setNodes, nodes, updateBoardPosition]
  );

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col relative overflow-hidden bg-slate-50 border border-slate-200 rounded-xl">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-20 bg-white/90 backdrop-blur border-b border-slate-200 p-4 flex justify-between items-start shadow-sm">
        <div>
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <ClipboardList className="w-5 h-5 text-blue-600" />
            Evidence Board Map
          </h2>
          <div className="mt-1 flex items-center gap-3">
            <span className="badge-pill bg-slate-100 text-slate-600 font-mono">{activeCaseId || 'No Active Case'}</span>
            <span className="text-xs text-slate-500">Visualize cryptographic linkages between evidence files.</span>
          </div>
        </div>
      </div>

      {/* React Flow Canvas */}
      <div className="flex-1 w-full h-full relative z-10 pt-[72px]">
        {casePins.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center p-8 z-50 pointer-events-none">
            <div className="max-w-md w-full bg-white/80 backdrop-blur border border-slate-200 rounded-xl shadow-lg p-8 text-center pointer-events-auto">
              <EmptyState
                type="documents"
                title="No Evidence Pinned"
                message="Pin authorized documents from the Case Files or Document Viewer to visualize connections."
                actionButton={
                  <button 
                    onClick={() => navigate('dashboard')}
                    className="btn-primary mt-4"
                  >
                    Return to Case Files
                  </button>
                }
              />
            </div>
          </div>
        ) : (
          <ReactFlow 
            nodes={nodes} 
            edges={edges} 
            onNodesChange={onNodesChange}
            nodeTypes={nodeTypes}
            fitView
            minZoom={0.2}
            className="bg-slate-50"
          >
            <Background color="#cbd5e1" gap={24} size={2} />
            <Controls className="bg-white shadow-md border-slate-200 rounded-lg overflow-hidden" />
            <MiniMap 
              nodeColor={(n) => {
                if (n.type === 'documentCard') return '#3b82f6';
                return '#1e293b';
              }} 
              maskColor="rgba(248, 250, 252, 0.7)"
              className="border border-slate-200 rounded-lg shadow-sm" 
            />
          </ReactFlow>
        )}
      </div>
    </div>
  );
}
