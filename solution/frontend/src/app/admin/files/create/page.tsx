

import UploadForm from "@/components/files/upload-form"
import { Button } from "@/components/ui/button"

import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function CreateFilePage() {


  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/admin/files">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver
          </Button>
        </Link>        
      </div>
      <div>
          <h1 className="text-2xl font-bold ">Subir Archivo</h1>
          <p className="text-gray-500">Sube un archivo TXT o CSV con los links para procesar</p>
        </div>

      {/* Upload Form */}
      <UploadForm />    
    </div>
  )
}
