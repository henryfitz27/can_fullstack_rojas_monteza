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
  id: number
  totalLinks: number
  fileName: string
  totalProcessed: number
  totalFailed: number
  status: "PENDING" | "PROCESSED" | "FAILED"
  uploadedAt: string
}

export interface LinkRecord {
  id: number
  fileId: number
  url: string
  title: string
  postDate: string
  content: string
  pageExists: boolean
  success: boolean
  errorDescription: string | null
  processedDate: string
}
