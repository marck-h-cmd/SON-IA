/**
 * Utilidad para exportación de tablas a formato Excel / CSV
 * Incluye UTF-8 BOM para compatibilidad total con Microsoft Excel en español.
 */

export function exportToCsv<T extends Record<string, any>>(
  filename: string,
  data: T[],
  columns: { header: string; key: keyof T | ((row: T) => any) }[]
) {
  if (!data || !data.length) {
    alert('No hay datos para exportar.');
    return;
  }

  // Generar encabezados
  const headers = columns.map((col) => `"${col.header.replace(/"/g, '""')}"`).join(';');

  // Generar filas
  const rows = data.map((row) => {
    return columns
      .map((col) => {
        let val = typeof col.key === 'function' ? col.key(row) : row[col.key];
        if (val === null || val === undefined) val = '';
        if (typeof val === 'number') {
          // Formato numérico para Excel
          return `"${val.toFixed(2).replace('.', ',')}"`;
        }
        return `"${String(val).replace(/"/g, '""')}"`;
      })
      .join(';');
  });

  // UTF-8 Byte Order Mark (BOM) para caracteres como tildes y ñ
  const csvContent = '\uFEFF' + [headers, ...rows].join('\r\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}_${new Date().toISOString().slice(0, 10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
