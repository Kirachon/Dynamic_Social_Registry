'use client'

import React from 'react'

type State = { hasError: boolean, error?: any }

export default class ErrorBoundary extends React.Component<{ children: React.ReactNode }, State> {
  state: State = { hasError: false }
  static getDerivedStateFromError(error: any) { return { hasError: true, error } }
  componentDidCatch(error: any, errorInfo: any) { console.error('ErrorBoundary', error, errorInfo) }
  render() {
    if (this.state.hasError) {
      return <div className="p-4 border border-red-200 bg-red-50 text-red-700 text-sm rounded">An error occurred while rendering this section.</div>
    }
    return this.props.children
  }
}

