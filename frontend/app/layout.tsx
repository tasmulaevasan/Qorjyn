import type { Metadata } from 'next';
import './globals.css';
import { LanguageProvider } from '@/context/LanguageContext';
import { ThemeProvider } from '@/context/ThemeContext';
import { Header } from '@/components/Header';
import { Navigation } from '@/components/Navigation';

export const metadata: Metadata = {
  title: 'QORJYN Mesh — B2B Коллективное Снабжение',
  description: 'Платформа коллективного закупа, ИИ-прогнозирования остатков и предотвращения дефицита для малого бизнеса Алматы',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru" className="dark">
      <body className="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 min-h-screen font-sans antialiased flex flex-col transition-colors duration-200">
        <ThemeProvider>
          <LanguageProvider>
            <Header />
            <Navigation />
            <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
              {children}
            </main>
            <footer className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 py-6 text-center text-xs text-slate-500 dark:text-slate-400">
              <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center space-x-2">
                  <span className="font-extrabold text-slate-700 dark:text-slate-300">QORJYN Mesh</span>
                  <span>© 2026 B2B Network. Все права защищены.</span>
                </div>
                <div className="flex items-center space-x-4 text-slate-500 dark:text-slate-400">
                  <span>Port 4000 Django Server</span>
                  <span>•</span>
                  <span>Green API WhatsApp Integration</span>
                </div>
              </div>
            </footer>
          </LanguageProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
