import { LucideIcon } from 'lucide-react';
import { formatCurrency, formatNumber, formatPercent } from '@/lib/utils';

interface KPIStatProps {
  title: string;
  value: number | string;
  icon: LucideIcon;
  format?: 'currency' | 'number' | 'percent' | 'default';
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: 'blue' | 'green' | 'purple' | 'orange' | 'pink' | 'indigo';
}

const colorSchemes = {
  blue: {
    bg: 'bg-gradient-to-br from-blue-50 to-blue-100',
    iconBg: 'bg-blue-500',
    iconColor: 'text-white',
    border: 'border-blue-200',
    text: 'text-blue-900',
  },
  green: {
    bg: 'bg-gradient-to-br from-green-50 to-emerald-100',
    iconBg: 'bg-green-500',
    iconColor: 'text-white',
    border: 'border-green-200',
    text: 'text-green-900',
  },
  purple: {
    bg: 'bg-gradient-to-br from-purple-50 to-purple-100',
    iconBg: 'bg-purple-500',
    iconColor: 'text-white',
    border: 'border-purple-200',
    text: 'text-purple-900',
  },
  orange: {
    bg: 'bg-gradient-to-br from-orange-50 to-amber-100',
    iconBg: 'bg-orange-500',
    iconColor: 'text-white',
    border: 'border-orange-200',
    text: 'text-orange-900',
  },
  pink: {
    bg: 'bg-gradient-to-br from-pink-50 to-rose-100',
    iconBg: 'bg-pink-500',
    iconColor: 'text-white',
    border: 'border-pink-200',
    text: 'text-pink-900',
  },
  indigo: {
    bg: 'bg-gradient-to-br from-indigo-50 to-indigo-100',
    iconBg: 'bg-indigo-500',
    iconColor: 'text-white',
    border: 'border-indigo-200',
    text: 'text-indigo-900',
  },
};

export default function KPIStat({ 
  title, 
  value, 
  icon: Icon, 
  format = 'default', 
  trend,
  color = 'blue'
}: KPIStatProps) {
  const formatValue = () => {
    if (typeof value === 'string') return value;
    // Handle Decimal type from backend
    let numValue: number;
    if (typeof value === 'object' && value !== null) {
      numValue = parseFloat(value.toString());
    } else {
      numValue = value;
    }
    
    // Handle NaN or invalid values
    if (isNaN(numValue)) {
      return format === 'currency' ? '$0.00' : format === 'percent' ? '0.00%' : '0';
    }
    
    switch (format) {
      case 'currency':
        return formatCurrency(numValue);
      case 'number':
        return formatNumber(numValue);
      case 'percent':
        return formatPercent(numValue);
      default:
        return numValue.toString();
    }
  };

  const colors = colorSchemes[color];

  return (
    <div className={`rounded-xl border-2 ${colors.border} ${colors.bg} p-6 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0 overflow-hidden">
          <p className={`text-sm font-semibold ${colors.text} opacity-80 mb-2 truncate`}>{title}</p>
          <p className={`text-2xl sm:text-3xl md:text-4xl font-bold ${colors.text} break-all overflow-wrap-anywhere`} style={{ lineHeight: '1.2', maxWidth: '100%' }}>
            {formatValue()}
          </p>
          {trend && (
            <p className={`mt-2 text-sm font-medium ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {trend.isPositive ? '↑' : '↓'} {trend.isPositive ? '+' : ''}{trend.value}%
            </p>
          )}
        </div>
        <div className={`rounded-xl ${colors.iconBg} p-3 sm:p-4 shadow-md flex-shrink-0`}>
          <Icon className={`h-6 w-6 sm:h-7 sm:w-7 ${colors.iconColor}`} />
        </div>
      </div>
    </div>
  );
}

