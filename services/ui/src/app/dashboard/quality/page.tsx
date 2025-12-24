'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import ChartCard from '@/components/ChartCard';
import Loading from '@/components/Loading';
import { CheckCircle, XCircle } from 'lucide-react';

interface QualityCheck {
  checkpoint_name: string;
  run_time: string;
  success: boolean;
  expectations_passed: number;
  expectations_failed: number;
  failed_expectations: string[];
}

export default function QualityPage() {
  const [quality, setQuality] = useState<QualityCheck | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get<QualityCheck>('/quality/latest');
        setQuality(response.data);
      } catch (error) {
        console.error('Failed to fetch quality data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  if (loading || !quality) {
    return <Loading />;
  }

  return (
    <div className="p-8 bg-gradient-to-br from-gray-50 via-green-50 to-emerald-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
          Data Quality
        </h1>
        <p className="mt-2 text-gray-600 text-lg">Latest data quality check results</p>
      </div>
      <div className="space-y-6">
        <ChartCard title="Quality Check Summary">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Checkpoint</p>
                <p className="text-lg font-semibold">{quality.checkpoint_name}</p>
              </div>
              <div className="flex items-center space-x-2">
                {quality.success ? (
                  <>
                    <CheckCircle className="h-6 w-6 text-green-600" />
                    <span className="text-green-600 font-semibold">Passed</span>
                  </>
                ) : (
                  <>
                    <XCircle className="h-6 w-6 text-red-600" />
                    <span className="text-red-600 font-semibold">Failed</span>
                  </>
                )}
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Run Time</p>
                <p className="text-lg font-semibold">
                  {new Date(quality.run_time).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Expectations Passed</p>
                <p className="text-lg font-semibold text-green-600">
                  {quality.expectations_passed}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Expectations Failed</p>
                <p className="text-lg font-semibold text-red-600">
                  {quality.expectations_failed}
                </p>
              </div>
            </div>
            {quality.failed_expectations.length > 0 && (
              <div>
                <p className="mb-2 text-sm font-semibold text-red-600">Failed Expectations:</p>
                <ul className="list-disc list-inside space-y-1">
                  {quality.failed_expectations.map((exp, index) => (
                    <li key={index} className="text-sm text-gray-700">{exp}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </ChartCard>
      </div>
    </div>
  );
}

