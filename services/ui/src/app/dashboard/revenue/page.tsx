'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import ChartCard from '@/components/ChartCard';
import Loading from '@/components/Loading';
import {
  BarChart,
  Bar,
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

export default function RevenuePage() {
  const [data, setData] = useState<TimeSeriesPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(365);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get<{ data: TimeSeriesPoint[] }>(`/metrics/revenue_timeseries?days=${days}`);
        const formatted = response.data.data.map((point) => ({
          date: new Date(point.timestamp).toLocaleDateString(),
          revenue: point.value,
        }));
        setData(formatted);
      } catch (error) {
        console.error('Failed to fetch revenue data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [days]);

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="p-8 bg-gradient-to-br from-gray-50 via-green-50 to-emerald-50 min-h-screen">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
            Revenue Analytics
          </h1>
          <p className="mt-2 text-gray-600 text-lg">Daily revenue trends</p>
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="rounded-xl border-2 border-green-300 bg-white px-6 py-3 font-semibold text-green-700 shadow-md hover:shadow-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
          <option value={365}>Last 365 days</option>
        </select>
      </div>
      <ChartCard title={`Daily Revenue (Last ${days} Days)`}>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
            <Legend />
            <Bar dataKey="revenue" fill="#10b981" name="Revenue ($)" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}

