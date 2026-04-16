import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Github } from 'lucide-react'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'EthicLens Audit | AI Ethics Dataset Quality Framework',
  description:
    'Audit your AI ethics datasets across 8 quality dimensions including duplicate detection, class balance, lexical diversity, and more.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <header className="bg-gray-900 border-b border-gray-800 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <a href="/" className="flex items-center gap-2 group">
                <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">EL</span>
                </div>
                <span className="text-white font-semibold text-lg">
                  <span className="text-indigo-400">Ethic</span>Lens Audit
                </span>
              </a>

              <nav className="flex items-center gap-6">
                <a
                  href="/"
                  className="text-gray-400 hover:text-white text-sm transition-colors"
                >
                  Home
                </a>
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 text-gray-400 hover:text-white text-sm transition-colors"
                >
                  <Github size={16} />
                  <span>GitHub</span>
                </a>
              </nav>
            </div>
          </div>
        </header>

        <main className="min-h-screen bg-slate-50">
          {children}
        </main>

        <footer className="bg-gray-900 border-t border-gray-800 py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <p className="text-gray-400 text-sm">
              Built for AI Ethics Research &mdash;{' '}
              <span className="text-indigo-400">EthicLens Audit Framework</span>
            </p>
          </div>
        </footer>
      </body>
    </html>
  )
}
