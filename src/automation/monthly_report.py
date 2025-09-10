#!/usr/bin/env python3
"""
Automatización de análisis mensual de inversiones
Genera reporte mensual automático del mercado de acciones chileno
"""

import os
import sys
import smtplib
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd

# Importaciones para PDF
from fpdf import FPDF
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importar módulos locales
from analysis.investment_analyzer import InvestmentAnalyzer
from analysis.report_generator import generate_investment_report
from utils.config import get_config


def is_first_business_day():
    """Verifica si hoy es el primer día hábil del mes"""
    today = datetime.now().date()
    
    # Obtener el primer día del mes
    first_day = today.replace(day=1)
    
    # Encontrar el primer día hábil (lunes a viernes)
    while first_day.weekday() > 4:  # 0=lunes, 6=domingo
        first_day += timedelta(days=1)
    
    return today == first_day


def run_monthly_analysis():
    """Ejecuta análisis mensual completo"""
    print(f"🚀 Iniciando análisis mensual - {datetime.now()}")
    
    try:
        # Configuración predeterminada
        config = {
            'budget': 200000,  # 200 mil CLP
            'risk_level': 'moderado',
            'dividend_preference': True
        }
        
        # Ejecutar análisis
        analyzer = InvestmentAnalyzer()
        result = analyzer.run_complete_analysis_with_gpt(
            budget=config['budget'],
            risk_level=config['risk_level'],
            dividend_preference=config['dividend_preference']
        )
        
        print(f"✅ Análisis completado. Empresas analizadas: {result['market_summary']['total_empresas']}")
        print(f"📊 Recomendaciones generadas: {result['recommendations']['empresas_recomendadas']}")
        
        return result, config
        
    except Exception as e:
        print(f"❌ Error en análisis: {str(e)}")
        raise


