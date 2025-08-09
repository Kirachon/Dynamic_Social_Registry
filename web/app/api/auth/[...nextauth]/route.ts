import NextAuth from "next-auth"
import Keycloak from "next-auth/providers/keycloak"
import { cookies } from "next/headers"

const handler = NextAuth({
  debug: false,
  providers: [
    Keycloak({
      issuer: process.env.KEYCLOAK_ISSUER,
      clientId: process.env.KEYCLOAK_CLIENT_ID,
      clientSecret: process.env.KEYCLOAK_CLIENT_SECRET,
      authorization: { params: { scope: "openid profile email" } },
    }),
  ],
  session: { strategy: "jwt" },
  callbacks: {
    async jwt({ token, account }) {
      if (account) {
        // Persist access token and ID token (for roles)
        // @ts-ignore
        token.accessToken = account.access_token
        // @ts-ignore
        token.idToken = account.id_token
      }
      return token
    },
    async session({ session, token }) {
      // @ts-ignore
      session.accessToken = token.accessToken
      // Try to set dsrs_token cookie for Kong usage
      try {
        if (token && (token as any).accessToken) {
          cookies().set("dsrs_token", String((token as any).accessToken), { path: "/", httpOnly: false, sameSite: "lax" })
        }
      } catch {}
      return session
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
})

export { handler as GET, handler as POST }

