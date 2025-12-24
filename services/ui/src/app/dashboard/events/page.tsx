'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import ChartCard from '@/components/ChartCard';
import Loading from '@/components/Loading';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface TimeSeriesPoint {
  timestamp: string;
  value: number;
}

export default function EventsPage() {
  const [data, setData] = useState<TimeSeriesPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [isLive, setIsLive] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get<{ data: TimeSeriesPoint[] }>('/metrics/events_timeseries?hours=24');
        const formatted = response.data.data.map((point) => ({
          timestamp: new Date(point.timestamp).toLocaleTimeString(),
          value: point.value,
        }));
        setData(formatted);
      } catch (error) {
        console.error('Failed to fetch events data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="p-8 bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 min-h-screen">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Events Analytics
          </h1>
          <p className="mt-2 text-gray-600 text-lg">Real-time event stream metrics</p>
        </div>
        {isLive && (
          <div className="flex items-center space-x-2 rounded-full bg-gradient-to-r from-red-500 to-pink-500 px-6 py-3 shadow-lg animate-pulse">
            <div className="h-3 w-3 rounded-full bg-white animate-ping"></div>
            <span className="text-sm font-bold text-white">LIVE</span>
          </div>
        )}
      </div>
      <ChartCard title="Events per Hour (Last 24 Hours)">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#3b82f6"
              strokeWidth={2}
              name="Events"
            />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}

