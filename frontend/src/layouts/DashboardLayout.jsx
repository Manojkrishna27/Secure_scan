import { useState } from "react";
import { Outlet } from "react-router-dom";

import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";

export function DashboardLayout() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar
        showMenuButton
        onMenuToggle={() => setMobileNavOpen((o) => !o)}
      />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          mobileOpen={mobileNavOpen}
          onClose={() => setMobileNavOpen(false)}
        />
        <main className="flex-1 overflow-auto">
          <div className="container max-w-7xl py-6 md:py-8">
            <Outlet />
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
}
