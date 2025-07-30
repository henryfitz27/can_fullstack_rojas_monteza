import { getServerSession } from "next-auth/next"
import { authOptions } from "@/auth"
import { getFileLinks } from "@/actions/files"
import { LinksAccordion } from "@/components/links"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { LinkRecord } from "@/types/files"

interface FileLinksPageProps {
  params: Promise<{
    fileId: string
  }>
}

export default async function FileLinksPage({ params }: FileLinksPageProps) {
  // Await params antes de usarlos
  const { fileId } = await params
  
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

  // Obtener los links del archivo
  let links: LinkRecord[] = []
  let error: string | null = null
  
  try {
    links = await getFileLinks(fileId)
  } catch (err) {
    error = err instanceof Error ? err.message : "Error al cargar los links"
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <div className="flex items-center gap-4 mb-4">
          <Link href="/admin/files">
            <Button variant="outline" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Volver a archivos
            </Button>
          </Link>
        </div>
        <h1 className="text-3xl font-bold mb-2">Links del Archivo</h1>        
        <p className="text-muted-foreground">
          Lista de todos los links procesados para el archivo ID: {fileId}
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Links Procesados</CardTitle>
          <CardDescription>
            {error ? "Error al cargar los links" : `${links.length} links encontrados`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error ? (
            <div className="text-center py-8">
              <div className="text-red-600 mb-4">Error: {error}</div>
              <p className="text-muted-foreground">
                No se pudieron cargar los links. Intenta recargar la página.
              </p>
            </div>
          ) : (
            <LinksAccordion links={links} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
