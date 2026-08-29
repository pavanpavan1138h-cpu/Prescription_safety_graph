import { useState, useEffect } from 'react';
import { prescriptionApi, SubgraphResponse } from '../api/client';

export const useGraphData = (analysisId: string | undefined, selectedPairId: string | null) => {
  const [graphType, setGraphType] = useState<'overview' | 'pair' | 'provenance'>('overview');
  const [subgraph, setSubgraph] = useState<SubgraphResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [sideEffectLimit, setSideEffectLimit] = useState<number>(5);

  useEffect(() => {
    if (!analysisId) {
      setSubgraph(null);
      return;
    }

    const loadGraph = async () => {
      setLoading(true);
      try {
        let res: SubgraphResponse;
        if (graphType === 'overview') {
          res = await prescriptionApi.getPrescriptionGraph(analysisId, sideEffectLimit);
        } else if (graphType === 'pair' && selectedPairId) {
          res = await prescriptionApi.getPairEvidenceGraph(analysisId, selectedPairId, 25);
        } else if (graphType === 'provenance' && selectedPairId) {
          res = await prescriptionApi.getProvenanceGraph(analysisId, selectedPairId);
        } else {
          // Fallback to overview
          res = await prescriptionApi.getPrescriptionGraph(analysisId, sideEffectLimit);
        }
        setSubgraph(res);
      } catch (err) {
        console.error('Failed to load subgraph:', err);
        setSubgraph(null);
      } finally {
        setLoading(false);
      }
    };

    loadGraph();
  }, [analysisId, graphType, selectedPairId, sideEffectLimit]);

  return {
    graphType,
    setGraphType,
    subgraph,
    loading,
    sideEffectLimit,
    setSideEffectLimit
  };
};
