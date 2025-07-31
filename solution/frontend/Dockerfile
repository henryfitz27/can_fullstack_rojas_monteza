# Dockerfile para Producción (Multi-etapa y optimizado para output: 'standalone')

# ---- Etapa 1: Builder ----
# En esta etapa instalamos dependencias y construimos el proyecto.
FROM node:18-alpine AS builder

# Establece el directorio de trabajo
WORKDIR /app

# Instala pnpm
RUN npm install -g pnpm

# Copia solo los archivos de manifiesto para aprovechar el caché de Docker.
COPY package.json pnpm-lock.yaml* ./

# Instala las dependencias (incluyendo las de desarrollo para la compilación)
RUN pnpm install --frozen-lockfile

# Copia el resto del código fuente de la aplicación
COPY . .

# Argumentos de build para las variables de entorno
ARG NEXTAUTH_URL
ARG NEXTAUTH_URL_INTERNAL
ARG NEXTAUTH_SECRET
ARG API_BASE_URL

# Establece las variables de entorno para el build
ENV NEXTAUTH_URL=$NEXTAUTH_URL
ENV NEXTAUTH_URL_INTERNAL=$NEXTAUTH_URL_INTERNAL
ENV NEXTAUTH_SECRET=$NEXTAUTH_SECRET
ENV API_BASE_URL=$API_BASE_URL

# Desactiva la telemetría de Next.js
ENV NEXT_TELEMETRY_DISABLED=1

# Construye la aplicación para producción
# El 'output: standalone' en next.config.js creará la carpeta .next/standalone
RUN pnpm build

# ---- Etapa 2: Runner ----
# Esta es la etapa final. Es muy ligera porque solo copia los artefactos
# de la carpeta 'standalone' generada por Next.js.
FROM node:18-alpine AS runner

WORKDIR /app

# Establece el entorno a producción
ENV NODE_ENV=production
# Desactiva la telemetría de Next.js
ENV NEXT_TELEMETRY_DISABLED=1

# Variables de entorno para runtime
ENV NEXTAUTH_URL=http://localhost:9999
ENV NEXTAUTH_URL_INTERNAL=http://f1_react_prod:3000
ENV NEXTAUTH_SECRET=mi-super-secreto-unico-para-desarrollo-2025-sgcan
ENV API_BASE_URL=http://f1_hub:5000

# Crea un usuario y grupo sin privilegios para mayor seguridad
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copia la salida 'standalone' desde la etapa 'builder'
# Esta carpeta ya contiene una copia mínima de node_modules y el servidor.
# La barra al final de la ruta de origen (/standalone/) es crucial para asegurar
# que se copie el *contenido* del directorio, no el directorio en sí.
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone/ ./

# Copia la carpeta 'public' y el directorio '.next/static'
# Son necesarios para servir assets estáticos e imágenes optimizadas.
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Cambia al usuario sin privilegios
USER nextjs

# Expone el puerto en el que se ejecutará la aplicación
EXPOSE 3000

# El 'standalone' output genera un 'server.js' para iniciar la aplicación
CMD ["node", "server.js"]