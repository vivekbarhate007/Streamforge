'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  LayoutDashboard, 
  Activity, 
  DollarSign, 
  TrendingUp, 
  CheckCircle, 
  Heart,
  LogOut
} from 'lucide-react';
import { removeToken } from '@/lib/auth';

const navItems = [
  { href: '/dashboard/overview', label: 'Overview', icon: LayoutDashboard },
  { href: '/dashboard/events', label: 'Events', icon: Activity },
  { href: '/dashboard/revenue', label: 'Revenue', icon: DollarSign },
  { href: '/dashboard/top-products', label: 'Top Products', icon: TrendingUp },
  { href: '/dashboard/quality', label: 'Data Quality', icon: CheckCircle },
  { href: '/dashboard/health', label: 'Pipeline Health', icon: Heart },
];

export default function Nav() {
  const pathname = usePathname();

  const handleLogout = () => {
    removeToken();
    window.location.href = '/login';
  };

  return (
    <div className="flex h-screen w-64 flex-col bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 text-white shadow-2xl">
      <div className="flex h-16 items-center justify-center border-b border-gray-700 bg-gradient-to-r from-blue-600 to-purple-600">
        <h1 className="text-xl font-bold text-white">StreamForge</h1>
      </div>
      <nav className="flex-1 space-y-2 p-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center space-x-3 rounded-xl px-4 py-3 transition-all duration-200',
                isActive
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg transform scale-105'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white hover:translate-x-1'
              )}
            >
              <Icon className="h-5 w-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-gray-700 p-4">
        <button
          onClick={handleLogout}
          className="flex w-full items-center space-x-3 rounded-xl px-4 py-3 text-gray-300 transition-all duration-200 hover:bg-red-600 hover:text-white hover:shadow-lg"
        >
          <LogOut className="h-5 w-5" />
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </div>
  );
}

