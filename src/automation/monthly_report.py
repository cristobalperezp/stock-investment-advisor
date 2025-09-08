"""
Automatización mensual para análisis de inversión y envío por email
Se ejecuta el primer día hábil de cada mes
"""

import os
import sys
import smtplib
import json
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd

# Agregar src al path
src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from analysis.investment_analyzer import InvestmentAnalyzer
from analysis.report_generator import generate_investment_report
from utils.config import get_config


def is_first_business_day():
    """Verifica si hoy es el primer día hábil del mes"""
    today = datetime.now()
    
    # Obtener primer día del mes
    first_day = datetime(today.year, today.month, 1)
    
    # Buscar primer día hábil (lunes=0, domingo=6)
    while first_day.weekday() > 4:  # Si es sábado (5) o domingo (6)
        first_day += timedelta(days=1)
    
    return today.date() == first_day.date()


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


def generate_monthly_report(result, config):
    """Genera reporte mensual completo"""
    print("📄 Generando reporte mensual...")
    
    try:
        # Generar reporte con gráficos
        report = generate_investment_report(
            result['fundamental_data'],
            result['recommendations'],
            result['market_summary']
        )
        
        # Crear reporte en texto
        report_content = f"""
        REPORTE MENSUAL DE INVERSIÓN - {datetime.now().strftime('%B %Y').upper()}
        ================================================================

        📊 RESUMEN EJECUTIVO
        - Fecha del análisis: {datetime.now().strftime('%d/%m/%Y')}
        - Presupuesto analizado: ${config['budget']:,} CLP
        - Perfil de riesgo: {config['risk_level'].title()}
        - Total de empresas analizadas: {result['market_summary']['total_empresas']}
        - Empresas recomendadas: {result['recommendations']['empresas_recomendadas']}

        🤖 ANÁLISIS INTELIGENTE CON IA
        {'=' * 40}
        """
        
        # Incluir análisis GPT si está disponible
        if 'gpt_analysis' in result and result['gpt_analysis']:
            report_content += f"""
            ✅ ANÁLISIS REALIZADO CON INTELIGENCIA ARTIFICIAL

            {result['gpt_analysis']}

            � DISTRIBUCIÓN RECOMENDADA POR IA:
            {result['gpt_distribution']}

            """
        else:
            report_content += """
            ⚠️ ANÁLISIS IA NO DISPONIBLE
            - Para habilitar análisis con IA, configure OPENAI_API_KEY
            - Se utilizó análisis automático basado en métricas cuantitativas
            """
        
        report_content += f"""
        �💰 TOP 10 RECOMENDACIONES DE INVERSIÓN (ANÁLISIS AUTOMÁTICO):
        """
        
        # Top 10 recomendaciones
        for i, company in enumerate(result['recommendations']['distribucion'][:10], 1):
            report_content += f"""
            {i:2d}. {company['Empresa']} ({company['Ticker']})
                • Sector: {company['Sector']}
                • Inversión sugerida: ${company['Monto_Inversion']:,} CLP ({company['Porcentaje_Recomendado']:.2f}%)
                • Score de análisis: {company['Puntaje']:.4f}
            """
        
        # Distribución por sectores
        report_content += f"""
        🏢 DISTRIBUCIÓN POR SECTORES:
        """
        for sector, data in result['recommendations']['resumen_sectores'].items():
            report_content += f"• {sector}: ${data['Monto_Inversion']:,} CLP ({data['Porcentaje_Recomendado']:.1f}%)\n"
        
        # Métricas del mercado
        report_content += f"""
        📈 ESTADO DEL MERCADO CHILENO:
        • Precio promedio de acciones: ${result['market_summary']['precio_promedio']:.2f}
        • Variación promedio últimos 6 meses: {result['market_summary']['variacion_promedio_6m']:.2f}%
        • Dividend yield promedio: {result['market_summary']['dividend_yield_promedio']:.2f}%
        • Empresas con dividendos: {result['market_summary']['empresas_con_dividendos']}

        🏆 MEJORES PERFORMERS (6 meses):
        """
        
        for i, performer in enumerate(result['market_summary']['top_performers_6m'][:5], 1):
            report_content += f"{i}. {performer['Empresa']}: {performer['Variacion_6M']*100:.1f}%\n"
        
        report_content += f"""
        💎 MEJORES DIVIDENDOS:
        """
        
        for i, dividend in enumerate(result['market_summary']['mejores_dividendos'][:5], 1):
            report_content += f"{i}. {dividend['Empresa']}: {dividend['Dividend_Yield']*100:.2f}%\n"
        
        # Disclaimer
        report_content += f"""
        ⚠️  IMPORTANTE - DISCLAIMER:
        Este análisis es generado automáticamente con fines informativos únicamente.
        No constituye asesoría financiera profesional. Los datos se basan en información
        histórica y pueden no reflejar condiciones futuras del mercado. Se recomienda
        consultar con un asesor financiero antes de tomar decisiones de inversión.

        ---
        Reporte generado automáticamente el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}
        Sistema de Análisis Automatizado - Stock Investment Advisor
        """
        
        # Guardar reporte
        report_filename = f"reporte_mensual_{datetime.now().strftime('%Y_%m')}.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ Reporte guardado: {report_filename}")
        
        return report_content, report_filename
        
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
        message['Subject'] = f"📊 Reporte Mensual de Inversión - {datetime.now().strftime('%B %Y')}"
        
        # Cuerpo del email
        body = f"""
        Estimado/a inversionista,

        Se ha generado el reporte mensual de análisis de inversión para el mercado chileno.

        📅 Fecha: {datetime.now().strftime('%d de %B de %Y')}
        🎯 Análisis: Mercado de acciones chileno
        💰 Presupuesto base: $5.000.000 CLP

        Encuentra el reporte completo en el archivo adjunto.

        Highlights del mes:
        • Total de empresas analizadas en el mercado chileno
        • Recomendaciones de inversión basadas en análisis fundamental
        • Distribución sugerida por sectores
        • Métricas clave del mercado

        ⚠️ Recordatorio: Este análisis es generado automáticamente y tiene fines informativos únicamente.

        Saludos,
        Sistema Automatizado de Análisis de Inversión
        """
        
        message.attach(MIMEText(body, 'plain'))
        
        # Adjuntar archivo de reporte
        try:
            with open(report_filename, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {report_filename}'
            )
            message.attach(part)
        except FileNotFoundError:
            print(f"⚠️  Archivo de reporte no encontrado: {report_filename}")
        
        # Enviar email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        print(f"✅ Email enviado exitosamente a {recipient_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error enviando email: {str(e)}")
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
    
    # Verificar si es el primer día hábil del mes
    if not is_first_business_day():
        print(f"📅 Hoy no es el primer día hábil del mes. Saliendo...")
        print(f"   Fecha actual: {datetime.now().strftime('%d/%m/%Y - %A')}")
        return
    
    print(f"🎯 Es primer día hábil del mes. Ejecutando análisis...")
    
    try:
        # 1. Ejecutar análisis
        result, config = run_monthly_analysis()
        
        # 2. Generar reporte
        report_content, report_filename = generate_monthly_report(result, config)
        
        # 3. Enviar por email
        email_sent = send_email_report(report_content, report_filename)
        
        # 4. Limpiar archivos
        cleanup_files(report_filename)
        
        # 5. Resumen final
        print("\n" + "=" * 60)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"📊 Empresas analizadas: {result['market_summary']['total_empresas']}")
        print(f"🎯 Recomendaciones: {result['recommendations']['empresas_recomendadas']}")
        print(f"📧 Email enviado: {'Sí' if email_sent else 'No'}")
        print(f"⏰ Tiempo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO EN EL PROCESO:")
        print(f"   {str(e)}")
        print("\nDetalles para debugging:")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
