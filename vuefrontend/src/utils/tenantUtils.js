/**
 * Utilidades para detectar y manejar tenants desde subdominios
 */

/**
 * Extrae el subdominio del tenant desde el hostname actual
 * @returns {string|null} El subdominio del tenant o null si no se encuentra
 * 
 * Ejemplos:
 * - phoenix.chalan-pro.net -> 'phoenix'
 * - localhost:3000 -> null (no hay subdominio)
 * - phoenix.localhost:3000 -> 'phoenix' (en desarrollo local)
 */
export function getTenantSubdomain() {
  const hostname = window.location.hostname;
  
  // En desarrollo local, puede ser: subdomain.localhost o subdomain.127.0.0.1
  if (hostname.includes('localhost') || hostname.includes('127.0.0.1')) {
    const parts = hostname.split('.');
    if (parts.length > 1 && parts[0] !== 'localhost' && parts[0] !== '127') {
      return parts[0];
    }
    return null;
  }
  
  // En producción, extraer el subdominio antes del dominio base
  // Ejemplo: phoenix.chalan-pro.net -> phoenix
  const domainParts = hostname.split('.');
  if (domainParts.length >= 3) {
    // Hay al menos un subdominio
    return domainParts[0];
  }
  
  return null;
}

/**
 * Obtiene el dominio base desde el hostname actual
 * @returns {string} El dominio base (ej: 'chalan-pro.net')
 */
export function getBaseDomain() {
  const hostname = window.location.hostname;
  
  // En desarrollo local, retornar el hostname completo
  if (hostname.includes('localhost') || hostname.includes('127.0.0.1')) {
    return hostname;
  }
  
  // En producción, extraer el dominio base (últimas dos partes)
  const parts = hostname.split('.');
  if (parts.length >= 2) {
    return parts.slice(-2).join('.');
  }
  
  return hostname;
}

/**
 * Construye la URL completa del tenant basada en el subdominio
 * @param {string} subdomain - El subdominio del tenant
 * @param {string} path - La ruta a agregar (ej: '/login/')
 * @returns {string} La URL completa
 */
export function buildTenantUrl(subdomain, path = '/') {
  const protocol = window.location.protocol;
  const port = window.location.port ? `:${window.location.port}` : '';
  const baseDomain = getBaseDomain();
  
  // En desarrollo local, usar formato subdomain.localhost:port
  if (baseDomain.includes('localhost') || baseDomain.includes('127.0.0.1')) {
    return `${protocol}//${subdomain}.${baseDomain}${port}${path}`;
  }
  
  // En producción, usar formato subdomain.basedomain.com
  return `${protocol}//${subdomain}.${baseDomain}${path}`;
}

/**
 * Verifica si estamos en el dominio público (sin subdominio de tenant)
 * @returns {boolean} True si estamos en el dominio público
 */
export function isPublicDomain() {
  return getTenantSubdomain() === null;
}

/**
 * Obtiene información del tenant desde el hostname actual
 * @returns {Object} Objeto con información del tenant
 */
export function getTenantInfo() {
  const subdomain = getTenantSubdomain();
  const baseDomain = getBaseDomain();
  const fullDomain = subdomain ? `${subdomain}.${baseDomain}` : baseDomain;
  
  return {
    subdomain,
    baseDomain,
    fullDomain,
    isPublic: isPublicDomain(),
    url: subdomain ? buildTenantUrl(subdomain) : window.location.origin
  };
}

