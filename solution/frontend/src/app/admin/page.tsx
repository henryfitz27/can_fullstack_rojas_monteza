"use client"

import { useSession, signOut } from "next-auth/react"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function AdminPage() {
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (status === "loading") return // Esperando carga

    if (!session) {
      router.push("/login")
      return
    }
  }, [session, status, router])

  if (status === "loading") {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-[200px]">
          <div>Cargando...</div>
        </div>
      </div>
    )
  }

  if (!session) {
    return null // Se redirigirá automáticamente
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Panel de Administración</h1>
        <Button onClick={() => signOut({ callbackUrl: "/login" })}>
          Cerrar Sesión
        </Button>
      </div>
      
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Información del Usuario</CardTitle>
          <CardDescription>Datos de la sesión actual</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2">
            <p><strong>Nombre:</strong> {session.user?.name}</p>
            <p><strong>Email:</strong> {session.user?.email}</p>
            <p><strong>Nombre:</strong> {session.user?.firstName}</p>
            <p><strong>Apellido:</strong> {session.user?.lastName}</p>
            <p><strong>Token expira:</strong> {session.expiresAt}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>🔐 Protección Activada</CardTitle>
          <CardDescription>
            Esta página está protegida con NextAuth v4
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p>
            ✅ Has iniciado sesión correctamente.<br/>
            🛡️ El acceso está protegido tanto por middleware como por componente.<br/>
            🔑 Tu token JWT está disponible para llamadas a la API.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
