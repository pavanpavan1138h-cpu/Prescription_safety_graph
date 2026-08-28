import React, { useEffect, useRef, useState } from 'react';
import cytoscape, { Core } from 'cytoscape';
import { SubgraphResponse, GraphNode, GraphEdge } from '../api/client';
import {
  Maximize2,
  Minimize2,
  RotateCcw,
  ZoomIn,
  ZoomOut,
  Info,
  GitFork,
  Layers,
  Database,
  Search
} from 'lucide-react';

interface InteractiveGraphProps {
  subgraph: SubgraphResponse;
  onSelectNode?: (node: GraphNode) => void;
  onSelectEdge?: (edge: GraphEdge) => void;
  highlightPairId?: string;
  height?: string;
}

export const InteractiveGraph: React.FC<InteractiveGraphProps> = ({
  subgraph,
  onSelectNode,
  onSelectEdge,
  highlightPairId,
  height = '540px'
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [selectedElement, setSelectedElement] = useState<any>(null);
  const [layoutMode, setLayoutMode] = useState<'cose' | 'circle' | 'breadthfirst' | 'concentric'>('cose');
  const [filterType, setFilterType] = useState<string>('ALL');

  useEffect(() => {
    if (!containerRef.current) return;

    // Convert SubgraphResponse to Cytoscape elements
    const elements: any[] = [];

    // Filter nodes if requested
    const filteredNodes = subgraph.nodes.filter(n => {
      if (filterType === 'DRUG') return n.node_type === 'Drug';
      if (filterType === 'COMBINATION') return n.node_type === 'DrugPair';
      if (filterType === 'SIDE_EFFECT') return n.node_type === 'SideEffect';
      if (filterType === 'RXNORM') return n.node_type === 'RxNormConcept';
      return true;
    });

    const activeNodeIds = new Set(filteredNodes.map(n => n.id));

    filteredNodes.forEach(node => {
      let bg = '#3b82f6';
      let shape = 'ellipse';
      let size = 36;
      let borderCol = '#60a5fa';

      if (node.node_type === 'Drug') {
        bg = '#2563eb';
        borderCol = '#93c5fd';
        size = 46;
      } else if (node.node_type === 'DrugPair') {
        bg = '#7c3aed';
        shape = 'diamond';
        borderCol = '#c4b5fd';
        size = 40;
      } else if (node.node_type === 'SideEffect') {
        bg = '#ef4444';
        size = 28;
        borderCol = '#fca5a5';
      } else if (node.node_type === 'RxNormConcept') {
        bg = '#059669';
        shape = 'round-rectangle';
        size = 34;
        borderCol = '#6ee7b7';
      } else if (node.node_type === 'InferenceDecision') {
        bg = '#dc2626';
        shape = 'star';
        size = 48;
        borderCol = '#fecaca';
      } else if (node.node_type === 'ReasoningRule') {
        bg = '#d97706';
        shape = 'hexagon';
        size = 38;
      } else if (node.node_type === 'ProvenanceSource') {
        bg = '#475569';
        shape = 'rectangle';
        size = 34;
      }

      elements.push({
        group: 'nodes',
        data: {
          id: node.id,
          label: node.label,
          node_type: node.node_type,
          display_category: node.display_category,
          properties: node.properties,
          is_focal: node.is_focal,
          bg,
          shape,
          size,
          borderCol
        }
      });
    });

    // Add valid edges
    subgraph.edges.forEach(edge => {
      if (activeNodeIds.has(edge.source) && activeNodeIds.has(edge.target)) {
        let lineCol = '#64748b';
        let arrowCol = '#94a3b8';
        let width = 2;

        if (edge.relationship_type === 'INTERACTS_WITH') {
          lineCol = '#ef4444';
          arrowCol = '#ef4444';
          width = 3;
        } else if (edge.relationship_type === 'MEMBER_OF_PAIR') {
          lineCol = '#8b5cf6';
          arrowCol = '#8b5cf6';
          width = 2;
        } else if (edge.relationship_type === 'ASSOCIATED_WITH') {
          lineCol = '#f87171';
          arrowCol = '#f87171';
          width = 1.5;
        } else if (edge.relationship_type === 'HAS_RXNORM_CONCEPT') {
          lineCol = '#10b981';
          arrowCol = '#10b981';
          width = 1.5;
        }

        elements.push({
          group: 'edges',
          data: {
            id: edge.id,
            source: edge.source,
            target: edge.target,
            label: edge.label,
            relationship_type: edge.relationship_type,
            source_dataset: edge.source_dataset,
            properties: edge.properties,
            lineCol,
            arrowCol,
            width
          }
        });
      }
    });

    // Initialize Cytoscape
    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': 'data(bg)',
            'label': 'data(label)',
            'color': '#f8fafc',
            'font-family': 'Inter, sans-serif',
            'font-size': '10px',
            'font-weight': '600',
            'text-valign': 'bottom',
            'text-margin-y': 5,
            'text-outline-color': '#0b0f17',
            'text-outline-width': 2,
            'shape': 'data(shape)' as any,
            'width': 'data(size)',
            'height': 'data(size)',
            'border-width': 2,
            'border-color': 'data(borderCol)'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 'data(width)',
            'line-color': 'data(lineCol)',
            'target-arrow-color': 'data(arrowCol)',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'opacity': 0.85
          }
        },
        {
          selector: ':selected',
          style: {
            'border-width': 4,
            'border-color': '#fbbf24',
            'line-color': '#fbbf24',
            'target-arrow-color': '#fbbf24'
          }
        }
      ],
      layout: {
        name: layoutMode,
        animate: true,
        animationDuration: 500,
        padding: 40
      }
    });

    cy.on('tap', 'node', evt => {
      const node = evt.target;
      setSelectedElement({ type: 'node', data: node.data() });
      if (onSelectNode) {
        onSelectNode(node.data());
      }
    });

    cy.on('tap', 'edge', evt => {
      const edge = evt.target;
      setSelectedElement({ type: 'edge', data: edge.data() });
      if (onSelectEdge) {
        onSelectEdge(edge.data());
      }
    });

    cy.on('tap', evt => {
      if (evt.target === cy) {
        setSelectedElement(null);
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [subgraph, layoutMode, filterType]);

  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.25);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() * 0.8);
  const handleFit = () => cyRef.current?.fit();
  const handleReset = () => {
    cyRef.current?.reset();
    cyRef.current?.center();
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: selectedElement ? '1fr 320px' : '1fr', gap: '16px', position: 'relative' }}>
      <div className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', height, position: 'relative' }}>
        {/* Controls Toolbar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', zIndex: 10 }}>
          <div style={{ display: 'flex', gap: '6px' }}>
            {['ALL', 'DRUG', 'COMBINATION', 'SIDE_EFFECT', 'RXNORM'].map(t => (
              <button
                key={t}
                onClick={() => setFilterType(t)}
                style={{
                  padding: '4px 10px',
                  borderRadius: '4px',
                  border: '1px solid var(--border-color)',
                  background: filterType === t ? '#3b82f6' : 'rgba(255,255,255,0.03)',
                  color: '#fff',
                  fontSize: '0.7rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                {t}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <select
              value={layoutMode}
              onChange={(e: any) => setLayoutMode(e.target.value)}
              style={{
                background: '#1e293b',
                border: '1px solid var(--border-color)',
                color: '#fff',
                borderRadius: '4px',
                padding: '4px 8px',
                fontSize: '0.75rem'
              }}
            >
              <option value="cose">Force-Directed (Cose)</option>
              <option value="circle">Circular</option>
              <option value="breadthfirst">Hierarchical</option>
              <option value="concentric">Concentric</option>
            </select>

            <button onClick={handleZoomIn} title="Zoom In" style={{ background: '#1e293b', border: '1px solid var(--border-color)', color: '#fff', borderRadius: '4px', padding: '4px 8px', cursor: 'pointer' }}><ZoomIn size={14} /></button>
            <button onClick={handleZoomOut} title="Zoom Out" style={{ background: '#1e293b', border: '1px solid var(--border-color)', color: '#fff', borderRadius: '4px', padding: '4px 8px', cursor: 'pointer' }}><ZoomOut size={14} /></button>
            <button onClick={handleFit} title="Fit to Screen" style={{ background: '#1e293b', border: '1px solid var(--border-color)', color: '#fff', borderRadius: '4px', padding: '4px 8px', cursor: 'pointer' }}><Maximize2 size={14} /></button>
            <button onClick={handleReset} title="Reset" style={{ background: '#1e293b', border: '1px solid var(--border-color)', color: '#fff', borderRadius: '4px', padding: '4px 8px', cursor: 'pointer' }}><RotateCcw size={14} /></button>
          </div>
        </div>

        {/* Graph Canvas */}
        <div ref={containerRef} style={{ flex: 1, width: '100%', borderRadius: '8px', background: 'rgba(0,0,0,0.3)' }} />

        {/* Truncation & Graph Stats Footer */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
          <span>Showing <b>{subgraph.metadata.node_count}</b> nodes, <b>{subgraph.metadata.edge_count}</b> edges</span>
          {subgraph.metadata.truncated && (
            <span style={{ color: '#fcd34d' }}>
              ℹ Truncated: +{subgraph.metadata.hidden_node_count} additional adverse event nodes hidden for performance
            </span>
          )}
        </div>
      </div>

      {/* Inspector Sidebar */}
      {selectedElement && (
        <div className="glass-panel animate-fade-in" style={{ padding: '16px', height, overflowY: 'auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px', marginBottom: '12px' }}>
            <span className="badge badge-limited">{selectedElement.type === 'node' ? selectedElement.data.display_category : 'Knowledge Graph Edge'}</span>
            <button onClick={() => setSelectedElement(null)} style={{ background: 'none', border: 'none', color: 'var(--text-dim)', cursor: 'pointer' }}>✕</button>
          </div>

          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '6px' }}>{selectedElement.data.label}</h3>
          <p className="mono" style={{ fontSize: '0.75rem', color: '#93c5fd', marginBottom: '14px' }}>ID: {selectedElement.data.id}</p>

          {selectedElement.type === 'node' ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.8rem' }}>
              <div><b>Type:</b> {selectedElement.data.node_type}</div>
              {selectedElement.data.properties?.rxcui && (
                <div><b>RxCUI:</b> {selectedElement.data.properties.rxcui}</div>
              )}
              {selectedElement.data.properties?.total_adverse_events !== undefined && (
                <div><b>Total Observed Events:</b> {selectedElement.data.properties.total_adverse_events}</div>
              )}
              {selectedElement.data.properties?.drugbank_ids?.length > 0 && (
                <div><b>DrugBank IDs:</b> {selectedElement.data.properties.drugbank_ids.join(', ')}</div>
              )}
              {selectedElement.data.properties?.twosides_cids?.length > 0 && (
                <div><b>TWOSIDES CIDs:</b> {selectedElement.data.properties.twosides_cids.join(', ')}</div>
              )}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.8rem' }}>
              <div><b>Relationship:</b> {selectedElement.data.relationship_type}</div>
              <div><b>Source Dataset:</b> {selectedElement.data.source_dataset}</div>
              <div><b>Direction:</b> {selectedElement.data.source} → {selectedElement.data.target}</div>
              {selectedElement.data.properties?.interaction_description && (
                <div style={{ marginTop: '8px', background: 'rgba(0,0,0,0.3)', padding: '8px', borderRadius: '6px' }}>
                  <b>Description:</b>
                  <p style={{ marginTop: '4px', fontSize: '0.75rem', color: '#e2e8f0' }}>{selectedElement.data.properties.interaction_description}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
