'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import KPIStat from '@/components/KPIStat';
import Loading from '@/components/Loading';
import { Users, Activity, DollarSign, TrendingUp } from 'lucide-react';

interface OverviewMetrics {
  total_users: number;
  total_events: number;
  total_revenue: number;
  conversion_rate: number | string;
  events_last_hour: number;
  revenue_today: number;
}

export default function OverviewPage() {
  const [metrics, setMetrics] = useState<OverviewMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await api.get<OverviewMetrics>('/metrics/overview');
        setMetrics(response.data);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading || !metrics) {
    return <Loading />;
  }

  return (
    <div className="p-8 bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Overview Dashboard
        </h1>
        <p className="mt-2 text-gray-600 text-lg">Key performance indicators at a glance</p>
      </div>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        <KPIStat
          title="Total Users"
          value={metrics.total_users}
          icon={Users}
          format="number"
          color="blue"
        />
        <KPIStat
          title="Total Events"
          value={metrics.total_events}
          icon={Activity}
          format="number"
          color="purple"
        />
        <KPIStat
          title="Total Revenue"
          value={metrics.total_revenue}
          icon={DollarSign}
          format="currency"
          color="green"
        />
        <KPIStat
          title="Conversion Rate"
          value={
            typeof metrics.conversion_rate === 'string' 
              ? parseFloat(metrics.conversion_rate) 
              : typeof metrics.conversion_rate === 'number'
              ? metrics.conversion_rate
              : 0
          }
          icon={TrendingUp}
          format="percent"
          color="orange"
        />
        <KPIStat
          title="Events (Last Hour)"
          value={metrics.events_last_hour}
          icon={Activity}
          format="number"
          color="pink"
        />
        <KPIStat
          title="Revenue Today"
          value={metrics.revenue_today}
          icon={DollarSign}
          format="currency"
          color="indigo"
        />
      </div>
    </div>
  );
}

