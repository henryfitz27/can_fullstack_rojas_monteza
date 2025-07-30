"use client"

import { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ProgressBar } from "@/components/ui/progress"
import { Upload, FileText, X, CheckCircle, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"

interface FileDropzoneProps {
  onFileSelect: (file: File) => void
  onFileRemove: () => void
  selectedFile: File | null
  isUploading?: boolean
  uploadStatus?: "idle" | "uploading" | "success" | "error"
  uploadProgress?: number
  errorMessage?: string
}

export function FileDropzone({
  onFileSelect,
  onFileRemove,
  selectedFile,
  isUploading = false,
  uploadStatus = "idle",
  uploadProgress = 0,
  errorMessage
}: FileDropzoneProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      
      // Validar tipo de archivo
      if (!file.name.endsWith('.txt') && !file.name.endsWith('.csv')) {
        return
      }
      
      // Validar tamaño (1MB)
      if (file.size > 1048576) {
        return
      }
      
      onFileSelect(file)
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'text/csv': ['.csv']
    },
    maxSize: 1048576, // 1MB
    maxFiles: 1,
    disabled: isUploading
  })

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getStatusIcon = () => {
    switch (uploadStatus) {
      case "success":
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case "error":
        return <AlertCircle className="h-5 w-5 text-red-500" />
      default:
        return <FileText className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusColor = () => {
    switch (uploadStatus) {
      case "success":
        return "border-green-500 bg-green-50"
      case "error":
        return "border-red-500 bg-red-50"
      default:
        return "border-gray-200"
    }
  }

  return (
    <div className="space-y-4">
      {!selectedFile ? (
        <Card
          {...getRootProps()}
          className={cn(
            "border-2 border-dashed transition-colors cursor-pointer",
            isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400",
            isUploading && "cursor-not-allowed opacity-50"
          )}
        >
          <CardContent className="flex flex-col items-center justify-center p-8 text-center">
            <input {...getInputProps()} />
            <Upload className={cn("h-12 w-12 mb-4", isDragActive ? "text-blue-500" : "text-gray-400")} />
            <h3 className="text-lg font-semibold mb-2">
              {isDragActive ? "Suelta el archivo aquí" : "Subir archivo"}
            </h3>
            <p className="text-gray-500 mb-4">
              Arrastra y suelta tu archivo aquí, o haz clic para seleccionar
            </p>
            <div className="text-sm text-gray-400">
              <p>Solo archivos TXT o CSV</p>
              <p>Tamaño máximo: 1MB</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className={cn("border-2", getStatusColor())}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {getStatusIcon()}
                <div>
                  <p className="font-medium">{selectedFile.name}</p>
                  <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
                  {uploadStatus === "uploading" && (
                    <div className="mt-2 space-y-1">
                      <ProgressBar progress={uploadProgress} />
                      <p className="text-xs text-blue-600">Subiendo... {Math.round(uploadProgress)}%</p>
                    </div>
                  )}
                  {uploadStatus === "error" && errorMessage && (
                    <p className="text-sm text-red-500 mt-1">{errorMessage}</p>
                  )}
                </div>
              </div>
              {!isUploading && uploadStatus !== "success" && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onFileRemove}
                  className="text-gray-500 hover:text-red-500"
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {fileRejections.length > 0 && (
        <div className="text-sm text-red-500 space-y-1">
          {fileRejections.map(({ file, errors }) => (
            <div key={file.name}>
              <p className="font-medium">{file.name}:</p>
              <ul className="list-disc list-inside ml-2">
                {errors.map(error => (
                  <li key={error.code}>
                    {error.code === "file-too-large" && "El archivo es muy grande (máximo 1MB)"}
                    {error.code === "file-invalid-type" && "Tipo de archivo no válido (solo TXT o CSV)"}
                    {error.code === "too-many-files" && "Solo se puede subir un archivo a la vez"}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
