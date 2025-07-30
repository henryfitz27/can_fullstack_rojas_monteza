import { FilesTable } from "@/components/files"
import { getServerSession } from "next-auth/next"
import { authOptions } from "@/auth"
import { getFiles } from "@/actions/files"
import { FileRecord } from "@/types/files"

export default async function FilesPage() {

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

    // Obtener los archivos usando el server action
    let files: FileRecord[] = []
    let error: string | null = null
    
    try {
        files = await getFiles()
    } catch (err) {
        error = err instanceof Error ? err.message : "Error al cargar archivos"
    }

    // Si hay error, mostrar mensaje de error
    if (error) {
        return (
            <div className="container mx-auto p-6">
                <div className="mb-6">
                    <h1 className="text-3xl font-bold mb-2">Gestión de Archivos</h1>        
                    <p className="text-muted-foreground">
                        Administra y monitorea el estado de los archivos subidos al sistema
                    </p>
                </div>
                <div className="flex items-center justify-center min-h-[200px]">
                    <div className="text-center">
                        <div className="text-red-600 mb-4">Error: {error}</div>
                        <p className="text-muted-foreground">
                            No se pudieron cargar los archivos. Intenta recargar la página.
                        </p>
                    </div>
                </div>
            </div>
        )
    }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Gestión de Archivos</h1>        
        <p className="text-muted-foreground">
          Administra y monitorea el estado de los archivos que has subido al sistema          
        </p>
    
      </div>
      
      <FilesTable files={files} />
    </div>
  )
}
