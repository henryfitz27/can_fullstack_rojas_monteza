"use server"

import { getServerSession } from "next-auth/next"
import { authOptions } from "@/auth"
import { FileRecord, LinkRecord } from "@/types/files"

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

export async function getFileLinks(fileId: string): Promise<LinkRecord[]> {
  // Obtener la sesión del usuario
  const session = await getServerSession(authOptions)
  
  if (!session?.accessToken) {
    throw new Error("No autorizado")
  }

  try {
    const response = await fetch(`${process.env.API_BASE_URL}/files/${fileId}/links`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${session.accessToken}`,
        "Content-Type": "application/json",
      },
      cache: "no-store", // Para obtener datos frescos en cada request
    })

    if (!response.ok) {
      throw new Error(`Error al obtener links: ${response.status} ${response.statusText}`)
    }

    const data: LinkRecord[] = await response.json()
    return data
  } catch (error) {
    console.error("Error fetching file links:", error)
    throw new Error("Error al cargar los links del archivo")
  }
}

export async function uploadFile(formData: FormData): Promise<{ success: boolean; message: string; fileId?: string }> {
  // Obtener la sesión del usuario
  const session = await getServerSession(authOptions)
  
  if (!session?.accessToken) {
    throw new Error("No autorizado")
  }

  const file = formData.get("file") as File
  
  if (!file) {
    return { success: false, message: "No se seleccionó ningún archivo" }
  }

  // Validar tipo de archivo
  if (!file.name.endsWith('.txt') && !file.name.endsWith('.csv')) {
    return { success: false, message: "Solo se permiten archivos TXT o CSV" }
  }

  // Validar tamaño del archivo (1MB = 1048576 bytes)
  if (file.size > 1048576) {
    return { success: false, message: "El archivo no puede ser mayor a 1MB" }
  }

  try {
    const uploadFormData = new FormData()
    uploadFormData.append("file", file)

    const response = await fetch(`${process.env.API_BASE_URL}/upload`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${session.accessToken}`,
      },
      body: uploadFormData,
    })

    if (!response.ok) {
      const errorData = await response.text()
      throw new Error(`Error al subir archivo: ${response.status} ${response.statusText} - ${errorData}`)
    }

    const data = await response.json()
    return { 
      success: true, 
      message: "Archivo subido exitosamente", 
      fileId: data.fileId || data.id 
    }
  } catch (error) {
    console.error("Error uploading file:", error)
    return { 
      success: false, 
      message: error instanceof Error ? error.message : "Error al subir el archivo" 
    }
  }
}
