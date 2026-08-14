import React from 'react';

interface Column<T> {
  header: string;
  key: keyof T;
  render?: (value: unknown, row: T) => React.ReactNode;
  align?: 'left' | 'center' | 'right';
  width?: string;
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor?: (row: T) => string;
  onRowClick?: (row: T) => void;
  loading?: boolean;
  emptyMessage?: string;
}

export const Table = React.forwardRef<HTMLTableElement, TableProps<any>>(
  ({ columns, data, keyExtractor, onRowClick, loading = false, emptyMessage = 'No hay datos' }, ref) => {
    const alignClasses = {
      left: 'text-left',
      center: 'text-center',
      right: 'text-right',
    };

    return (
      <div className="overflow-x-auto">
        <table ref={ref} className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-100 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
              {columns.map((col, colIndex) => (
                <th
                  key={`${String(col.key)}-${colIndex}`}
                  className={`px-6 py-3 font-semibold text-gray-900 dark:text-white ${alignClasses[col.align || 'left']}`}
                  style={{ width: col.width }}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={columns.length} className="px-6 py-4 text-center text-gray-500">
                  Cargando...
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-6 py-4 text-center text-gray-500">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((row, index) => (
                <tr
                  key={keyExtractor ? keyExtractor(row) : index}
                  onClick={() => onRowClick?.(row)}
                  className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors cursor-pointer"
                >
                  {columns.map((col, colIndex) => (
                    <td
                      key={`${String(col.key)}-${colIndex}`}
                      className={`px-6 py-4 text-gray-900 dark:text-gray-200 ${alignClasses[col.align || 'left']}`}
                    >
                      {col.render ? col.render(row[col.key], row) : String(row[col.key])}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    );
  }
);

Table.displayName = 'Table';

export default Table;
