import { useState, useEffect, useCallback } from 'react';
import { Measurement, VirtualSemaforo, LatestMeasurementResponse } from '../types';
import { ApiService } from '../services/api';

export interface MeasurementError {
  title: string;
  message: string;
}

function getErrorInfo(error: unknown): MeasurementError {
  if (error instanceof TypeError && /failed to fetch|fetch failed|networkerror/i.test(error.message)) {
    return {
      title: 'Error de conexión',
      message: 'No se pudo contactar al servidor de Narval. Verifica que el backend esté iniciado y vuelve a intentarlo.',
    };
  }

  if (error instanceof Error) {
    const statusMatch = error.message.match(/Error (\d{3}):\s*(.*)/);
    if (statusMatch) {
      const status = Number(statusMatch[1]);
      const titles: Record<number, string> = {
        400: 'Solicitud inválida',
        401: 'Autenticación requerida',
        403: 'Acceso denegado',
        404: 'Recurso no encontrado',
        500: 'Error interno del servidor',
        502: 'Servidor no disponible',
        503: 'Servicio temporalmente no disponible',
      };
      return {
        title: titles[status] || `Error HTTP ${status}`,
        message: statusMatch[2] || 'No se pudo completar la solicitud.',
      };
    }

    return { title: 'Error al cargar mediciones', message: error.message };
  }

  return {
    title: 'Error inesperado',
    message: 'No se pudieron cargar las mediciones. Intenta nuevamente.',
  };
}

export function useMeasurements(pollingIntervalMs = 15000) {
  const [latestData, setLatestData] = useState<LatestMeasurementResponse | null>(null);
  const [history, setHistory] = useState<Measurement[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<MeasurementError | null>(null);

  const fetchLatest = useCallback(async () => {
    try {
      const data = await ApiService.getLatestMeasurement();
      setLatestData(data);
      setError(null);
    } catch (err: unknown) {
      setError(getErrorInfo(err));
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
