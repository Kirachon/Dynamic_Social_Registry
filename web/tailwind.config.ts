import type { Config } from 'tailwindcss'

export default {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        gov: {
          bg: '#f8fafc',
          surface: '#ffffff',
          border: '#e5e7eb',
          text: '#0f172a',
          muted: '#475569',
          primary: '#0a4a6a',
          primaryAlt: '#156c99',
          accent: '#2563eb',
          success: '#16a34a',
          warning: '#f59e0b',
          danger: '#dc2626',
        },
      },
      boxShadow: {
        card: '0 1px 2px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.1)',
      },
      fontFamily: {
        sans: [
          'Inter var',
          'system-ui',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'Noto Sans',
          'Apple Color Emoji',
          'Segoe UI Emoji',
          'Segoe UI Symbol',
        ],
      },
    },
  },
  plugins: [],
} satisfies Config

