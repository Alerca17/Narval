import { useState, useEffect, useCallback } from 'react';
import { DeviceStatus } from '../types';
import { ApiService } from '../services/api';

export function useDeviceStatus(pollingIntervalMs = 20000) {
  const [devices, setDevices] = useState<DeviceStatus[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchStatus = useCallback(async () => {
    try {
      const data = await ApiService.getDevicesStatus();
      setDevices(data);
    } catch (e) {
      console.error('Error fetching device status:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const timer = setInterval(fetchStatus, pollingIntervalMs);
    return () => clearInterval(timer);
  }, [fetchStatus, pollingIntervalMs]);

  return { devices, loading, refetch: fetchStatus };
}
