"""
Generador de Recibos y Facturas en PDF con Diseño Corporativo Oficial Movistar (3 Páginas)
========================================================================================
Genera un documento PDF A4 de 3 páginas de alta fidelidad visual basado en la plantilla oficial Movistar:
- Página 1: Resumen del recibo y datos principales.
- Página 2: Detalle del recibo por conceptos, precio de venta, IGV y subtotal.
- Página 3: Conceptos facturables, Lugares de pago y Recibo digital.
"""

import io
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Optional
import structlog

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from app.database.models import BSSFactura, BSSCliente

logger = structlog.get_logger(__name__)

# Paleta Corporativa Movistar
COLOR_MOVISTAR_CYAN = colors.HexColor("#00A9E0")
COLOR_MOVISTAR_NAVY = colors.HexColor("#0B2742")
COLOR_SOFT_BG = colors.HexColor("#EBF7FC")
COLOR_BORDER = colors.HexColor("#E2E8F0")
COLOR_TEXT_MAIN = colors.HexColor("#0F172A")
COLOR_TEXT_MUTED = colors.HexColor("#475569")
COLOR_SUBTOTAL_BG = colors.HexColor("#E0F2FE")


class MovistarPdfGenerator:
    """Generador PDF de 3 Páginas de Recibos Movistar / Integratel"""

    def generar_pdf_recibo(
        self,
        factura: BSSFactura,
        cliente: BSSCliente,
    ) -> bytes:
        """Genera el binario PDF de 3 páginas en memoria del recibo oficial Movistar"""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        page_w, page_h = A4  # 595.27 x 841.89

        # Fechas
        f_emision = factura.fecha_emision or date.today()
        f_vto = factura.fecha_vto or date.today()
        
        meses_es = {
            "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
            "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
            "September": "Setiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
        }
        mes_es = meses_es.get(f_emision.strftime("%B"), f_emision.strftime("%B"))
        anio = f_emision.year

        monto_neto = float(factura.charge_net_amount or 33.81)
        igv = float(factura.charge_igv_invoice or 6.09)
        monto_total = float(factura.charge_total_amount or 39.90)
        nro_recibo = factura.nro_doc_fiscal or "S1AA-0053100009"

        m_left = 40
        m_right = page_w - 40

        def draw_legal_footer(page_num: int):
            c.setStrokeColor(COLOR_BORDER)
            c.line(m_left, 35, m_right, 35)
            c.setFillColor(COLOR_TEXT_MUTED)
            c.setFont("Helvetica", 6.5)
            c.drawString(m_left, 24, "Integratel Perú S.A.A. | R.U.C. 20100017491 | Jr. Domingo Martínez Luján Nº 1130 | Lima - Lima - Surquillo")
            c.drawRightString(m_right, 24, f"Página {page_num}/3")

        # =========================================================================
        # PÁGINA 1: RESUMEN DEL RECIBO
        # =========================================================================
        y = page_h - 45

        # Logo Movistar Cyan
        c.setFillColor(COLOR_MOVISTAR_CYAN)
        c.roundRect(m_left, y - 16, 20, 20, 4, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(m_left + 4, y - 12, "M")

        c.setFillColor(COLOR_MOVISTAR_CYAN)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(m_left + 26, y - 10, "Movistar Móvil")

        y -= 38
        c.setFont("Helvetica-Bold", 20)
        c.drawString(m_left, y, f"Recibo {mes_es}")

        y -= 22

        # Card Superior Derecha: Total a Pagar
        box_w = 175
        box_h = 100
        box_x = m_right - box_w
        box_y = y - 75

        c.setFillColor(COLOR_MOVISTAR_CYAN)
        c.roundRect(box_x, box_y, box_w, box_h, 12, stroke=0, fill=1)

        c.setFillColor(colors.white)
        c.setFont("Helvetica", 9)
        c.drawCentredString(box_x + (box_w / 2), box_y + box_h - 18, "Total a pagar")

        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(box_x + (box_w / 2), box_y + box_h - 44, f"S/{monto_total:,.2f}")

        c.setFont("Helvetica", 8.5)
        c.drawCentredString(box_x + (box_w / 2), box_y + box_h - 60, f"Último día de pago: {f_vto.strftime('%d/%m')}")

        pill_w = 145
        pill_h = 20
        pill_x = box_x + (box_w - pill_w) / 2
        pill_y = box_y + 10
        c.setFillColor(colors.white)
        c.roundRect(pill_x, pill_y, pill_w, pill_h, 6, stroke=0, fill=1)

        c.setFillColor(COLOR_MOVISTAR_CYAN)
        c.setFont("Helvetica-Bold", 8.5)
        cod_pago = (cliente.numero_identificacion_fiscal or "904388543")[:10]
        c.drawCentredString(box_x + (box_w / 2), pill_y + 6, f"Cód. pago: {cod_pago}")

        # Datos del Cliente
        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(m_left, y, (cliente.razon_social or "MARCK ALESSANDRO HERMENEGILDO PACHECO").upper()[:45])
        
        y -= 13
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 8.5)
        c.drawString(m_left, y, f"DNI / RUC: {cliente.numero_identificacion_fiscal or '61002639'}")

        y -= 12
        direccion = f"{cliente.sunat_departamento or 'CALLE JUAN JOSÉ CRESPO Y CASTILLO 867'}, {cliente.sunat_provincia or 'TRUJILLO'}"
        c.drawString(m_left, y, f"DIRECCIÓN: {direccion[:50].upper()}")

        y -= 12
        c.drawString(m_left, y, f"Cuenta financiera: {factura.cod_cuenta or '746452202'}")

        y -= 12
        c.drawString(m_left, y, f"Teléfonos asociados: {factura.cod_cliente or cliente.numero_celular or '904388543'}")

        y = box_y - 20

        # Cajas: Ciclo de Facturación + Ahorra
        half_w = (m_right - m_left - 12) / 2
        box_info_h = 68

        c.setFillColor(COLOR_SOFT_BG)
        c.roundRect(m_left, y - box_info_h, half_w, box_info_h, 10, stroke=0, fill=1)

        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(m_left + half_w / 2, y - 14, f"Ciclo de facturación - {mes_es} {anio}")

        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(m_left + 20, y - 30, f"{f_emision.strftime('%d/%m')}")
        c.drawRightString(m_left + half_w - 20, y - 30, f"{f_vto.strftime('%d/%m')}")

        c.setFillColor(colors.HexColor("#BAE6FD"))
        c.roundRect(m_left + 20, y - 42, half_w - 40, 5, 2.5, stroke=0, fill=1)
        c.setFillColor(COLOR_MOVISTAR_CYAN)
        c.roundRect(m_left + 20, y - 42, (half_w - 40) * 0.75, 5, 2.5, stroke=0, fill=1)

        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 7.5)
        c.drawString(m_left + 15, y - 56, "Fecha de Emisión")
        c.drawRightString(m_left + half_w - 15, y - 56, "Último día de pago")

        c.setFillColor(COLOR_SOFT_BG)
        c.roundRect(m_left + half_w + 12, y - box_info_h, half_w, box_info_h, 10, stroke=0, fill=1)

        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(m_left + half_w + 12 + half_w / 2, y - 16, "¡AHORRA!")

        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(m_left + half_w + 12 + half_w / 2, y - 30, "¡Paga tu recibo Movistar de forma digital, evita comisiones")
        c.drawCentredString(m_left + half_w + 12 + half_w / 2, y - 42, "y ten más beneficios! Es rápido, fácil y seguro. Ahora")
        c.drawCentredString(m_left + half_w + 12 + half_w / 2, y - 54, "puedes pagar con YAPE, BCP y BBVA.")

        y -= (box_info_h + 24)

        # Resumen del Recibo
        c.setFillColor(COLOR_MOVISTAR_CYAN)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(page_w / 2, y, f"Resumen del recibo - Nº {nro_recibo}")

        y -= 16
        table_w = m_right - m_left
        table_h = 160
        table_y = y - table_h

        c.setStrokeColor(COLOR_BORDER)
        c.setLineWidth(1)
        c.roundRect(m_left, table_y, table_w, table_h, 10, stroke=1, fill=0)

        filas_p1 = [
            ("🌐  Cargos Mensuales", f"S/ {monto_total:,.2f}", True),
            ("🎯  Descuentos y Bonificaciones Inafectos", "S/ 0.00", False),
            ("📄  Redondeo", "S/ 0.00", False),
            ("     Devoluciones", "S/ 0.00", False),
            ("     Débitos", "S/ 0.00", False),
            ("     Deuda pasada", "S/ 0.00", False),
        ]

        row_h = table_h / len(filas_p1)
        cur_y = y - row_h + 4

        for i, (concepto, monto_str, es_bold) in enumerate(filas_p1):
            if i > 0:
                c.setStrokeColor(COLOR_BORDER)
                c.line(m_left, cur_y + row_h - 4, m_right, cur_y + row_h - 4)

            c.setFillColor(COLOR_TEXT_MAIN if es_bold else COLOR_TEXT_MUTED)
            c.setFont("Helvetica-Bold" if es_bold else "Helvetica", 9)
            c.drawString(m_left + 16, cur_y + 6, concepto)

            c.setFont("Helvetica-Bold", 9.5)
            c.drawRightString(m_right - 16, cur_y + 6, monto_str)
            cur_y -= row_h

        y = table_y - 18

        # Total Box Navy
        navy_box_w = 210
        navy_box_h = 32
        navy_x = m_right - navy_box_w

        c.setFillColor(COLOR_MOVISTAR_NAVY)
        c.roundRect(navy_x, y - navy_box_h, navy_box_w, navy_box_h, 8, stroke=0, fill=1)

        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(navy_x + 16, y - navy_box_h + 11, "Total a pagar")
        c.setFont("Helvetica-Bold", 13)
        c.drawRightString(navy_x + navy_box_w - 16, y - navy_box_h + 10, f"S/ {monto_total:,.2f}")

        y -= (navy_box_h + 30)

        # Footer Banners
        banner_h = 55
        c.setFillColor(COLOR_MOVISTAR_CYAN)
        c.roundRect(m_left, y - banner_h, half_w, banner_h, 10, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(m_left + 14, y - 18, "¡REALIZA TUS PAGOS")
        c.drawString(m_left + 14, y - 29, "SIN SALIR DE CASA!")
        c.setFont("Helvetica", 7.5)
        c.drawString(m_left + 14, y - 44, "App Mi Movistar • Web • Yape • Banca Móvil")

        c.setFillColor(COLOR_SOFT_BG)
        c.roundRect(m_left + half_w + 12, y - banner_h, half_w, banner_h, 10, stroke=0, fill=1)
        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica", 8)
        c.drawString(m_left + half_w + 24, y - 24, "Paga a tiempo tu recibo y mantente")
        c.drawString(m_left + half_w + 24, y - 36, "siempre conectado. No esperes hasta")
        c.drawString(m_left + half_w + 24, y - 48, "el último día de pago.")

        draw_legal_footer(1)
        c.showPage()

        # =========================================================================
        # PÁGINA 2: DETALLE DEL RECIBO
        # =========================================================================
        y = page_h - 45

        # Logo Movistar
        c.setFillColor(COLOR_MOVISTAR_CYAN)
        c.roundRect(m_left, y - 16, 20, 20, 4, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(m_left + 4, y - 12, "M")

        c.setFillColor(COLOR_MOVISTAR_CYAN)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(m_left + 26, y - 10, "Movistar Móvil")

        y -= 38
        # Título: Detalle del recibo - Nº [Nro]
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(page_w / 2, y, f"Detalle del recibo - Nº {nro_recibo}")

        y -= 25

        # Bloque 1: Cargos Mensuales
        block1_h = 56
        c.setStrokeColor(COLOR_BORDER)
        c.roundRect(m_left, y - block1_h, page_w - 80, block1_h, 8, stroke=1, fill=0)

        # Header Categoría
        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(m_left + 16, y - 20, "🌐  Cargos Mensuales")

        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 8.5)
        c.drawRightString(m_right - 140, y - 20, "Precio de vta.")
        c.drawRightString(m_right - 80, y - 20, "IGV")
        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawRightString(m_right - 16, y - 20, f"S/{monto_total:,.2f}")

        # Sub-item 1
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 8.5)
        c.drawString(m_left + 36, y - 40, f"RV Plan Adicional S/{monto_total:.1f} II ({f_emision.strftime('%d%b')} al {f_vto.strftime('%d%b')})")
        c.drawRightString(m_right - 140, y - 40, f"{monto_neto:,.2f}")
        c.drawRightString(m_right - 80, y - 40, f"{igv:,.2f}")
        c.drawRightString(m_right - 16, y - 40, f"{monto_total:,.2f}")

        y -= (block1_h + 14)

        # Bloque 2: Descuentos y Bonificaciones Inafectos
        block2_h = 82
        c.setStrokeColor(COLOR_BORDER)
        c.roundRect(m_left, y - block2_h, page_w - 80, block2_h, 8, stroke=1, fill=0)

        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(m_left + 16, y - 20, "🎯  Descuentos y Bonificaciones Inafectos")

        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 8.5)
        c.drawRightString(m_right - 140, y - 20, "Precio de vta.")
        c.drawRightString(m_right - 80, y - 20, "IGV")
        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawRightString(m_right - 16, y - 20, "S/0.00")

        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 8)
        c.drawString(m_left + 36, y - 40, "Bonificacion Ilim Linea Adic 39.9 I (VR S/60.30)")
        c.drawRightString(m_right - 140, y - 40, "0.00")
        c.drawRightString(m_right - 80, y - 40, "0.00")
        c.drawRightString(m_right - 16, y - 40, "0.00")

        c.drawString(m_left + 36, y - 60, "Bonificacion Nuevo Cliente 100GB (VR S/63.65)")
        c.drawRightString(m_right - 140, y - 60, "0.00")
        c.drawRightString(m_right - 80, y - 60, "0.00")
        c.drawRightString(m_right - 16, y - 60, "0.00")

        y -= (block2_h + 14)

        # Bloque 3: Redondeo
        block3_h = 82
        c.setStrokeColor(COLOR_BORDER)
        c.roundRect(m_left, y - block3_h, page_w - 80, block3_h, 8, stroke=1, fill=0)

        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(m_left + 16, y - 20, "📄  Redondeo")

        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 8.5)
        c.drawRightString(m_right - 140, y - 20, "Precio de vta.")
        c.drawRightString(m_right - 80, y - 20, "IGV")
        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawRightString(m_right - 16, y - 20, "S/0.00")

        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 8)
        c.drawString(m_left + 36, y - 40, "Redondeo del mes Actual")
        c.drawRightString(m_right - 140, y - 40, "-0.08")
        c.drawRightString(m_right - 80, y - 40, "0.00")
        c.drawRightString(m_right - 16, y - 40, "-0.08")

        c.drawString(m_left + 36, y - 60, "Redondeo del mes Anterior")
        c.drawRightString(m_right - 140, y - 60, "0.08")
        c.drawRightString(m_right - 80, y - 60, "0.00")
        c.drawRightString(m_right - 16, y - 60, "0.08")

        y -= (block3_h + 24)

        # Resumen Inferior de Totales (Subtotal, IGV, Total Facturado)
        summary_box_w = 210
        summary_box_x = m_right - summary_box_w

        # Subtotal Box
        c.setFillColor(COLOR_SUBTOTAL_BG)
        c.roundRect(summary_box_x, y - 26, summary_box_w, 26, 6, stroke=0, fill=1)
        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(summary_box_x + 14, y - 18, "Subtotal")
        c.drawRightString(summary_box_x + summary_box_w - 14, y - 18, f"S/{monto_neto:,.2f}")

        y -= 34

        # IGV Box
        c.setFillColor(COLOR_SUBTOTAL_BG)
        c.roundRect(summary_box_x, y - 26, summary_box_w, 26, 6, stroke=0, fill=1)
        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(summary_box_x + 14, y - 18, "IGV (18%)")
        c.drawRightString(summary_box_x + summary_box_w - 14, y - 18, f"S/{igv:,.2f}")

        y -= 34

        # Total Facturado Box
        c.setFillColor(COLOR_SUBTOTAL_BG)
        c.roundRect(summary_box_x, y - 28, summary_box_w, 28, 6, stroke=0, fill=1)
        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(summary_box_x + 14, y - 19, "Total facturado")
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(summary_box_x + summary_box_w - 14, y - 19, f"S/{monto_total:,.2f}")

        draw_legal_footer(2)
        c.showPage()

        # =========================================================================
        # PÁGINA 3: INFORMACIÓN AL CLIENTE Y LUGARES DE PAGO
        # =========================================================================
        y = page_h - 45

        # ---------------- Section 1: Conceptos Facturables ----------------
        header_bar_h = 24
        c.setFillColor(COLOR_MOVISTAR_CYAN)
        c.roundRect(m_left, y - header_bar_h, page_w - 80, header_bar_h, 6, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(page_w / 2, y - 16, "Conceptos facturables")

        y -= (header_bar_h + 4)

        sec1_box_h = 150
        c.setFillColor(COLOR_SOFT_BG)
        c.roundRect(m_left, y - sec1_box_h, page_w - 80, sec1_box_h, 8, stroke=0, fill=1)

        # Columna 1
        col1_x = m_left + 16
        col1_w = (page_w - 80) / 2 - 20
        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(col1_x, y - 18, "Cargos fijos mensuales")

        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 7.5)
        c.drawString(col1_x, y - 30, "Cargo mensual facturado al cliente por el plan contratado")
        c.drawString(col1_x, y - 40, "para los servicios de voz y datos. Cargo fijo proporcional")
        c.drawString(col1_x, y - 50, "del plan desde la fecha de inicio del servicio hasta el")
        c.drawString(col1_x, y - 60, "siguiente cierre de facturación.")

        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(col1_x, y - 76, "Cargos por llamadas adicionales")

        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 7.5)
        c.drawString(col1_x, y - 88, "Cargos por tráfico de voz, datos, mensajes de texto que")
        c.drawString(col1_x, y - 98, "no se encuentran comprendidos dentro del cargo fijo mensual.")
        c.drawString(col1_x, y - 108, "Larga distancia: llamadas nacionales e internacionales.")
        c.drawString(col1_x, y - 118, "KB internet y multimedia: navegación y aplicativos.")
        c.drawString(col1_x, y - 128, "Roaming internacional: llamadas y datos en el extranjero.")

        # Columna 2
        col2_x = m_left + (page_w - 80) / 2 + 10
        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(col2_x, y - 18, "Detalle de documentos afectos al IGV")

        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 7.5)
        c.drawString(col2_x, y - 30, "Cargo por Reconexión: cargo aplicado si el cliente")
        c.drawString(col2_x, y - 40, "cancela su recibo después de corte por deuda.")
        c.drawString(col2_x, y - 50, "Cargo por Reconexión de corte APC (a pedido de cliente).")
        c.drawString(col2_x, y - 60, "Llamadas a operadoras rurales: Gilat, Valtron, Claro")
        c.drawString(col2_x, y - 70, "Rural, Integratel Rural o satelitales como Tesam.")
        c.drawString(col2_x, y - 80, "Renta fraccionaria por cambio de plan tarifario.")

        y -= (sec1_box_h + 16)

        # ---------------- Section 2: Lugares de Pago ----------------
        c.setFillColor(COLOR_MOVISTAR_CYAN)
        c.roundRect(m_left, y - header_bar_h, page_w - 80, header_bar_h, 6, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(page_w / 2, y - 16, "Lugares de pago")

        y -= (header_bar_h + 4)

        sec2_box_h = 240
        c.setFillColor(COLOR_SOFT_BG)
        c.roundRect(m_left, y - sec2_box_h, page_w - 80, sec2_box_h, 8, stroke=0, fill=1)

        # 3 Columnas de Bancos / Comercios
        col_w = (page_w - 80 - 40) / 3

        # Col 1: Bancos y Agentes
        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(m_left + 16, y - 20, "Bancos y agentes")

        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 8)
        bancos = ["BBVA Continental", "Banco Pichincha", "BCP", "Banco de la Nación", "BanBif", "Interbank", "Scotiabank"]
        cur_banco_y = y - 36
        for b in bancos:
            c.drawString(m_left + 16, cur_banco_y, b)
            cur_banco_y -= 12

        # Col 2: Otros
        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(m_left + 16 + col_w, y - 20, "Otros")

        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 8)
        otros = ["Agente Multibanco KASNET", "Multibanco", "Fullcarga", "Red Digital"]
        cur_otro_y = y - 36
        for o in otros:
            c.drawString(m_left + 16 + col_w, cur_otro_y, o)
            cur_otro_y -= 12

        # Col 3: Comercios
        c.drawString(m_left + 16 + (col_w * 2), y - 36, "Metro")
        c.drawString(m_left + 16 + (col_w * 2), y - 48, "Wong")
        c.drawString(m_left + 16 + (col_w * 2), y - 60, "Western Union")

        # Texto informativo
        info_y = y - 130
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 7.5)
        c.drawString(m_left + 16, info_y, "Algunos lugares de pago presenciales pueden aplicar cobro de comisión de acuerdo a sus tarifarios vigentes.")
        c.drawString(m_left + 16, info_y - 12, "Puede realizar su pago de forma rápida y segura en el App Mi Movistar, YAPE o App / Web de su banco.")
        c.drawString(m_left + 16, info_y - 28, "Recuerda que también puede afiliar su recibo Movistar al débito automático, más info: http://smvst.com/DAT")

        # Sub-banner interior azul
        c.setFillColor(colors.HexColor("#BAE6FD"))
        c.roundRect(m_left + 16, info_y - 65, page_w - 80 - 32, 22, 5, stroke=0, fill=1)
        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(page_w / 2, info_y - 58, "Mayor información sobre lugares de pago en www.movistar.com.pe")

        y -= (sec2_box_h + 16)

        # ---------------- Section 3: ¿Qué es el recibo digital? ----------------
        c.setFillColor(COLOR_MOVISTAR_CYAN)
        c.roundRect(m_left, y - header_bar_h, page_w - 80, header_bar_h, 6, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(page_w / 2, y - 16, "¿Qué es el recibo digital?")

        y -= (header_bar_h + 4)

        sec3_box_h = 55
        c.setFillColor(COLOR_SOFT_BG)
        c.roundRect(m_left, y - sec3_box_h, page_w - 80, sec3_box_h, 8, stroke=0, fill=1)

        # Icono Digital
        c.setFillColor(COLOR_MOVISTAR_CYAN)
        c.circle(m_left + 30, y - 28, 14, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(m_left + 26, y - 32, "📄")

        # Texto Recibo Digital
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica", 8)
        c.drawString(m_left + 54, y - 22, "Es un servicio gratuito que ofrece Integratel, con el que podrá recibir mensualmente su recibo en formato PDF")
        c.drawString(m_left + 54, y - 34, "al correo electrónico que usted indique. El envío del recibo digital va en reemplazo de su recibo físico.")

        draw_legal_footer(3)
        c.showPage()

        c.save()
        buffer.seek(0)
        return buffer.getvalue()


# Singleton
pdf_generator = MovistarPdfGenerator()
