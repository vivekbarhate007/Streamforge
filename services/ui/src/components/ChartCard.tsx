'use client';

import { ReactNode } from 'react';

interface ChartCardProps {
  title: string;
  children: ReactNode;
  action?: ReactNode;
  className?: string;
}

export default function ChartCard({ title, children, action, className }: ChartCardProps) {
  return (
    <div className={`rounded-xl border-2 border-gray-200 bg-gradient-to-br from-white to-gray-50 p-6 shadow-lg hover:shadow-xl transition-all duration-300 ${className || ''}`}>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          {title}
        </h3>
        {action && <div>{action}</div>}
      </div>
      <div>{children}</div>
    </div>
  );
}

