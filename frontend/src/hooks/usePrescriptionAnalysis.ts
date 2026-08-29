import { useState } from 'react';
import { prescriptionApi, AdvancedPrescriptionAnalysisResponse } from '../api/client';
import { PairDetailResponse } from '../types/api';

export const usePrescriptionAnalysis = () => {
  const [medications, setMedications] = useState<string[]>([]);
  const [analysisData, setAnalysisData] = useState<AdvancedPrescriptionAnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  
  // Drilldown states
  const [selectedPairId, setSelectedPairId] = useState<string | null>(null);
  const [selectedPairDetail, setSelectedPairDetail] = useState<PairDetailResponse | null>(null);
  const [loadingPairDetail, setLoadingPairDetail] = useState<boolean>(false);

  const addMedication = (med: string) => {
    if (!med.trim()) return;
    const clean = med.trim();
    if (!medications.includes(clean)) {
      setMedications([...medications, clean]);
    }
  };

  const removeMedication = (index: number) => {
    setMedications(medications.filter((_, i) => i !== index));
  };

  const runAnalysis = async () => {
    if (medications.length === 0) {
      setErrorMsg('Please add at least one medication to analyze.');
      return;
    }
    
    setLoading(true);
    setErrorMsg(null);
    try {
      const data = await prescriptionApi.analyzePrescriptionAdvanced(medications);
      setAnalysisData(data);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to analyze prescription.');
      setAnalysisData(null);
    } finally {
      setLoading(false);
    }
  };

  const selectPair = async (pairId: string) => {
    if (!analysisData) return;
    const analysisId = analysisData.prescription_report.metadata.analysis_id;
    setSelectedPairId(pairId);
    setLoadingPairDetail(true);
    try {
      const detail = await prescriptionApi.getPairDetail(analysisId, pairId);
      setSelectedPairDetail(detail);
    } catch (err: any) {
      console.error('Failed to fetch pair detail:', err);
    } finally {
      setLoadingPairDetail(false);
    }
  };

  const closePairDetail = () => {
    setSelectedPairId(null);
    setSelectedPairDetail(null);
  };

  const resetAnalysis = () => {
    setAnalysisData(null);
    setMedications([]);
    closePairDetail();
    setErrorMsg(null);
  };

  return {
    medications,
    addMedication,
    removeMedication,
    analysisData,
    loading,
    errorMsg,
    runAnalysis,
    resetAnalysis,
    selectedPairId,
    selectedPairDetail,
    loadingPairDetail,
    selectPair,
    closePairDetail
  };
};
