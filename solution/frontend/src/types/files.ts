export interface FileRecord {
  id: number
  totalLinks: number
  filePath: string
  fileName: string
  totalProcessed: number
  totalFailed: number
  status: "PENDING" | "PROCESSED" | "FAILED"
  uploadedAt: string
  userId: number
}

export interface FileTableData {
  totalLinks: number
  fileName: string
  totalProcessed: number
  totalFailed: number
  status: "PENDING" | "PROCESSED" | "FAILED"
  uploadedAt: string
}
