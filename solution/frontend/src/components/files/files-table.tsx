"use client"

import { FilesDataTable } from "./data-table"
import { columns } from "./columns"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { FileRecord, FileTableData } from "@/types/files"

interface FilesTableProps {
  files: FileRecord[]
}

export default function FilesTable({ files }: FilesTableProps) {
  // Transformar los datos para mostrar solo los campos necesarios
  const transformedData: FileTableData[] = files.map((file) => ({
    id: file.id,
    totalLinks: file.totalLinks,
    fileName: file.fileName,
    totalProcessed: file.totalProcessed,
    totalFailed: file.totalFailed,
    status: file.status,
    uploadedAt: file.uploadedAt,
  }))

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Archivos</CardTitle>
          <CardDescription>
            Gestión y seguimiento de archivos subidos al sistema
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        <FilesDataTable columns={columns} data={transformedData} />
      </CardContent>
    </Card>
  )
}
