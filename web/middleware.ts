import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Simple RBAC route guard for SSR/edge
// Roles are expected from JWT claims (e.g., realm_access.roles from Keycloak)
function getRolesFromToken(token: string | undefined): string[] {
  if (!token) return []
  try {
    const [, payload] = token.split('.')
    const json = JSON.parse(Buffer.from(payload, 'base64').toString())
    const roles = json?.realm_access?.roles || json?.resource_access?.['dsrs-web']?.roles || []
    return Array.isArray(roles) ? roles : []
  } catch {
    return []
  }
}

export function middleware(req: NextRequest) {
  const url = req.nextUrl.clone()
  const protectedPaths: Record<string, string[]> = {
    '/admin': ['admin'],
    '/quality': ['admin', 'quality'],
    '/soc': ['admin', 'security'],
  }
  for (const [path, rolesRequired] of Object.entries(protectedPaths)) {
    if (url.pathname.startsWith(path)) {
      const token = req.cookies.get('dsrs_token')?.value
      const roles = getRolesFromToken(token)
      const ok = rolesRequired.some(r => roles.includes(r))
      if (!ok) {
        url.pathname = '/login'
        return NextResponse.redirect(url)
      }
    }
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['/admin/:path*', '/quality/:path*', '/soc/:path*'],
}

