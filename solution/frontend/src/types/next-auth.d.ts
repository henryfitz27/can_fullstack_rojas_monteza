import { DefaultSession, DefaultUser } from "next-auth"
import { JWT, DefaultJWT } from "next-auth/jwt"

declare module "next-auth" {
  interface Session extends DefaultSession {
    user: {
      id: string
      firstName: string
      lastName: string
    } & DefaultSession["user"]
    accessToken: string
    expiresAt: string
  }

  interface User extends DefaultUser {
    id: string
    firstName: string
    lastName: string
    token: string
    expiresAt: string
  }
}

declare module "next-auth/jwt" {
  interface JWT extends DefaultJWT {
    id: string
    accessToken: string
    firstName: string
    lastName: string
    expiresAt: string
  }
}