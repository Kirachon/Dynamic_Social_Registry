import './globals.css'
import type { Metadata } from 'next'
import Link from 'next/link'
import React from 'react'

export const metadata: Metadata = {
  title: 'DSRS Prototype',
  description: 'Dynamic Social Registry System Dashboards (Prototype)',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gov-bg text-gov-text">
        <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 bg-gov-accent text-white px-3 py-1 rounded">Skip to content</a>
        <div className="min-h-screen grid grid-cols-[260px_1fr]">
          <aside className="bg-gov-surface border-r border-gov-border p-4 hidden md:block">
            <h1 className="text-lg font-semibold mb-4">DSRS Dashboards</h1>
            <nav className="space-y-2 text-sm">
              {[
                ['Operations','/operations'],
                ['Executive','/executive'],
                ['Beneficiary','/beneficiary'],
                ['Field','/field'],
                ['Programs','/programs'],
                ['Payments','/payments'],
                ['SOC','/soc'],
                ['Analytics','/analytics'],
                ['Admin','/admin'],
                ['Quality','/quality'],
                ['Mobile Registration','/mobile/registration'],
              ].map(([label, href]) => (
                <div key={href}>
                  <Link className="block px-3 py-2 rounded hover:bg-gov-bg" href={href}>{label}</Link>
                </div>
              ))}
            </nav>
          </aside>
          <div>
            <header className="bg-gov-surface border-b border-gov-border p-4 flex items-center justify-between sticky top-0 z-10">
              <div className="flex items-center gap-3">
                <button className="md:hidden px-3 py-2 border rounded" aria-label="Open navigation">☰</button>
                <span className="font-semibold">Dynamic Social Registry System</span>
              </div>
              <div className="text-sm text-gov-muted">Prototype | Accessible Neutral Theme</div>
            </header>
            <main id="main" className="p-4 max-w-[1600px] mx-auto">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  )
}

