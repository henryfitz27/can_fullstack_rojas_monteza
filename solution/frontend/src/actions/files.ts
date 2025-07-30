"use server"

import { getServerSession } from "next-auth/next"
import { authOptions } from "@/auth"
import { FileRecord } from "@/types/files"

export async function getFiles(): Promise<FileRecord[]> {
  // Obtener la sesión del usuario
  const session = await getServerSession(authOptions)
  
  if (!session?.accessToken) {
    throw new Error("No autorizado")
  }

  try {
    const response = await fetch(`${process.env.API_BASE_URL}/files`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${session.accessToken}`,
        "Content-Type": "application/json",
      },
      cache: "no-store", // Para obtener datos frescos en cada request
    })

    if (!response.ok) {
      throw new Error(`Error al obtener archivos: ${response.status} ${response.statusText}`)
    }

    const data: FileRecord[] = await response.json()
    return data
  } catch (error) {
    console.error("Error fetching files:", error)
    throw new Error("Error al cargar los archivos")
  }
}
