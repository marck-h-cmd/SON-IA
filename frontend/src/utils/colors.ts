/**
 * Color utilities and status color mappings
 */

// Color palette Movistar Oficial
export const colors = {
  primary: '#00A9E0', // Movistar Electric Blue / Cyan
  primaryHover: '#0084B4', // Movistar Dark Cyan
  secondary: '#6B7280', // Gray
  success: '#10B981', // Green
  warning: '#F59E0B', // Amber
  danger: '#EF4444', // Red
  info: '#00A9E0', // Movistar Cyan
  light: '#EBF7FC', // Soft Movistar Cyan Tint
  dark: '#0C4A6E', // Deep Movistar Navy
};

// Invoice status colors
export const statusColors = {
  factura: {
    Pendiente: '#FFC107', // Amber
    Pagado: '#10B981', // Green
    Vencido: '#EF4444', // Red
  },
  agente: {
    activo: '#10B981', // Green
    idle: '#9CA3AF', // Gray
    error: '#EF4444', // Red
  },
  oferta: {
    pendiente: '#3B82F6', // Blue
    aceptada: '#10B981', // Green
    rechazada: '#EF4444', // Red
    expirada: '#9CA3AF', // Gray
  },
  mora: {
    temprana: '#FCD34D', // Light Yellow
    media: '#FCA5A5', // Light Red
    tardia: '#EF4444', // Red
    critica: '#991B1B', // Dark Red
  },
};

/**
 * Get color for invoice status
 */
export const getFacturaStatusColor = (status: string): string => {
  return statusColors.factura[status as keyof typeof statusColors.factura] || '#9CA3AF';
};

/**
 * Get color for agent status
 */
export const getAgentStatusColor = (status: string): string => {
  return statusColors.agente[status as keyof typeof statusColors.agente] || '#9CA3AF';
};

/**
 * Get color for offer status
 */
export const getOfertaStatusColor = (status: string): string => {
  return statusColors.oferta[status as keyof typeof statusColors.oferta] || '#9CA3AF';
};

/**
 * Get color for collection stage (mora)
 */
export const getMoraStatusColor = (stage: string): string => {
  return statusColors.mora[stage as keyof typeof statusColors.mora] || '#9CA3AF';
};

/**
 * Get background color class for Tailwind
 */
export const getStatusBgClass = (status: string, type: 'factura' | 'agente' | 'oferta' | 'mora' = 'factura'): string => {
  const colorMap: Record<string, string> = {
    // Factura
    Pendiente: 'bg-amber-100',
    Pagado: 'bg-green-100',
    Vencido: 'bg-red-100',
    // Agente
    activo: 'bg-green-100',
    idle: 'bg-gray-100',
    error: 'bg-red-100',
    // Oferta
    pendiente: 'bg-blue-100',
    aceptada: 'bg-green-100',
    rechazada: 'bg-red-100',
    expirada: 'bg-gray-100',
    // Mora
    temprana: 'bg-yellow-100',
    media: 'bg-orange-100',
    tardia: 'bg-red-200',
    critica: 'bg-red-300',
  };
  return colorMap[status] || 'bg-gray-100';
};

/**
 * Get text color class for Tailwind
 */
export const getStatusTextClass = (status: string, type: 'factura' | 'agente' | 'oferta' | 'mora' = 'factura'): string => {
  const colorMap: Record<string, string> = {
    // Factura
    Pendiente: 'text-amber-700',
    Pagado: 'text-green-700',
    Vencido: 'text-red-700',
    // Agente
    activo: 'text-green-700',
    idle: 'text-gray-700',
    error: 'text-red-700',
    // Oferta
    pendiente: 'text-blue-700',
    aceptada: 'text-green-700',
    rechazada: 'text-red-700',
    expirada: 'text-gray-700',
    // Mora
    temprana: 'text-yellow-700',
    media: 'text-orange-700',
    tardia: 'text-red-700',
    critica: 'text-red-900',
  };
  return colorMap[status] || 'text-gray-700';
};

/**
 * Get morosidad indicator color
 */
export const getMorosidadColor = (percentage: number): string => {
  if (percentage < 2) return '#10B981'; // Green
  if (percentage < 5) return '#FCD34D'; // Amber
  return '#EF4444'; // Red
};

/**
 * Get confidence score color
 */
export const getScoreColor = (score: number): string => {
  if (score >= 80) return '#10B981'; // Green
  if (score >= 60) return '#3B82F6'; // Blue
  if (score >= 40) return '#F59E0B'; // Amber
  return '#EF4444'; // Red
};

/**
 * Get score badge class
 */
export const getScoreBadgeClass = (score: number): string => {
  if (score >= 80) return 'bg-green-100 text-green-700';
  if (score >= 60) return 'bg-blue-100 text-blue-700';
  if (score >= 40) return 'bg-amber-100 text-amber-700';
  return 'bg-red-100 text-red-700';
};
