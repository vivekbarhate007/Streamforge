'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import ChartCard from '@/components/ChartCard';
import Loading from '@/components/Loading';
import DataTable from '@/components/DataTable';
import { formatNumber } from '@/lib/utils';
import { CheckCircle, XCircle, Clock } from 'lucide-react';

interface PipelineStatus {
  pipeline_name: string;
  last_run_ts: string | null;
  status: string | null;
  rows_processed: number | null;
  lag_seconds: number | null;
}

interface HealthStatus {
  pipelines: PipelineStatus[];
  table_counts: Record<string, number>;
  last_dbt_run: string | null;
  last_ge_run: string | null;
}

export default function HealthPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get<HealthStatus>('/health/pipelines');
        setHealth(response.data);
      } catch (error) {
        console.error('Failed to fetch health data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading || !health) {
    return <Loading />;
  }

  const getStatusIcon = (status: string | null) => {
    if (!status) return <Clock className="h-5 w-5 text-gray-400" />;
    if (status === 'running' || status === 'completed') {
      return <CheckCircle className="h-5 w-5 text-green-600" />;
    }
    return <XCircle className="h-5 w-5 text-red-600" />;
  };

  return (
    <div className="p-8 bg-gradient-to-br from-gray-50 via-blue-50 to-cyan-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
          Pipeline Health
        </h1>
        <p className="mt-2 text-gray-600 text-lg">Monitor pipeline status and data flow</p>
      </div>
      <div className="space-y-6">
        <ChartCard title="Pipeline Status">
          <DataTable
            data={health.pipelines}
            columns={[
              {
                header: 'Pipeline',
                accessor: 'pipeline_name',
              },
              {
                header: 'Status',
                accessor: (row) => (
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(row.status)}
                    <span className="capitalize">{row.status || 'Unknown'}</span>
                  </div>
                ),
              },
              {
                header: 'Last Run',
                accessor: (row) =>
                  row.last_run_ts
                    ? new Date(row.last_run_ts).toLocaleString()
                    : 'Never',
              },
              {
                header: 'Lag',
                accessor: (row) =>
                  row.lag_seconds !== null ? `${row.lag_seconds}s` : '-',
              },
            ]}
          />
        </ChartCard>
        <ChartCard title="Table Row Counts">
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {Object.entries(health.table_counts).map(([table, count]) => (
              <div key={table} className="rounded-lg border bg-gray-50 p-4">
                <p className="text-sm text-gray-600">{table}</p>
                <p className="mt-1 text-2xl font-bold">{formatNumber(count)}</p>
              </div>
            ))}
          </div>
        </ChartCard>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <ChartCard title="Last dbt Run">
            <p className="text-lg">
              {health.last_dbt_run
                ? new Date(health.last_dbt_run).toLocaleString()
                : 'Never'}
            </p>
          </ChartCard>
          <ChartCard title="Last Quality Check">
            <p className="text-lg">
              {health.last_ge_run
                ? new Date(health.last_ge_run).toLocaleString()
                : 'Never'}
            </p>
          </ChartCard>
        </div>
      </div>
    </div>
  );
}

