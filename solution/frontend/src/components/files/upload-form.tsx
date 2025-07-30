"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileDropzone } from "@/components/files"
import { uploadFile } from "@/actions/files"
import { toast } from "sonner"
import { Upload } from "lucide-react"


export default function UploadForm() {
      const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle")
  const [uploadProgress, setUploadProgress] = useState(0)
  const [errorMessage, setErrorMessage] = useState<string>("")
  const router = useRouter()

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
    setUploadStatus("idle")
    setUploadProgress(0)
    setErrorMessage("")
  }

  const handleFileRemove = () => {
    setSelectedFile(null)
    setUploadStatus("idle")
    setUploadProgress(0)
    setErrorMessage("")
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error("Por favor selecciona un archivo")
      return
    }

    setIsUploading(true)
    setUploadStatus("uploading")
    setUploadProgress(0)

    // Simular progreso de subida
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + 10
      })
    }, 200)

    try {
      const formData = new FormData()
      formData.append("file", selectedFile)

      const result = await uploadFile(formData)

      clearInterval(progressInterval)
      setUploadProgress(100)

      if (result.success) {
        setUploadStatus("success")
        toast.success(result.message)
        
        // Redirigir a la lista de archivos después de un breve delay
        setTimeout(() => {
          router.push("/admin/files")
        }, 2000)
      } else {
        setUploadStatus("error")
        setErrorMessage(result.message)
        toast.error(result.message)
      }
    } catch (error) {
      clearInterval(progressInterval)
      setUploadStatus("error")
      const errorMsg = error instanceof Error ? error.message : "Error al subir el archivo"
      setErrorMessage(errorMsg)
      toast.error(errorMsg)
    } finally {
      setIsUploading(false)
    }
  }
  return (
       <div className="max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle>Cargar archivo de links</CardTitle>
            <CardDescription>
              Selecciona un archivo TXT o CSV que contenga los links que deseas procesar. 
              El archivo debe tener un tamaño máximo de 1MB.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <FileDropzone
              onFileSelect={handleFileSelect}
              onFileRemove={handleFileRemove}
              selectedFile={selectedFile}
              isUploading={isUploading}
              uploadStatus={uploadStatus}
              uploadProgress={uploadProgress}
              errorMessage={errorMessage}
            />

            {selectedFile && uploadStatus !== "success" && (
              <div className="flex justify-end space-x-3">
                <Button
                  variant="outline"
                  onClick={handleFileRemove}
                  disabled={isUploading}
                >
                  Cancelar
                </Button>
                <Button
                  onClick={handleUpload}
                  disabled={isUploading}
                  className="min-w-[120px]"
                >
                  {isUploading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                      Subiendo...
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 mr-2" />
                      Subir archivo
                    </>
                  )}
                </Button>
              </div>
            )}

            {uploadStatus === "success" && (
              <div className="text-center space-y-2">
                <p className="text-green-600 font-medium">¡Archivo subido exitosamente!</p>
                <p className="text-sm text-gray-500">Redirigiendo a la lista de archivos...</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Instructions */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-lg">Formato del archivo</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 text-sm">
              <div>
                <h4 className="font-medium mb-2">Archivos TXT o CSV:</h4>
                <p className="text-gray-600 mb-2">Cada link debe estar en una línea separada:</p>
                <div className="bg-gray-50 p-3 rounded font-mono text-xs">
                  https://ejemplo1.com<br />
                  https://ejemplo2.com<br />
                  https://ejemplo3.com
                </div>
              </div>
                            
              <div className="bg-blue-50 p-3 rounded">
                <p className="text-blue-800 text-sm">
                  <strong>Nota:</strong> El archivo debe tener un tamaño máximo de 1MB y solo se aceptan formatos TXT y CSV.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
  )
}
