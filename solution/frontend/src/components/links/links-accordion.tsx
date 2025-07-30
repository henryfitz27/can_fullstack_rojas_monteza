"use client"

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { LinkRecord } from "@/types/files"
import { Badge } from "@/components/ui/badge"
import { Calendar, Globe, CheckCircle, XCircle } from "lucide-react"

interface LinksAccordionProps {
  links: LinkRecord[]
}

export function LinksAccordion({ links }: LinksAccordionProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  if (links.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No se encontraron links para este archivo.
      </div>
    )
  }

  return (
    <Accordion type="single" collapsible className="w-full">
      {links.map((link) => (
        <AccordionItem key={link.id} value={`link-${link.id}`}>
          <AccordionTrigger className="text-left">
            <div className="flex items-center justify-between w-full mr-4">
              <span className="font-medium">
                {link.title || "No se encontró título para este link"}
              </span>
              <div className="flex items-center space-x-2">
                {link.success ? (
                  <Badge variant="default" className="bg-green-100 text-green-800">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Exitoso
                  </Badge>
                ) : (
                  <Badge variant="destructive">
                    <XCircle className="w-3 h-3 mr-1" />
                    Error
                  </Badge>
                )}
              </div>
            </div>
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-4 pt-2">
              {/* URL */}
              <div className="flex items-start space-x-2">
                <Globe className="w-4 h-4 mt-1 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">URL:</p>
                  <a 
                    href={link.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 underline text-sm break-all"
                  >
                    {link.url}
                  </a>
                </div>
              </div>

              {/* Fecha de publicación */}
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-muted-foreground" />
                <div>
                  <span className="text-sm font-medium">Fecha de publicación: </span>
                  <span className="text-sm">{formatDate(link.postDate)}</span>
                </div>
              </div>

              {/* Estado de la página */}
              <div className="flex items-center space-x-2">
                <div>
                  <span className="text-sm font-medium">Página existe: </span>
                  <Badge variant={link.pageExists ? "default" : "secondary"}>
                    {link.pageExists ? "Sí" : "No"}
                  </Badge>
                </div>
              </div>

              {/* Error description si existe */}
              {link.errorDescription && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm font-medium text-red-800">Error:</p>
                  <p className="text-sm text-red-700">{link.errorDescription}</p>
                </div>
              )}

              {/* Contenido */}
              <div>
                <p className="text-sm font-medium mb-2">Contenido:</p>
                <div className="bg-gray-50 p-3 rounded-md max-h-60 overflow-y-auto">
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">
                    {link.content}
                  </p>
                </div>
              </div>

              {/* Fecha de procesamiento */}
              <div className="text-xs text-muted-foreground">
                Procesado el: {formatDate(link.processedDate)}
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  )
}
