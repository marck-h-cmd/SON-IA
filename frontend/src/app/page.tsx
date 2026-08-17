'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    router.push('/dashboard-interno');
  }, [router]);

  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">FINIA Dashboard</h1>
        <p className="text-gray-600">Redirigiendo al dashboard...</p>
      </div>
    </div>
  );
}
