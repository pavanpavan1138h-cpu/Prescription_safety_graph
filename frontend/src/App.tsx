import React, { useState, useEffect } from 'react';
import { AppShell } from './components/layout/AppShell';
import { HomePage } from './pages/HomePage';
import { AboutPage } from './pages/AboutPage';
import { PrescriptionSafetyPage } from './pages/PrescriptionSafetyPage';
import { prescriptionApi } from './api/client';
import { SystemInfoResponse } from './types/api';

function App() {
  const [currentPage, setCurrentPage] = useState<'home' | 'dashboard' | 'about'>('home');
  const [isLightTheme, setIsLightTheme] = useState(false);
  const [systemInfo, setSystemInfo] = useState<SystemInfoResponse | null>(null);

  useEffect(() => {
    prescriptionApi.getSystemInfo()
      .then(setSystemInfo)
      .catch(console.error);
  }, []);

  const handleThemeToggle = () => {
    setIsLightTheme((prev) => {
      const newVal = !prev;
      if (newVal) {
        document.documentElement.classList.add('light-theme');
      } else {
        document.documentElement.classList.remove('light-theme');
      }
      return newVal;
    });
  };

  return (
    <AppShell
      systemInfo={systemInfo}
      currentPage={currentPage}
      onPageChange={setCurrentPage}
      isLightTheme={isLightTheme}
      onThemeToggle={handleThemeToggle}
    >
      <div style={{ display: currentPage === 'home' ? 'block' : 'none' }}>
        <HomePage onStartAnalysis={() => setCurrentPage('dashboard')} systemInfo={systemInfo} />
      </div>
      
      <div style={{ display: currentPage === 'dashboard' ? 'flex' : 'none', flexDirection: 'column', flex: 1, minHeight: 0 }}>
        <PrescriptionSafetyPage systemInfo={systemInfo} />
      </div>
      
      <div style={{ display: currentPage === 'about' ? 'block' : 'none' }}>
        <AboutPage />
      </div>
    </AppShell>
  );
}

export default App;
