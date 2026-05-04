'use client';

import { Sidebar, MobileHeader } from './sidebar';
import { Topbar } from './topbar';
import { useUIStore } from '@/lib/store';

export function MainLayout({ children }: { children: React.ReactNode }) {
  const { sidebarOpen } = useUIStore();

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <div
        className={`flex flex-col transition-all duration-200 ${
          sidebarOpen ? 'lg:pl-64' : 'lg:pl-64'
        }`}
      >
        <Topbar />
        <MobileHeader />
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}