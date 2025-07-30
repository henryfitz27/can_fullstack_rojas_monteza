"use client"

import { useSession } from "next-auth/react"

export function useAuth() {
  const { data: session, status } = useSession()

  return {
    user: session?.user,
    token: session?.accessToken,
    isLoading: status === "loading",
    isAuthenticated: !!session,
    expiresAt: session?.expiresAt,
  }
}
