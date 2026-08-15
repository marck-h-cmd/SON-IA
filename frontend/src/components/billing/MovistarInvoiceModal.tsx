'use client';

import React, { useState } from 'react';
import Button from '@/components/ui/Button';
import { formatCurrency, formatDate } from '@/utils/formatting';
import type { FacturaDetalle } from '@/types/api';

interface MovistarInvoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  factura: FacturaDetalle | null;
  onDownloadXml?: () => void;
  onDownloadPdf?: () => void;
  downloadingPdf?: boolean;
  onSendEmail?: (emailDestino?: string) => Promise<void>;
  sendingEmail?: boolean;
}

export const MovistarInvoiceModal: React.FC<MovistarInvoiceModalProps> = ({
  isOpen,
  onClose,
  factura,
  onDownloadXml,
  onDownloadPdf,
  downloadingPdf = false,
  onSendEmail,
  sendingEmail = false,
}) => {
  const [activeTab, setActiveTab] = useState<'p1' | 'p2' | 'p3'>('p1');
  const [showEmailPrompt, setShowEmailPrompt] = useState(false);
  const [customEmail, setCustomEmail] = useState('');

  if (!isOpen || !factura) return null;

  const fechaEmision = factura.fecha_emision ? new Date(factura.fecha_emision) : new Date();
  const fechaVto = factura.fecha_vencimiento ? new Date(factura.fecha_vencimiento) : new Date();
  
  const formatDayMonth = (dateObj: Date) => {
    try {
      const d = String(dateObj.getDate()).padStart(2, '0');
      const m = String(dateObj.getMonth() + 1).padStart(2, '0');
      return `${d}/${m}`;
    } catch {
      return '15/08';
    }
  };

  const mesNombre = fechaEmision.toLocaleString('es-PE', { month: 'long' });
  const mesCapitalizado = mesNombre.charAt(0).toUpperCase() + mesNombre.slice(1);
  const anio = fechaEmision.getFullYear() || 2026;

  const subtotal = factura.subtotal || 33.81;
  const igv = factura.igv || 6.09;
  const total = factura.monto_total || 39.90;
  const nroRecibo = factura.numero_factura || 'S1AA-0053100009';

  const handlePrint = () => {
    window.print();
  };

  const handleSendEmailClick = async () => {
    if (onSendEmail) {
      const defaultEmail = factura.cliente?.email || `pagos@${factura.cliente?.ruc || 'cliente'}.com`;
      const target = customEmail.trim() || defaultEmail;
      await onSendEmail(target);
      setShowEmailPrompt(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/60 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4">
      <div className="relative bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[94vh] flex flex-col overflow-hidden border border-gray-200 dark:border-gray-800">
        
        {/* Top Control Bar */}
        <div className="print:hidden flex flex-wrap items-center justify-between px-6 py-3 bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 gap-3">
          <div className="flex items-center gap-3">
            <span className="text-xl">📄</span>
            <span className="font-bold text-gray-900 dark:text-white text-sm">
              Recibo Oficial Movistar (3 Páginas)
            </span>
            {/* Page Tabs */}
            <div className="flex bg-gray-200 dark:bg-gray-700 p-0.5 rounded-lg text-xs font-semibold">
              <button
                onClick={() => setActiveTab('p1')}
                className={`px-3 py-1 rounded-md transition-colors ${activeTab === 'p1' ? 'bg-white dark:bg-gray-900 text-[#00A9E0] shadow-sm' : 'text-gray-600 dark:text-gray-300'}`}
              >
                Pág. 1: Resumen
              </button>
              <button
                onClick={() => setActiveTab('p2')}
                className={`px-3 py-1 rounded-md transition-colors ${activeTab === 'p2' ? 'bg-white dark:bg-gray-900 text-[#00A9E0] shadow-sm' : 'text-gray-600 dark:text-gray-300'}`}
              >
                Pág. 2: Detalle
              </button>
              <button
                onClick={() => setActiveTab('p3')}
                className={`px-3 py-1 rounded-md transition-colors ${activeTab === 'p3' ? 'bg-white dark:bg-gray-900 text-[#00A9E0] shadow-sm' : 'text-gray-600 dark:text-gray-300'}`}
              >
                Pág. 3: Información
              </button>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            {onSendEmail && (
              <Button
                size="sm"
                variant="secondary"
                onClick={() => setShowEmailPrompt(!showEmailPrompt)}
                loading={sendingEmail}
              >
                ✉️ Enviar por Correo
              </Button>
            )}
            {onDownloadPdf && (
              <Button size="sm" variant="primary" onClick={onDownloadPdf} loading={downloadingPdf}>
                📥 Descargar PDF
              </Button>
            )}
            {onDownloadXml && (
              <Button size="sm" variant="secondary" onClick={onDownloadXml}>
                📑 XML SUNAT
              </Button>
            )}
            <Button size="sm" variant="secondary" onClick={handlePrint}>
              🖨️ Imprimir
            </Button>
            <button
              onClick={onClose}
              className="p-1.5 text-gray-500 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Email Input Panel Banner */}
        {showEmailPrompt && (
          <div className="print:hidden p-4 bg-sky-50 dark:bg-sky-950/40 border-b border-sky-200 dark:border-sky-800 flex items-center justify-between gap-4">
            <div className="flex-1 flex items-center gap-3">
              <span className="text-sm font-semibold text-sky-900 dark:text-sky-200 whitespace-nowrap">
                Destinatario:
              </span>
              <input
                type="email"
                placeholder={factura.cliente?.email || `pagos@${factura.cliente?.ruc || 'cliente'}.com`}
                value={customEmail}
                onChange={(e) => setCustomEmail(e.target.value)}
                className="w-full max-w-md px-3 py-1.5 text-sm rounded-lg border border-sky-300 dark:border-sky-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-sky-500"
              />
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="primary" onClick={handleSendEmailClick} loading={sendingEmail}>
                🚀 Enviar Recibo Movistar
              </Button>
              <Button size="sm" variant="secondary" onClick={() => setShowEmailPrompt(false)}>
                Cancelar
              </Button>
            </div>
          </div>
        )}

        {/* Printable Document Container */}
        <div className="overflow-y-auto p-6 sm:p-8 bg-white text-gray-900 print:p-0 print:m-0" id="movistar-invoice-printable">
          <div className="max-w-[780px] mx-auto text-sm font-sans space-y-8">
            
            {/* ========================================================= */}
            {/* PÁGINA 1: RESUMEN GENERAL                                 */}
            {/* ========================================================= */}
            <div className={`${activeTab === 'p1' ? 'block' : 'hidden print:block'} space-y-6 print:break-after-page`}>
              {/* Header: Logo Movistar + Client Info + Total Box */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
                <div className="md:col-span-2 space-y-2">
                  <div className="flex items-center gap-2 mb-1">
                    <svg className="w-8 h-8 text-[#00A9E0]" viewBox="0 0 100 100" fill="currentColor">
                      <path d="M15,65 C10,40 30,20 42,42 C50,20 70,20 75,45 C80,20 95,30 90,65 C85,85 70,75 62,55 C55,75 40,75 35,55 C28,75 18,85 15,65 Z" />
                    </svg>
                    <span className="text-lg font-bold text-[#00A9E0] tracking-tight">Movistar Móvil</span>
                  </div>

                  <h2 className="text-2xl font-bold text-[#00A9E0]">
                    Recibo {mesCapitalizado}
                  </h2>

                  <div className="text-xs text-gray-700 space-y-0.5 leading-relaxed pt-1">
                    <p className="font-bold text-gray-900 uppercase">
                      {factura.cliente?.razon_social || 'MARCK ALESSANDRO HERMENEGILDO PACHECO'}
                    </p>
                    <p className="font-medium text-gray-600">
                      DNI / RUC: {factura.cliente?.ruc || '61002639'}
                    </p>
                    <p className="text-gray-600">
                      DIRECCIÓN: {factura.cliente?.direccion || 'CALLE JUAN JOSÉ CRESPO Y CASTILLO 867, URB. RESIDENCIAL EL PORVENIR, TRUJILLO'}
                    </p>
                    <p className="text-gray-600">
                      Cuenta financiera: <span className="font-semibold text-gray-800">{factura.cod_cuenta || '746452202'}</span>
                    </p>
                    <p className="text-gray-600">
                      Teléfonos asociados: <span className="font-semibold text-gray-800">{factura.cod_cliente || '904388543'}</span>
                    </p>
                  </div>
                </div>

                {/* Right Column: Blue Card Total */}
                <div className="bg-[#00A9E0] text-white rounded-2xl p-5 shadow-md flex flex-col justify-between text-center relative overflow-hidden">
                  <div className="space-y-1">
                    <p className="text-xs font-semibold text-white/90 uppercase tracking-wider">Total a pagar</p>
                    <p className="text-3xl font-extrabold tracking-tight">
                      {formatCurrency(total)}
                    </p>
                    <p className="text-xs text-white/90 pt-1">
                      Último día de pago: <span className="font-bold">{formatDayMonth(fechaVto)}</span>
                    </p>
                  </div>
                  <div className="mt-4 bg-white text-[#00A9E0] font-bold text-xs py-1.5 px-3 rounded-lg shadow-sm">
                    Cód. pago: {factura.cliente?.ruc?.slice(0, 9) || '904388543'}
                  </div>
                </div>
              </div>

              {/* Row of 2 Info Boxes: Timeline + Savings */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-[#EBF7FC] p-4 rounded-2xl border border-sky-100 space-y-3">
                  <p className="text-xs font-bold text-gray-800 text-center">
                    Ciclo de facturación - {mesCapitalizado} {anio}
                  </p>
                  <div className="flex justify-between text-xs font-bold text-gray-700 px-2">
                    <span>{formatDayMonth(fechaEmision)}</span>
                    <span>{formatDayMonth(fechaVto)}</span>
                  </div>
                  <div className="relative w-full h-2 bg-sky-200 rounded-full overflow-hidden">
                    <div className="absolute left-0 top-0 h-full bg-[#00A9E0] rounded-full w-3/4"></div>
                  </div>
                  <div className="flex justify-between text-[10px] text-gray-500 px-1">
                    <span>Fecha de Emisión</span>
                    <span>Último día de pago</span>
                  </div>
                </div>

                <div className="bg-[#EBF7FC] p-4 rounded-2xl border border-sky-100 space-y-1.5 flex flex-col justify-center text-center">
                  <p className="text-xs font-extrabold text-gray-900 uppercase tracking-wide">
                    ¡AHORRA!
                  </p>
                  <p className="text-[11px] text-gray-600 leading-snug">
                    ¡Paga tu recibo Movistar de forma digital, evita comisiones y ten más beneficios! Es rápido, fácil y seguro. Ahora puedes pagar con <strong>YAPE, BCP, BBVA</strong>.
                  </p>
                </div>
              </div>

              {/* Resumen Header */}
              <div className="text-center pt-1">
                <h3 className="text-lg font-bold text-[#00A9E0]">
                  Resumen del recibo - Nº {nroRecibo}
                </h3>
              </div>

              {/* Table Conceptos */}
              <div className="border border-gray-200 rounded-2xl overflow-hidden divide-y divide-gray-200 shadow-sm">
                <div className="flex justify-between items-center px-4 py-3 bg-white">
                  <div className="flex items-center gap-2.5">
                    <span className="text-base text-blue-500">🌐</span>
                    <span className="font-semibold text-gray-800">Cargos Mensuales</span>
                  </div>
                  <span className="font-bold text-gray-900">{formatCurrency(total)}</span>
                </div>
                <div className="flex justify-between items-center px-4 py-3 bg-white">
                  <div className="flex items-center gap-2.5">
                    <span className="text-base text-amber-500">🎯</span>
                    <span className="font-semibold text-gray-800">Descuentos y Bonificaciones Inafectos</span>
                  </div>
                  <span className="font-bold text-gray-900">S/ 0.00</span>
                </div>
                <div className="flex justify-between items-center px-4 py-3 bg-white">
                  <div className="flex items-center gap-2.5">
                    <span className="text-base text-rose-500">📄</span>
                    <span className="font-semibold text-gray-800">Redondeo</span>
                  </div>
                  <span className="font-bold text-gray-900">S/ 0.00</span>
                </div>
                <div className="flex justify-between items-center px-4 py-3 bg-white">
                  <span className="font-semibold text-gray-700 pl-8">Devoluciones</span>
                  <span className="font-bold text-gray-900">S/ 0.00</span>
                </div>
                <div className="flex justify-between items-center px-4 py-3 bg-white">
                  <span className="font-semibold text-gray-700 pl-8">Débitos</span>
                  <span className="font-bold text-gray-900">S/ 0.00</span>
                </div>
                <div className="flex justify-between items-center px-4 py-3 bg-white">
                  <span className="font-semibold text-gray-700 pl-8">Deuda pasada</span>
                  <span className="font-bold text-gray-900">S/ 0.00</span>
                </div>
              </div>

              {/* Total Dark Navy */}
              <div className="flex justify-end pt-1">
                <div className="bg-[#0B2742] text-white px-8 py-3.5 rounded-2xl flex items-center gap-8 shadow-md">
                  <span className="font-bold text-base tracking-wide">Total a pagar</span>
                  <span className="font-extrabold text-2xl tracking-tight">
                    {formatCurrency(total)}
                  </span>
                </div>
              </div>

              {/* Foot Banners */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div className="bg-gradient-to-r from-blue-600 to-sky-400 text-white p-4 rounded-2xl flex items-center justify-between shadow-sm">
                  <div>
                    <p className="font-extrabold text-xs tracking-wider">¡REALIZA TUS PAGOS</p>
                    <p className="font-extrabold text-sm tracking-wider">SIN SALIR DE CASA!</p>
                    <p className="text-[10px] text-white/90 pt-1">Yape • Banca por Internet • App Mi Movistar</p>
                  </div>
                  <div className="text-2xl">📱</div>
                </div>
                <div className="bg-[#EBF7FC] p-4 rounded-2xl border border-sky-100 flex items-center text-xs text-gray-700">
                  <p>
                    Paga a tiempo tu recibo y mantente siempre conectado. No esperes hasta el último día de pago.
                  </p>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-3 flex justify-between text-[10px] text-gray-500 font-mono">
                <span>Integratel Perú S.A.A. | R.U.C. 20100017491 | Jr. Domingo Martínez Luján Nº 1130 | Lima - Lima - Surquillo</span>
                <span>Página 1/3</span>
              </div>
            </div>

            {/* ========================================================= */}
            {/* PÁGINA 2: DETALLE DEL RECIBO                              */}
            {/* ========================================================= */}
            <div className={`${activeTab === 'p2' ? 'block' : 'hidden print:block'} space-y-5 print:break-after-page`}>
              <div className="flex items-center gap-2">
                <svg className="w-8 h-8 text-[#00A9E0]" viewBox="0 0 100 100" fill="currentColor">
                  <path d="M15,65 C10,40 30,20 42,42 C50,20 70,20 75,45 C80,20 95,30 90,65 C85,85 70,75 62,55 C55,75 40,75 35,55 C28,75 18,85 15,65 Z" />
                </svg>
                <span className="text-lg font-bold text-[#00A9E0]">Movistar Móvil</span>
              </div>

              <div className="text-center">
                <h3 className="text-lg font-bold text-[#00A9E0]">
                  Detalle del recibo - Nº {nroRecibo}
                </h3>
              </div>

              {/* Block 1: Cargos Mensuales */}
              <div className="border border-gray-200 rounded-2xl p-4 space-y-2 shadow-sm">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2 font-bold text-gray-900 text-sm">
                    <span className="text-blue-500">🌐</span> Cargos Mensuales
                  </div>
                  <div className="flex gap-8 text-xs font-semibold text-gray-600">
                    <span>Precio de vta.</span>
                    <span>IGV</span>
                    <span className="font-bold text-gray-900 text-sm">{formatCurrency(total)}</span>
                  </div>
                </div>
                <div className="flex justify-between items-center text-xs text-gray-700 pt-1 pl-6">
                  <span>RV Plan Adicional S/{total.toFixed(1)} II ({formatDayMonth(fechaEmision)} al {formatDayMonth(fechaVto)})</span>
                  <div className="flex gap-12 font-mono">
                    <span>{subtotal.toFixed(2)}</span>
                    <span>{igv.toFixed(2)}</span>
                    <span className="font-bold">{total.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              {/* Block 2: Descuentos */}
              <div className="border border-gray-200 rounded-2xl p-4 space-y-3 shadow-sm">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2 font-bold text-gray-900 text-sm">
                    <span className="text-amber-500">🎯</span> Descuentos y Bonificaciones Inafectos
                  </div>
                  <div className="flex gap-8 text-xs font-semibold text-gray-600">
                    <span>Precio de vta.</span>
                    <span>IGV</span>
                    <span className="font-bold text-gray-900 text-sm">S/ 0.00</span>
                  </div>
                </div>
                <div className="space-y-1.5 text-xs text-gray-700 pl-6">
                  <div className="flex justify-between items-center">
                    <span>Bonificacion Ilim Linea Adic 39.9 I (VR S/60.30)</span>
                    <div className="flex gap-14 font-mono">
                      <span>0.00</span>
                      <span>0.00</span>
                      <span>0.00</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Bonificacion Nuevo Cliente 100GB (VR S/63.65)</span>
                    <div className="flex gap-14 font-mono">
                      <span>0.00</span>
                      <span>0.00</span>
                      <span>0.00</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Block 3: Redondeo */}
              <div className="border border-gray-200 rounded-2xl p-4 space-y-3 shadow-sm">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2 font-bold text-gray-900 text-sm">
                    <span className="text-rose-500">📄</span> Redondeo
                  </div>
                  <div className="flex gap-8 text-xs font-semibold text-gray-600">
                    <span>Precio de vta.</span>
                    <span>IGV</span>
                    <span className="font-bold text-gray-900 text-sm">S/ 0.00</span>
                  </div>
                </div>
                <div className="space-y-1.5 text-xs text-gray-700 pl-6">
                  <div className="flex justify-between items-center">
                    <span>Redondeo del mes Actual</span>
                    <div className="flex gap-14 font-mono">
                      <span>-0.08</span>
                      <span>0.00</span>
                      <span>-0.08</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Redondeo del mes Anterior</span>
                    <div className="flex gap-14 font-mono">
                      <span>0.08</span>
                      <span>0.00</span>
                      <span>0.08</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Subtotal & IGV Summary Boxes */}
              <div className="flex flex-col items-end space-y-2 pt-2">
                <div className="bg-[#EBF7FC] w-64 px-4 py-2 rounded-xl flex justify-between items-center text-xs">
                  <span className="font-bold text-gray-800">Subtotal</span>
                  <span className="font-bold text-gray-900">{formatCurrency(subtotal)}</span>
                </div>
                <div className="bg-[#EBF7FC] w-64 px-4 py-2 rounded-xl flex justify-between items-center text-xs">
                  <span className="font-bold text-gray-800">IGV (18%)</span>
                  <span className="font-bold text-gray-900">{formatCurrency(igv)}</span>
                </div>
                <div className="bg-[#BAE6FD] w-64 px-4 py-2.5 rounded-xl flex justify-between items-center text-sm">
                  <span className="font-extrabold text-gray-900">Total facturado</span>
                  <span className="font-extrabold text-gray-900">{formatCurrency(total)}</span>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-3 flex justify-between text-[10px] text-gray-500 font-mono">
                <span>Integratel Perú S.A.A. | R.U.C. 20100017491 | Jr. Domingo Martínez Luján Nº 1130 | Lima - Lima - Surquillo</span>
                <span>Página 2/3</span>
              </div>
            </div>

            {/* ========================================================= */}
            {/* PÁGINA 3: INFORMACIÓN Y LUGARES DE PAGO                   */}
            {/* ========================================================= */}
            <div className={`${activeTab === 'p3' ? 'block' : 'hidden print:block'} space-y-5`}>
              {/* Section 1: Conceptos Facturables */}
              <div>
                <div className="bg-[#00A9E0] text-white font-bold text-xs py-2 px-4 rounded-t-xl text-center">
                  Conceptos facturables
                </div>
                <div className="bg-[#EBF7FC] p-4 rounded-b-xl grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-gray-700">
                  <div className="space-y-3">
                    <div>
                      <p className="font-bold text-gray-900 mb-0.5">Cargos fijos mensuales</p>
                      <p className="text-[11px] text-gray-600 leading-snug">
                        Cargo mensual facturado al cliente por el plan contratado para los servicios de voz y datos. Cargo fijo proporcional del plan desde la fecha de inicio del servicio hasta el siguiente cierre de facturación.
                      </p>
                    </div>
                    <div>
                      <p className="font-bold text-gray-900 mb-0.5">Cargos por llamadas adicionales</p>
                      <p className="text-[11px] text-gray-600 leading-snug">
                        Cargos por tráfico de voz, datos, mensajes de texto que no se encuentran comprendidos dentro del cargo fijo mensual. Larga distancia nacional e internacional. KB internet y navegación. Roaming internacional.
                      </p>
                    </div>
                  </div>

                  <div>
                    <p className="font-bold text-gray-900 mb-0.5">Detalle de documentos afectos al IGV</p>
                    <p className="text-[11px] text-gray-600 leading-snug">
                      Cargo por Reconexión: cargo facturado si el cliente cancela un recibo después de habérsele cortado por deuda.<br/>
                      Cargo por Reconexión de corte APC (a pedido de cliente).<br/>
                      Cargo por llamadas a operadoras rurales: Gilat, Valtron, Claro Rural, Integratel Rural o satelitales como Tesam.<br/>
                      Renta fraccionaria por cambio de plan tarifario.
                    </p>
                  </div>
                </div>
              </div>

              {/* Section 2: Lugares de Pago */}
              <div>
                <div className="bg-[#00A9E0] text-white font-bold text-xs py-2 px-4 rounded-t-xl text-center">
                  Lugares de pago
                </div>
                <div className="bg-[#EBF7FC] p-4 rounded-b-xl space-y-4 text-xs">
                  <div className="grid grid-cols-3 gap-3 text-gray-700">
                    <div>
                      <p className="font-bold text-gray-900 mb-1">Bancos y agentes</p>
                      <p className="text-[11px] text-gray-600 leading-tight">
                        BBVA Continental<br/>Banco Pichincha<br/>BCP<br/>Banco de la Nación<br/>BanBif<br/>Interbank<br/>Scotiabank
                      </p>
                    </div>
                    <div>
                      <p className="font-bold text-gray-900 mb-1">Otros</p>
                      <p className="text-[11px] text-gray-600 leading-tight">
                        Agente KASNET<br/>Multibanco<br/>Fullcarga<br/>Red Digital
                      </p>
                    </div>
                    <div>
                      <p className="text-[11px] text-gray-600 leading-tight pt-4">
                        Metro<br/>Wong<br/>Western Union
                      </p>
                    </div>
                  </div>

                  <div className="text-[11px] text-gray-600 space-y-1">
                    <p>Algunos lugares de pago presenciales pueden aplicar cobro de comisión de acuerdo a sus tarifarios vigentes.</p>
                    <p>Puede realizar su pago de forma rápida y segura en el App Mi Movistar, YAPE o App / Web de su banco.</p>
                    <p>Recuerda que también puede afiliar su recibo al débito automático en http://smvst.com/DAT</p>
                  </div>

                  <div className="bg-[#BAE6FD] py-1.5 px-3 rounded-lg text-center font-bold text-xs text-gray-900">
                    Mayor información sobre lugares de pago en www.movistar.com.pe
                  </div>
                </div>
              </div>

              {/* Section 3: ¿Qué es el recibo digital? */}
              <div>
                <div className="bg-[#00A9E0] text-white font-bold text-xs py-2 px-4 rounded-t-xl text-center">
                  ¿Qué es el recibo digital?
                </div>
                <div className="bg-[#EBF7FC] p-4 rounded-b-xl flex items-center gap-3 text-xs text-gray-700">
                  <span className="text-2xl text-[#00A9E0]">📄</span>
                  <p className="text-[11px] leading-snug">
                    Es un servicio gratuito que ofrece Integratel, con el que podrá recibir mensualmente su recibo en formato PDF al correo electrónico que usted indique. El envío del recibo digital va en reemplazo de su recibo físico.
                  </p>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-3 flex justify-between text-[10px] text-gray-500 font-mono">
                <span>Integratel Perú S.A.A. | R.U.C. 20100017491 | Jr. Domingo Martínez Luján Nº 1130 | Lima - Lima - Surquillo</span>
                <span>Página 3/3</span>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
};

export default MovistarInvoiceModal;
