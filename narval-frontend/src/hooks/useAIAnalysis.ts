import { useState } from 'react';
import type { AIAnalysis } from '../types';
import { ApiService } from '../services/api';

export interface SensorErrorDetail {
  error_code?: string;
  title?: string;
  message?: string;
  sensor_errors?: string[];
  action_required?: string;
}

export function useAIAnalysis() {
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [structuredError, setStructuredError] = useState<SensorErrorDetail | null>(null);

  const requestAnalysis = async (measurementId?: number, count = 5) => {
    setLoading(true);
    setError(null);
    setStructuredError(null);
    try {
      const result = await ApiService.requestAIAnalysis(measurementId, count);
      setAnalysis(result);
    } catch (err: any) {
      if (err.structuredDetail && typeof err.structuredDetail === 'object') {
        setStructuredError(err.structuredDetail);
        setError(err.structuredDetail.message || 'Sensores no disponibles para análisis.');
      } else {
        setError(err.message || 'Error al solicitar análisis de IA a Gemini');
      }
    } finally {
      setLoading(false);
    }
  };

  return { analysis, loading, error, structuredError, requestAnalysis };
}
