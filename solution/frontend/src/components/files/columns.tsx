"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { FileTableData } from "@/types/files"
import { Eye } from "lucide-react"
import Link from "next/link"

const getStatusColor = (status: string) => {
  switch (status) {
    case "PENDING":
      return "bg-yellow-100 text-yellow-800 border-yellow-300"
    case "PROCESSED":
      return "bg-green-100 text-green-800 border-green-300"
    case "FAILED":
      return "bg-red-100 text-red-800 border-red-300"
    default:
      return "bg-gray-100 text-gray-800 border-gray-300"
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString("es-ES", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export const columns: ColumnDef<FileTableData>[] = [
  {
    accessorKey: "fileName",
    header: "Nombre del Archivo",
    cell: ({ row }) => {
      const fileName = row.getValue("fileName") as string
      return (
        <div className="font-medium text-left min-w-[200px]">
          {fileName}
        </div>
      )
    },
    enableSorting: true,
    enableHiding: false,
  },
  {
    accessorKey: "totalLinks",
    header: "Total Enlaces",
    cell: ({ row }) => {
      const totalLinks = row.getValue("totalLinks") as number
      return (
        <div className="text-center">
          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
            {totalLinks}
          </Badge>
        </div>
      )
    },
    enableSorting: true,
  },
  {
    accessorKey: "totalProcessed",
    header: "Procesados",
    cell: ({ row }) => {
      const totalProcessed = row.getValue("totalProcessed") as number
      return (
        <div className="text-center">
          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
            {totalProcessed}
          </Badge>
        </div>
      )
    },
    enableSorting: true,
  },
  {
    accessorKey: "totalFailed",
    header: "Fallidos",
    cell: ({ row }) => {
      const totalFailed = row.getValue("totalFailed") as number
      return (
        <div className="text-center">
          <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
            {totalFailed}
          </Badge>
        </div>
      )
    },
    enableSorting: true,
  },
  {
    accessorKey: "status",
    header: "Estado",
    cell: ({ row }) => {
      const status = row.getValue("status") as string
      return (
        <div className="text-center">
          <Badge className={getStatusColor(status)}>
            {status === "PENDING" ? "Pendiente" : 
             status === "PROCESSED" ? "Procesado" : 
             "Fallido"}
          </Badge>
        </div>
      )
    },
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id))
    },
    enableSorting: true,
  },
  {
    accessorKey: "uploadedAt",
    header: "Fecha de Subida",
    cell: ({ row }) => {
      const uploadedAt = row.getValue("uploadedAt") as string
      return (
        <div className="text-center min-w-[150px]">
          {formatDate(uploadedAt)}
        </div>
      )
    },
    enableSorting: true,
  },
  {
    id: "actions",
    header: "Acciones",
    cell: ({ row }) => {
      const fileId = row.original.id
      return (
        <div className="text-center">
          <Link href={`/admin/files/${fileId}`}>
            <Button variant="outline" size="sm">
              <Eye className="w-4 h-4 mr-2" />
              Ver links
            </Button>
          </Link>
        </div>
      )
    },
    enableSorting: false,
    enableHiding: false,
  },
]
