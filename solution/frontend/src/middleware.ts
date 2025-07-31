// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { getToken } from 'next-auth/jwt';

export async function middleware(request: NextRequest) {
  // Obtiene el token de la sesión del usuario.
  // Es crucial tener la variable de entorno NEXTAUTH_SECRET configurada.
  const token = await getToken({ 
    req: request, 
    secret: process.env.NEXTAUTH_SECRET,
    secureCookie: false // Deshabilitamos secureCookie para Docker localhost
  });

  const { pathname } = request.nextUrl;

  // 1. Si el usuario NO está logueado (!token)
  if (!token) {
    // Y está intentando acceder a una ruta protegida bajo /admin
    if (pathname.startsWith('/admin')) {
      // Redirigir a la página de login
      const loginUrl = new URL('/login', request.url);
      return NextResponse.redirect(loginUrl);
    }
    
    // Y está intentando acceder a la página principal
    if (pathname === '/') {
        // Redirigir a la página de login
        const loginUrl = new URL('/login', request.url);
        return NextResponse.redirect(loginUrl);
    }
  }

  // 2. Si el usuario SÍ está logueado (token)
  if (token) {
    // Si un usuario logueado intenta ir a /login, redirigirlo al admin
    if (pathname === '/login' || pathname === '/register') {
      const adminUrl = new URL('/admin', request.url);
      return NextResponse.redirect(adminUrl);
    }
  }

  // Si ninguna de las condiciones anteriores se cumple, permite que la solicitud continúe.
  return NextResponse.next();
}

// El `matcher` especifica en qué rutas se ejecutará este middleware.
// Así evitamos que se ejecute en rutas de API, archivos estáticos (_next/*), etc.
export const config = {
  matcher: [
    /*
     * Coincide con todas las rutas excepto las que comienzan con:
     * - api (rutas de API)
     * - _next/static (archivos estáticos)
     * - _next/image (imágenes optimizadas)
     * - favicon.ico (ícono de la página)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
    '/', // Asegura que la raíz también sea evaluada
  ],
};