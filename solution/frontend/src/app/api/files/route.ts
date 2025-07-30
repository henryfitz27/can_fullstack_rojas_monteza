import { NextRequest, NextResponse } from "next/server"

// Datos de ejemplo para el endpoint /files
const mockFilesData = [
  {
    "id": 1,
    "totalLinks": 10,
    "filePath": "abc",
    "fileName": "ejemplo1.txt",
    "totalProcessed": 0,
    "totalFailed": 0,
    "status": "PENDING",
    "uploadedAt": "2025-07-29T15:12:19Z",
    "userId": 1
  },
  {
    "id": 2,
    "totalLinks": 19,
    "filePath": "/app/shared/1_20250729_202532_f997d3120e624fa5914b36adc752eac6.txt",
    "fileName": "file1.txt",
    "totalProcessed": 13,
    "totalFailed": 6,
    "status": "PROCESSED",
    "uploadedAt": "2025-07-29T20:25:32.573597Z",
    "userId": 1
  },
  {
    "id": 3,
    "totalLinks": 25,
    "filePath": "/app/shared/documentos.csv",
    "fileName": "documentos.csv",
    "totalProcessed": 20,
    "totalFailed": 5,
    "status": "PROCESSED",
    "uploadedAt": "2025-07-28T10:30:45Z",
    "userId": 1
  },
  {
    "id": 4,
    "totalLinks": 5,
    "filePath": "/app/shared/test.txt",
    "fileName": "test.txt",
    "totalProcessed": 0,
    "totalFailed": 5,
    "status": "FAILED",
    "uploadedAt": "2025-07-27T14:15:20Z",
    "userId": 1
  },
  {
    "id": 5,
    "totalLinks": 50,
    "filePath": "/app/shared/gran_archivo.txt",
    "fileName": "gran_archivo.txt",
    "totalProcessed": 30,
    "totalFailed": 0,
    "status": "PROCESSED",
    "uploadedAt": "2025-07-26T09:45:12Z",
    "userId": 1
  }
]

export async function GET(request: NextRequest) {
  try {
    // Aquí puedes agregar validación del token de autorización
    const authHeader = request.headers.get("authorization")
    
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return NextResponse.json(
        { error: "Token de autorización requerido" },
        { status: 401 }
      )
    }

    // Simular un pequeño delay como si fuera una API real
    await new Promise(resolve => setTimeout(resolve, 300))

    // Retornar los datos mock
    return NextResponse.json(mockFilesData)
  } catch (error) {
    console.error("Error en API /files:", error)
    return NextResponse.json(
      { error: "Error interno del servidor" },
      { status: 500 }
    )
  }
}
