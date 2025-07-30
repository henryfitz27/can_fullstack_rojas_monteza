
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { getServerSession } from "next-auth/next"
import { authOptions } from "@/auth"
import { signOut } from "next-auth/react"
import SignOut from "@/components/auth/sign-out"

export default async function AdminPage() {
    // Verifica la sesión del usuario
    const session = await getServerSession(authOptions)
    if (!session) {
        return (
            <div className="container mx-auto p-6">
                <div className="flex items-center justify-center min-h-[200px]">
                    <div>No tienes permiso para acceder a esta página.</div>
                </div>
            </div>
        )
    }

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Mi cuenta</h1>
       <SignOut />
      </div>
      
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Información del Usuario</CardTitle>
          <CardDescription>Datos de la sesión actual</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2">
  
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
            Esta página está protegida con NextAuth 
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
