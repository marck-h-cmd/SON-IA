/**
 * Formatting utilities
 */

/**
 * Format currency as Peruvian Soles (S/)
 */
export const formatCurrency = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined || value === '') return 'S/ 0.00';
  const num = typeof value === 'number' ? value : Number(value);
  if (isNaN(num)) return 'S/ 0.00';

  try {
    return new Intl.NumberFormat('es-PE', {
      style: 'currency',
      currency: 'PEN',
      minimumFractionDigits: 2,
    }).format(num);
  } catch {
    return `S/ ${num.toFixed(2)}`;
  }
};

/**
 * Format percentage
 */
export const formatPercentage = (value: number | string | null | undefined, decimals: number = 1): string => {
  if (value === null || value === undefined || value === '') return '0.0%';
  const num = typeof value === 'number' ? value : Number(value);
  if (isNaN(num)) return '0.0%';
  return `${num.toFixed(decimals)}%`;
};

/**
 * Format date to readable format (DD/MM/YYYY)
 */
export const formatDate = (dateInput: string | number | Date | null | undefined): string => {
  if (!dateInput) return 'N/A';
  try {
    const date = dateInput instanceof Date ? dateInput : new Date(dateInput);
    if (isNaN(date.getTime())) return 'N/A';
    
    return new Intl.DateTimeFormat('es-PE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    }).format(date);
  } catch {
    return 'N/A';
  }
};

/**
 * Format date and time (DD/MM/YYYY HH:mm:ss)
 */
export const formatDateTime = (dateInput: string | number | Date | null | undefined): string => {
  if (!dateInput) return 'N/A';
  try {
    const date = dateInput instanceof Date ? dateInput : new Date(dateInput);
    if (isNaN(date.getTime())) return 'N/A';
    
    return new Intl.DateTimeFormat('es-PE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }).format(date);
  } catch {
    return 'N/A';
  }
};

/**
 * Format time ago (e.g., "hace 2 horas")
 */
export const formatTimeAgo = (dateInput: string | number | Date | null | undefined): string => {
  if (!dateInput) return 'N/A';
  try {
    const date = dateInput instanceof Date ? dateInput : new Date(dateInput);
    if (isNaN(date.getTime())) return 'N/A';
    
    const now = new Date();
    const secondsAgo = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (secondsAgo < 0) return formatDate(date);
    if (secondsAgo < 60) return 'hace unos segundos';
    const minutesAgo = Math.floor(secondsAgo / 60);
    if (minutesAgo < 60) return `hace ${minutesAgo} ${minutesAgo === 1 ? 'minuto' : 'minutos'}`;
    const hoursAgo = Math.floor(minutesAgo / 60);
    if (hoursAgo < 24) return `hace ${hoursAgo} ${hoursAgo === 1 ? 'hora' : 'horas'}`;
    const daysAgo = Math.floor(hoursAgo / 24);
    if (daysAgo < 7) return `hace ${daysAgo} ${daysAgo === 1 ? 'día' : 'días'}`;
    return formatDate(date);
  } catch {
    return 'N/A';
  }
};

/**
 * Format large numbers with thousand separators
 */
export const formatNumber = (value: number | string | null | undefined, decimals: number = 0): string => {
  if (value === null || value === undefined || value === '') return '0';
  const num = typeof value === 'number' ? value : Number(value);
  if (isNaN(num)) return '0';

  try {
    return new Intl.NumberFormat('es-PE', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(num);
  } catch {
    return num.toFixed(decimals);
  }
};

/**
 * Format file size
 */
export const formatFileSize = (bytes: number | null | undefined): string => {
  if (!bytes || bytes <= 0 || isNaN(bytes)) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Capitalize string
 */
export const capitalize = (str: string | null | undefined): string => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

/**
 * Convert enum to readable string
 */
export const enumToString = (value: string | null | undefined): string => {
  if (!value) return '';
  return value
    .replace(/_/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .toLowerCase()
    .split(' ')
    .map((word) => capitalize(word))
    .join(' ');
};
