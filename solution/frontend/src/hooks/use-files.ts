"use client"

import { useState, useEffect } from "react"
import { useSession } from "next-auth/react"
import { FileRecord, FileTableData } from "@/types/files"

export function useFiles() {
  const { data: session } = useSession()
  const [files, setFiles] = useState<FileTableData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchFiles = async () => {
    if (!session?.accessToken) {
      setError("No hay token de acceso disponible")
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      setError(null)

      const response = await fetch("/api/files", {
        headers: {
          "Authorization": `Bearer ${session.accessToken}`,
          "Content-Type": "application/json",
        },
      })

      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`)
      }

      const data: FileRecord[] = await response.json()
      
      // Transformar los datos para mostrar solo los campos necesarios
      const transformedData: FileTableData[] = data.map((file) => ({
        totalLinks: file.totalLinks,
        fileName: file.fileName,
        totalProcessed: file.totalProcessed,
        totalFailed: file.totalFailed,
        status: file.status,
        uploadedAt: file.uploadedAt,
      }))

      setFiles(transformedData)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (session) {
      fetchFiles()
    }
  }, [session])

  return {
    files,
    loading,
    error,
    refetch: fetchFiles,
  }
}
