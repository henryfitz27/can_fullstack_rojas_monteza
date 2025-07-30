# Configuración de NextAuth v4 con API Backend

## Configuración realizada

### 1. Instalación
```bash
pnpm add next-auth
```

### 2. Archivos configurados

#### `.env.local`
- `NEXTAUTH_URL`: URL de la aplicación Next.js (http://localhost:3000)
- `NEXTAUTH_SECRET`: Clave secreta para NextAuth
- `API_BASE_URL`: URL base de tu API backend (http://localhost:9010)

#### `src/auth.ts`
Configuración principal de NextAuth v4 con:
- `authOptions` exportado para reutilización
- Provider de credenciales (email/password)
- Integración con tu API backend en `/login`
- Callbacks para manejar JWT y sesión

#### `src/types/next-auth.d.ts`
Extensión de tipos de TypeScript para NextAuth con propiedades personalizadas:
- `firstName`, `lastName`, `token`, `expiresAt`

#### `src/app/api/auth/[...nextauth]/route.ts`
Handlers de API para NextAuth v4 usando App Router

#### `src/components/auth-provider.tsx`
Proveedor de contexto de sesión para la aplicación

#### `src/components/login-form.tsx`
Formulario de login actualizado para usar NextAuth v4

#### `middleware.ts`
Middleware usando `withAuth` de NextAuth v4 para proteger rutas

### 3. Uso en componentes

#### Hook personalizado
```tsx
import { useAuth } from "@/hooks/use-auth"

function MyComponent() {
  const { user, token, isAuthenticated, isLoading } = useAuth()
  
  if (isLoading) return <div>Cargando...</div>
  if (!isAuthenticated) return <div>No autorizado</div>
  
  return <div>Hola {user?.name}</div>
}
```

#### Usando useSession directamente
```tsx
import { useSession, signOut } from "next-auth/react"

function MyComponent() {
  const { data: session } = useSession()
  
  return (
    <div>
      <p>Usuario: {session?.user?.name}</p>
      <p>Email: {session?.user?.email}</p>
      <p>Token: {session?.accessToken}</p>
      <button onClick={() => signOut()}>Cerrar sesión</button>
    </div>
  )
}
```

### 4. Protección de rutas

Las rutas que empiecen con `/admin` están protegidas por el middleware. Si el usuario no está autenticado, será redirigido a `/login`.

**Nota importante**: Si el middleware no funciona correctamente (problema común con Turbopack), puedes usar protección a nivel de componente:

```tsx
// En tu página protegida
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export default function ProtectedPage() {
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (status === "loading") return // Esperando carga

    if (!session) {
      router.push("/login")
      return
    }
  }, [session, status, router])

  if (status === "loading") {
    return <div>Cargando...</div>
  }

  if (!session) {
    return null
  }

  return <div>Contenido protegido</div>
}
```

### 5. Flujo de autenticación

1. Usuario ingresa credenciales en `/login`
2. NextAuth envía POST a `${API_BASE_URL}/login`
3. Si las credenciales son válidas, el backend retorna:
```json
{
  "token": "jwt-token",
  "user": {
    "id": 1,
    "firstName": "henry",
    "lastName": "Rojas", 
    "email": "henryfitz27@hotmail.com",
    "createdAt": "2025-07-29T19:17:07.194836Z"
  },
  "expiresAt": "2025-07-29T23:35:47.2361546Z"
}
```
4. NextAuth crea una sesión JWT con la información del usuario
5. Usuario es redirigido a `/admin`

### 6. Acceso al token JWT

El token JWT del backend está disponible en `session.accessToken` y puede ser usado para hacer llamadas autenticadas a tu API:

```tsx
import { useSession } from "next-auth/react"

function ApiCall() {
  const { data: session } = useSession()
  
  const fetchData = async () => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/protected-endpoint`, {
      headers: {
        'Authorization': `Bearer ${session?.accessToken}`
      }
    })
    return response.json()
  }
}
```

### 7. Comandos útiles

```bash
# Iniciar desarrollo
pnpm dev

# Verificar middleware
# Si no funciona, usa protección a nivel de componente

# Probar autenticación
# 1. Ve a http://localhost:3000/login
# 2. Ingresa credenciales válidas
# 3. Deberías ser redirigido a /admin
```

## Próximos pasos

1. Cambiar `NEXTAUTH_SECRET` en producción
2. Configurar variables de entorno para producción
3. Si el middleware no funciona con Turbopack, usar protección a nivel de componente
4. Implementar manejo de refresh tokens si es necesario
5. Agregar validación adicional en las páginas protegidas

## Troubleshooting

- **Middleware no funciona**: Usar protección a nivel de componente
- **Token no se guarda**: Verificar configuración de callbacks
- **Redirección infinita**: Verificar que `/login` no esté en el matcher del middleware
