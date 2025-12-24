import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}

export function formatPercent(value: number | string): string {
  // Handle Decimal type from backend (convert to float if needed)
  let numValue: number;
  if (typeof value === 'string') {
    numValue = parseFloat(value);
  } else if (typeof value === 'object' && value !== null) {
    numValue = parseFloat(value.toString());
  } else {
    numValue = value;
  }
  
  // Handle NaN or invalid values
  if (isNaN(numValue)) {
    return '0.00%';
  }
  
  // If value is already a percentage (0-1), multiply by 100, otherwise use as-is
  const percentage = numValue > 1 ? numValue : numValue * 100;
  return `${percentage.toFixed(2)}%`;
}

