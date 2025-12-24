'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import ChartCard from '@/components/ChartCard';
import DataTable from '@/components/DataTable';
import Loading from '@/components/Loading';
import { formatCurrency, formatNumber } from '@/lib/utils';
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

interface TopProduct {
  product_id: string;
  product_name: string;
  revenue: number;
  quantity: number;
  orders: number;
}

export default function TopProductsPage() {
  const [products, setProducts] = useState<TopProduct[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get<{ products: TopProduct[] }>('/metrics/top_products?limit=10');
        setProducts(response.data.products);
      } catch (error) {
        console.error('Failed to fetch top products:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <Loading />;
  }

  const chartData = products.map((p) => ({
    name: p.product_name,
    revenue: p.revenue,
  }));

  return (
    <div className="p-8 bg-gradient-to-br from-gray-50 via-indigo-50 to-purple-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
          Top Products
        </h1>
        <p className="mt-2 text-gray-600 text-lg">Best performing products by revenue</p>
      </div>
      <div className="space-y-6">
        <ChartCard title="Revenue by Product">
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={150} />
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Legend />
              <Bar dataKey="revenue" fill="#3b82f6" name="Revenue" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Product Details">
          <DataTable
            data={products}
            columns={[
              { header: 'Product ID', accessor: 'product_id' },
              { header: 'Product Name', accessor: 'product_name' },
              {
                header: 'Revenue',
                accessor: 'revenue',
                format: (value) => formatCurrency(value),
              },
              {
                header: 'Quantity',
                accessor: 'quantity',
                format: (value) => formatNumber(value),
              },
              {
                header: 'Orders',
                accessor: 'orders',
                format: (value) => formatNumber(value),
              },
            ]}
          />
        </ChartCard>
      </div>
    </div>
  );
}

