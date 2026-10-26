import { useState, useEffect, useCallback } from 'react';
import { Measurement, VirtualSemaforo, LatestMeasurementResponse } from '../types';
import { ApiService } from '../services/api';

export function useMeasurements(pollingIntervalMs = 15000) {
  const [latestData, setLatestData] = useState<LatestMeasurementResponse | null>(null);
  const [history, setHistory] = useState<Measurement[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLatest = useCallback(async () => {
    try {
      const data = await ApiService.getLatestMeasurement();
      setLatestData(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Error al conectar con el backend de Narval');
    }
  }, []);

  const fetchHistory = useCallback(async (limit = 50, offset = 0) => {
    try {
      const res = await ApiService.getMeasurements(limit, offset);
      setHistory(res.items);
      setTotalCount(res.total);
    } catch (err: any) {
      console.error('Error fetching history:', err);
    }
  }, []);

  const refreshAll = useCallback(async () => {
    setLoading(true);
    await Promise.all([fetchLatest(), fetchHistory(50, 0)]);
    setLoading(false);
  }, [fetchLatest, fetchHistory]);

  useEffect(() => {
    refreshAll();
    const timer = setInterval(() => {
      fetchLatest();
      fetchHistory(50, 0);
    }, pollingIntervalMs);
    return () => clearInterval(timer);
  }, [refreshAll, fetchLatest, fetchHistory, pollingIntervalMs]);

  return {
    latest: latestData?.measurement || null,
    semaforo: latestData?.semaforo || null,
    aiAnalysis: latestData?.ai_analysis || null,
    history,
    totalCount,
    loading,
    error,
    refreshAll,
  };
}