def generate_monthly_report_pdf(result, config):
    """Genera reporte mensual en formato PDF profesional"""
    print("📄 Generando reporte PDF profesional...")
    
    try:
        # Asegurar que existe el directorio outputs/reports
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'outputs', 'reports')
        os.makedirs(output_dir, exist_ok=True)
        
        # Nombre del archivo PDF con ruta completa
        pdf_filename = f"reporte_mensual_{datetime.now().strftime('%Y_%m')}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        # Crear documento PDF
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=20,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Centrado
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkred,
            leftIndent=0
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=10
        )
        
        # Contenido del documento
        story = []
        
        # Título principal
        title = "REPORTE MENSUAL DE INVERSION"
        subtitle = f"{datetime.now().strftime('%B %Y').upper()}"
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(subtitle, title_style))
        story.append(Spacer(1, 20))
        
        # Resumen ejecutivo
        story.append(Paragraph("RESUMEN EJECUTIVO", heading_style))
        
        # Crear párrafos separados para mejor renderizado
        story.append(Paragraph(f"<b>Fecha del analisis:</b> {datetime.now().strftime('%d/%m/%Y')}", normal_style))
        story.append(Paragraph(f"<b>Presupuesto analizado:</b> ${config['budget']:,} CLP", normal_style))
        story.append(Paragraph(f"<b>Perfil de riesgo:</b> {config['risk_level'].title()}", normal_style))
        story.append(Paragraph(f"<b>Total de empresas analizadas:</b> {result['market_summary']['total_empresas']}", normal_style))
        story.append(Paragraph(f"<b>Empresas recomendadas:</b> {result['recommendations']['empresas_recomendadas']}", normal_style))
        story.append(Spacer(1, 15))
        
        # Análisis con IA
        story.append(Paragraph("ANALISIS INTELIGENTE", heading_style))
        
        if 'gpt_analysis' in result and result['gpt_analysis']:
            # Procesar y dividir el contenido en párrafos separados
            gpt_text = result['gpt_analysis']
            # Limpiar markdown y emojis
            gpt_text = gpt_text.replace('### ', '').replace('##', '').replace('#', '')
            gpt_text = gpt_text.replace('📊', '').replace('📈', '').replace('💹', '')
            gpt_text = gpt_text.replace('�', '').replace('⚖️', '').replace('💎', '')
            gpt_text = gpt_text.replace('🎯', '').replace('*', '').replace('**', '')
            
            # Dividir en líneas y procesar cada una
            lines = gpt_text.split('\n')
            clean_lines = []
            for line in lines:
                line = line.strip()
                if line and len(line) > 3:  # Solo líneas con contenido
                    clean_lines.append(line)
            
            # Crear párrafo de análisis IA
            story.append(Paragraph("<b>ANALISIS REALIZADO CON INTELIGENCIA ARTIFICIAL</b>", normal_style))
            story.append(Spacer(1, 8))
            
            # Agregar cada línea como párrafo separado
            for line in clean_lines[:8]:  # Limitar a 8 líneas principales
                if line:
                    story.append(Paragraph(line, normal_style))
                    story.append(Spacer(1, 4))
            
            # Distribución
            gpt_dist = result['gpt_distribution']
            gpt_dist = gpt_dist.replace('### ', '').replace('##', '').replace('#', '')
            gpt_dist = gpt_dist.replace('*', '')
            
            story.append(Spacer(1, 10))
            story.append(Paragraph("<b>DISTRIBUCION RECOMENDADA POR IA:</b>", normal_style))
            story.append(Spacer(1, 6))
            
            dist_lines = gpt_dist.split('\n')
            for line in dist_lines[:6]:  # Primeras 6 líneas de distribución
                line = line.strip()
                if line and len(line) > 2:
                    story.append(Paragraph(line, normal_style))
                    story.append(Spacer(1, 3))
                    
        else:
            story.append(Paragraph("<b>ANALISIS IA NO DISPONIBLE</b>", normal_style))
            story.append(Spacer(1, 8))
            story.append(Paragraph("Para habilitar analisis con IA, configure OPENAI_API_KEY", normal_style))
            story.append(Spacer(1, 4))
            story.append(Paragraph("Se utilizo analisis automatico basado en metricas cuantitativas", normal_style))
        
        story.append(Spacer(1, 15))
        
        # Top 10 Recomendaciones
        story.append(Paragraph("TOP 10 RECOMENDACIONES", heading_style))
        
        # Crear tabla para recomendaciones
        data = [['#', 'Empresa', 'Sector', 'Inversion (CLP)', '%', 'Score']]
        
        for i, company in enumerate(result['recommendations']['distribucion'][:10], 1):
            data.append([
                str(i),
                f"{company['Empresa']}\n({company['Ticker']})",
                company['Sector'],
                f"${company['Monto_Inversion']:,}",
                f"{company['Porcentaje_Recomendado']:.1f}%",
                f"{company['Puntaje']:.3f}"
            ])
        
        table = Table(data, colWidths=[0.5*inch, 2*inch, 1.5*inch, 1.3*inch, 0.7*inch, 0.7*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(table)
        story.append(Spacer(1, 15))
        
        # Distribución por sectores
        story.append(Paragraph("DISTRIBUCION POR SECTORES", heading_style))
        
        sectores_data = [['Sector', 'Inversion (CLP)', 'Porcentaje']]
        for sector, data_sector in result['recommendations']['resumen_sectores'].items():
            sectores_data.append([
                sector,
                f"${data_sector['Monto_Inversion']:,}",
                f"{data_sector['Porcentaje_Recomendado']:.1f}%"
            ])
        
        sectores_table = Table(sectores_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        sectores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightcyan),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(sectores_table)
        story.append(Spacer(1, 15))
        
        # Estado del mercado
        story.append(Paragraph("ESTADO DEL MERCADO CHILENO", heading_style))
        
        # Crear párrafos separados para mejor renderizado
        story.append(Paragraph(f"<b>Precio promedio de acciones:</b> ${result['market_summary']['precio_promedio']:.2f}", normal_style))
        story.append(Paragraph(f"<b>Variacion promedio ultimos 6 meses:</b> {result['market_summary']['variacion_promedio_6m']:.2f}%", normal_style))
        story.append(Paragraph(f"<b>Dividend yield promedio:</b> {result['market_summary']['dividend_yield_promedio']:.2f}%", normal_style))
        story.append(Paragraph(f"<b>Empresas con dividendos:</b> {result['market_summary']['empresas_con_dividendos']}", normal_style))
        story.append(Spacer(1, 10))
        
        # Top performers
        story.append(Paragraph("MEJORES PERFORMERS (6 meses):", heading_style))
        for i, performer in enumerate(result['market_summary']['top_performers_6m'][:5], 1):
            story.append(Paragraph(f"{i}. <b>{performer['Empresa']}</b>: {performer['Variacion_6M']*100:.1f}%", normal_style))
        story.append(Spacer(1, 10))
        
        # Mejores dividendos
        story.append(Paragraph("MEJORES DIVIDENDOS:", heading_style))
        for i, dividend in enumerate(result['market_summary']['mejores_dividendos'][:5], 1):
            story.append(Paragraph(f"{i}. <b>{dividend['Empresa']}</b>: {dividend['Dividend_Yield']*100:.2f}%", normal_style))
        story.append(Spacer(1, 20))
        
        # Disclaimer
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            leftIndent=10,
            rightIndent=10,
            borderColor=colors.gray,
            borderWidth=1,
            borderPadding=10
        )
        
        # Disclaimer
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            leftIndent=10,
            rightIndent=10,
            borderColor=colors.gray,
            borderWidth=1,
            borderPadding=10
        )
        
        story.append(Spacer(1, 20))
        story.append(Paragraph("<b>IMPORTANTE - DISCLAIMER:</b>", disclaimer_style))
        story.append(Paragraph("Este analisis es generado automaticamente con fines informativos unicamente.", disclaimer_style))
        story.append(Paragraph("No constituye asesoria financiera profesional. Los datos se basan en informacion", disclaimer_style))
        story.append(Paragraph("historica y pueden no reflejar condiciones futuras del mercado. Se recomienda", disclaimer_style))
        story.append(Paragraph("consultar con un asesor financiero antes de tomar decisiones de inversion.", disclaimer_style))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"Reporte generado automaticamente el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}", disclaimer_style))
        story.append(Paragraph("Sistema de Analisis Automatizado - Stock Investment Advisor", disclaimer_style))
        
        # Construir PDF
        doc.build(story)
        
        print(f"✅ Reporte PDF generado: {pdf_filename}")
        print(f"📂 Ubicación: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        print(f"❌ Error generando PDF: {str(e)}")
        print("Detalles del error:")
        import traceback
        traceback.print_exc()
        raise
        raise


def generate_monthly_report(result, config):
    """Genera reporte mensual completo"""
    print("📄 Generando reporte mensual...")
    
    try:
        # Generar PDF directamente
        pdf_filename = generate_monthly_report_pdf(result, config)
        
        # Crear contenido de texto simple para el email
        report_content = f"""
REPORTE MENSUAL DE INVERSIÓN - {datetime.now().strftime('%B %Y').upper()}

📊 RESUMEN EJECUTIVO:
- Fecha: {datetime.now().strftime('%d/%m/%Y')}
- Presupuesto: ${config['budget']:,} CLP
- Perfil de riesgo: {config['risk_level'].title()}
- Empresas analizadas: {result['market_summary']['total_empresas']}
- Recomendaciones: {result['recommendations']['empresas_recomendadas']}

El análisis completo se encuentra en el archivo PDF adjunto.

Sistema de Análisis Automatizado - Stock Investment Advisor
        """
        
        return report_content, pdf_filename
        
    except Exception as e:
        print(f"❌ Error generando reporte: {str(e)}")
        raise


def send_email_report(report_content, report_filename):
    """Envía reporte por email"""
    print("📧 Preparando envío de email...")
    
    try:
        # Configuración de email (variables de entorno)
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        recipient_email = os.getenv('RECIPIENT_EMAIL')
        
        # Verificar configuración
        if not all([sender_email, sender_password, recipient_email]):
            print("⚠️  Configuración de email incompleta. Saltando envío...")
            print("   Configure las variables de entorno:")
            print("   - SENDER_EMAIL: Email del remitente")
            print("   - SENDER_PASSWORD: Contraseña del remitente")
            print("   - RECIPIENT_EMAIL: Email del destinatario")
            return False
        
        # Crear mensaje
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = (
            f"📊 Reporte Mensual de Inversión - "
            f"{datetime.now().strftime('%B %Y')}"
        )
        
        # Cuerpo del email
        body = f"""
Estimado/a inversionista,

Se ha generado el reporte mensual de análisis de inversión para el 
mercado chileno.

Fecha: {datetime.now().strftime('%d de %B de %Y')}
Análisis: Mercado de acciones chileno
Presupuesto base: ${200000:,} CLP

Encuentra el reporte completo en formato PDF adjunto con:
• Análisis detallado de todas las empresas del mercado
• Top 10 recomendaciones de inversión
• Distribución sugerida por sectores
• Métricas clave del mercado
• Análisis con Inteligencia Artificial (si está habilitada)

Recordatorio: Este análisis es generado automáticamente y tiene 
fines informativos únicamente.

Saludos,
Sistema Automatizado de Análisis de Inversión
        """
        
        message.attach(MIMEText(body, 'plain'))
        
        # Adjuntar archivo de reporte PDF
        try:
            with open(report_filename, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={report_filename}'
            )
            message.attach(part)
        except FileNotFoundError:
            print(f"⚠️  Archivo de reporte no encontrado: {report_filename}")
        
        # Enviar email con manejo de errores específico para Gmail
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            
            # Debug información de conexión
            print(f"🔗 Conectando a: {smtp_server}:{smtp_port}")
            print(f"👤 Usuario: {sender_email}")
            print("🔑 Intentando autenticación...")
            
            server.login(sender_email, sender_password)
            
            text = message.as_string()
            server.sendmail(sender_email, recipient_email, text)
            server.quit()
            
            print(f"✅ Email enviado exitosamente a {recipient_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Error de autenticación SMTP: {str(e)}")
            print("💡 Para Gmail, asegúrate de:")
            print("   1. Tener 2FA activado en tu cuenta")
            print("   2. Usar App Password en lugar de tu contraseña normal")
            print("   3. Generar App Password en: https://myaccount.google.com/apppasswords")
            print("   4. Usar esa contraseña en SENDER_PASSWORD")
            return False
        
    except Exception as e:
        print(f"❌ Error enviando email: {str(e)}")
        print("Detalles del error:")
        import traceback
        traceback.print_exc()
        return False


def cleanup_files(report_filename):
    """Limpia archivos temporales"""
    try:
        if os.path.exists(report_filename):
            os.remove(report_filename)
            print(f"🗑️  Archivo temporal eliminado: {report_filename}")
    except Exception as e:
        print(f"⚠️  Error limpiando archivos: {str(e)}")


def main():
    """Función principal del script de automatización"""
    print("=" * 60)
    print("🤖 SISTEMA DE ANÁLISIS AUTOMATIZADO")
    print("=" * 60)
    
    # Verificar si se debe forzar ejecución (para testing o ejecución manual)
    force_run = os.getenv('FORCE_RUN', 'false').lower() == 'true'
    github_workflow = os.getenv('GITHUB_ACTIONS', 'false').lower() == 'true'
    
    if force_run or github_workflow:
        print("🔧 Ejecución forzada detectada:")
        print(f"   - FORCE_RUN: {force_run}")
        print(f"   - GitHub Actions: {github_workflow}")
        print("   - Omitiendo verificación de fecha")
        print("🎯 Ejecutando análisis...")
    else:
        # Verificar si es primer día hábil (solo para ejecuciones locales)
        if not is_first_business_day():
            print("📅 Hoy no es el primer día hábil del mes. Saliendo...")
            print(f"   Fecha actual: {datetime.now().strftime('%d/%m/%Y - %A')}")
            print("   💡 Para ejecutar manualmente, use:")
            print(f"   FORCE_RUN=true python {__file__}")
            return
        
        print("🎯 Es primer día hábil del mes. Ejecutando análisis...")
    
    try:
        # 1. Ejecutar análisis
        result, config = run_monthly_analysis()
        
        # 2. Generar reporte
        report_content, report_filename = generate_monthly_report(
            result, config)
        
        # 3. Enviar por email
        email_sent = send_email_report(report_content, report_filename)
        
        # 4. Limpiar archivos
        cleanup_files(report_filename)
        
        # 5. Resumen final
        print("\n" + "=" * 60)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"📊 Empresas analizadas: "
              f"{result['market_summary']['total_empresas']}")
        print(f"🎯 Recomendaciones: "
              f"{result['recommendations']['empresas_recomendadas']}")
        print(f"📧 Email enviado: {'Sí' if email_sent else 'No'}")
        print(f"⏰ Tiempo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
    except Exception as e:
        print("\n❌ ERROR CRÍTICO EN EL PROCESO:")
        print(f"   {str(e)}")
        print("\nDetalles para debugging:")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
