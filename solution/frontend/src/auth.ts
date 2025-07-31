import NextAuth, { NextAuthOptions } from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"

interface LoginResponse {
  token: string
  user: {
    id: number
    firstName: string
    lastName: string
    email: string
    createdAt: string
  }
  expiresAt: string
}

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        try {
          const response = await fetch(`${process.env.API_BASE_URL}/login`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          })

          if (!response.ok) {
            return null
          }

          const data: LoginResponse = await response.json()

          return {
            id: data.user.id.toString(),
            email: data.user.email,
            name: `${data.user.firstName} ${data.user.lastName}`,
            firstName: data.user.firstName,
            lastName: data.user.lastName,
            token: data.token,
            expiresAt: data.expiresAt,
          }
        } catch (error) {
          console.error("Login error:", error)
          return null
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = user.token
        token.firstName = user.firstName
        token.lastName = user.lastName
        token.expiresAt = user.expiresAt
      }
      return token
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string
      session.user.firstName = token.firstName as string
      session.user.lastName = token.lastName as string
      session.expiresAt = token.expiresAt as string
      return session
    },
    async redirect({ url, baseUrl }) {
      // Si la URL es relativa, añadir el baseUrl
      if (url.startsWith("/")) return `${baseUrl}${url}`
      // Si la URL pertenece al mismo origen, permitir la redirección
      if (new URL(url).origin === baseUrl) return url
      // De lo contrario, redirigir al baseUrl
      return baseUrl
    },
  },
  pages: {
    signIn: "/login",
  },
  session: {
    strategy: "jwt",
    maxAge: 24 * 60 * 60, // 24 horas
  },
  jwt: {
    maxAge: 24 * 60 * 60, // 24 horas
  },
  cookies: {
    sessionToken: {
      name: 'next-auth.session-token',
      options: {
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: false, // Deshabilitamos HTTPS para localhost en Docker
        domain: undefined, // No restringir dominio para localhost
      },
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
}

export default NextAuth(authOptions)