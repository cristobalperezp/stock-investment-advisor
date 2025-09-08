"""
Generador de reportes de inversión con gráficos y análisis
Integra con OpenAI para análisis inteligente
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class InvestmentReportGenerator:
    """Generador de reportes de inversión con visualizaciones"""
    
    def __init__(self):
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }
    
    def create_portfolio_pie_chart(self, recommendations: Dict) -> go.Figure:
        """Crea gráfico de torta para distribución del portafolio"""
        distribution = recommendations['distribucion']
        
        labels = [item['Empresa'] for item in distribution]
        values = [item['Porcentaje_Recomendado'] for item in distribution]
        amounts = [item['Monto_Inversion'] for item in distribution]
        
        # Crear texto personalizado para el hover
        hover_text = [
            f"<b>{label}</b><br>" +
            f"Porcentaje: {value:.1f}%<br>" +
            f"Inversión: ${amount:,.0f}<br>" +
            f"Sector: {item['Sector']}"
            for label, value, amount, item in zip(labels, values, amounts, distribution)
        ]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hovertemplate='%{text}<extra></extra>',
            text=hover_text,
            textinfo='label+percent',
            textposition='inside',
            marker=dict(
                colors=px.colors.qualitative.Set3[:len(labels)],
                line=dict(color='white', width=2)
            ),
            hole=0.4
        )])
        
        fig.update_layout(
            title={
                'text': f"<b>Distribución de Portafolio</b><br>" +
                        f"<sub>Presupuesto Total: ${recommendations['presupuesto_total']:,.0f}</sub>",
                'x': 0.5,
                'font': {'size': 20}
            },
            font={'size': 14},
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02
            ),
            height=600,
            margin=dict(l=20, r=150, t=80, b=20)
        )
        
        return fig
    
    def create_sector_distribution_chart(self, recommendations: Dict) -> go.Figure:
        """Crea gráfico de barras para distribución por sector"""
        sector_summary = recommendations['resumen_sectores']
        
        sectores = list(sector_summary.keys())
        inversiones = [sector_summary[sector]['Monto_Inversion'] for sector in sectores]
        porcentajes = [sector_summary[sector]['Porcentaje_Recomendado'] for sector in sectores]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=sectores,
            y=inversiones,
            name='Monto de Inversión',
            text=[f'${inv:,.0f}<br>({pct:.1f}%)' for inv, pct in zip(inversiones, porcentajes)],
            textposition='outside',
            marker_color=self.colors['primary'],
            hovertemplate='<b>%{x}</b><br>Inversión: $%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': '<b>Distribución por Sector</b>',
                'x': 0.5,
                'font': {'size': 20}
            },
            xaxis_title='Sector',
            yaxis_title='Monto de Inversión ($)',
            font={'size': 14},
            height=500,
            margin=dict(l=60, r=60, t=80, b=60),
            showlegend=False
        )
        
        # Formato del eje Y
        fig.update_yaxes(tickformat='$,.0f')
        
        return fig
    
    def create_metrics_comparison_chart(self, df_fundamentals: pd.DataFrame, 
                                      recommendations: Dict) -> go.Figure:
        """Crea gráfico comparativo de métricas clave"""
        recommended_tickers = [item['Ticker'] for item in recommendations['distribucion']]
        df_recommended = df_fundamentals[df_fundamentals['Ticker'].isin(recommended_tickers)].copy()
        
        metrics = ['ROE', 'Dividend_Yield', 'Variacion_6M', 'PE_Ratio']
        metric_names = ['ROE (%)', 'Dividend Yield (%)', 'Variación 6M (%)', 'P/E Ratio']
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=metric_names,
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        for i, (metric, name) in enumerate(zip(metrics, metric_names)):
            row = i // 2 + 1
            col = i % 2 + 1
            
            # Obtener datos válidos
            data = df_recommended[df_recommended[metric].notna()]
            if len(data) == 0:
                continue
                
            # Convertir a porcentajes si es necesario
            if metric in ['ROE', 'Dividend_Yield', 'Variacion_6M']:
                values = data[metric] * 100
                format_str = '.1f'
            else:
                values = data[metric]
                format_str = '.2f'
            
            # Asegurar que todos los valores son numéricos
            values = pd.to_numeric(values, errors='coerce')
            valid_mask = ~values.isna()
            values = values[valid_mask]
            data_filtered = data[valid_mask]
            
            if len(values) == 0:
                continue
            
            fig.add_trace(
                go.Bar(
                    x=data_filtered['Empresa'],
                    y=values,
                    name=name,
                    text=[f'{v:{format_str}}' if pd.notna(v) else 'N/A' for v in values],
                    textposition='outside',
                    marker_color=px.colors.qualitative.Set2[i],
                    showlegend=False,
                    hovertemplate=f'<b>%{{x}}</b><br>{name}: %{{y:{format_str}}}<extra></extra>'
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            title={
                'text': '<b>Métricas Clave de Empresas Recomendadas</b>',
                'x': 0.5,
                'font': {'size': 20}
            },
            height=800,
            showlegend=False,
            font={'size': 12}
        )
        
        return fig
    
    def create_performance_timeline_chart(self, df_fundamentals: pd.DataFrame, 
                                        recommendations: Dict) -> go.Figure:
        """Crea gráfico de líneas para performance temporal"""
        recommended_companies = recommendations['distribucion'][:10]  # Top 10
        
        fig = go.Figure()
        
        periods = ['1M', '6M', '1Y']
        period_columns = ['Variacion_1M', 'Variacion_6M', 'Variacion_1Y']
        
        for company in recommended_companies:
            ticker = company['Ticker']
            empresa = company['Empresa']
            
            company_data = df_fundamentals[df_fundamentals['Ticker'] == ticker].iloc[0]
            
            returns = []
            for col in period_columns:
                value = company_data.get(col, np.nan)
                returns.append(value * 100 if not pd.isna(value) else np.nan)
            
            fig.add_trace(go.Scatter(
                x=periods,
                y=returns,
                mode='lines+markers',
                name=empresa,
                line=dict(width=3),
                marker=dict(size=8),
                hovertemplate=f'<b>{empresa}</b><br>Período: %{{x}}<br>Retorno: %{{y:.1f}}%<extra></extra>'
            ))
        
        fig.update_layout(
            title={
                'text': '<b>Performance Temporal de Empresas Recomendadas</b>',
                'x': 0.5,
                'font': {'size': 20}
            },
            xaxis_title='Período',
            yaxis_title='Retorno (%)',
            height=600,
            font={'size': 14},
            hovermode='x unified',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.01
            )
        )
        
        # Añadir línea de referencia en 0%
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        return fig
    
    def create_risk_return_scatter(self, df_fundamentals: pd.DataFrame, 
                                 recommendations: Dict) -> go.Figure:
        """Crea gráfico de dispersión riesgo-retorno"""
        recommended_tickers = [item['Ticker'] for item in recommendations['distribucion']]
        df_plot = df_fundamentals[
            (df_fundamentals['Ticker'].isin(recommended_tickers)) &
            (df_fundamentals['Volatilidad'].notna()) &
            (df_fundamentals['Variacion_6M'].notna())
        ].copy()
        
        if len(df_plot) == 0:
            return go.Figure().add_annotation(
                text="No hay datos suficientes para el análisis riesgo-retorno",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Obtener información de inversión
        investment_info = {item['Ticker']: item['Monto_Inversion'] 
                          for item in recommendations['distribucion']}
        df_plot['Inversion'] = df_plot['Ticker'].map(investment_info)
        
        fig = go.Figure()
        
        # Crear scatter plot
        fig.add_trace(go.Scatter(
            x=df_plot['Volatilidad'] * 100,
            y=df_plot['Variacion_6M'] * 100,
            mode='markers+text',
            text=df_plot['Empresa'],
            textposition='top center',
            marker=dict(
                size=df_plot['Inversion'] / 10000,  # Escalar por inversión
                color=df_plot['Variacion_6M'] * 100,
                colorscale='RdYlGn',
                colorbar=dict(title="Retorno 6M (%)"),
                line=dict(width=2, color='white'),
                sizemin=10,
                sizeref=2
            ),
            hovertemplate=(
                '<b>%{text}</b><br>' +
                'Volatilidad: %{x:.1f}%<br>' +
                'Retorno 6M: %{y:.1f}%<br>' +
                'Inversión: $%{customdata:,.0f}<extra></extra>'
            ),
            customdata=df_plot['Inversion'],
            name='Empresas'
        ))
        
        fig.update_layout(
            title={
                'text': '<b>Análisis Riesgo-Retorno</b><br><sub>Tamaño de burbuja = Monto de inversión</sub>',
                'x': 0.5,
                'font': {'size': 20}
            },
            xaxis_title='Volatilidad Anualizada (%)',
            yaxis_title='Retorno 6 Meses (%)',
            height=600,
            font={'size': 14},
            showlegend=False
        )
        
        # Añadir líneas de referencia
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=df_plot['Volatilidad'].mean() * 100, 
                      line_dash="dash", line_color="gray", opacity=0.5)
        
        return fig
    
    def generate_text_analysis(self, df_fundamentals: pd.DataFrame, 
                             recommendations: Dict, market_summary: Dict) -> str:
        """Genera análisis textual de las recomendaciones"""
        
        analysis_text = f"""## 📊 Análisis de Inversión - {datetime.now().strftime('%d/%m/%Y')}

### 🎯 Resumen Ejecutivo
- **Total de empresas analizadas**: {market_summary['total_empresas']}
- **Empresas con dividendos**: {market_summary['empresas_con_dividendos']}
- **Presupuesto total**: ${recommendations['presupuesto_total']:,.0f}
- **Total a invertir**: ${recommendations['total_invertido']:,.0f}
- **Empresas recomendadas**: {recommendations['empresas_recomendadas']}

### 💰 Top 5 Recomendaciones"""
        
        # Top 5 recomendaciones
        for i, company in enumerate(recommendations['distribucion'][:5], 1):
            analysis_text += f"""

**{i}. {company['Empresa']} ({company['Sector']})**
- Inversión recomendada: ${company['Monto_Inversion']:,.0f} ({company['Porcentaje_Recomendado']:.1f}%)
- Puntaje de análisis: {company['Puntaje']:.3f}"""
        
        # Análisis por sector
        analysis_text += f"""

### 🏢 Distribución por Sectores"""
        
        for sector, data in recommendations['resumen_sectores'].items():
            analysis_text += f"\n- **{sector}**: ${data['Monto_Inversion']:,.0f} ({data['Porcentaje_Recomendado']:.1f}%)"
        
        # Métricas del mercado
        analysis_text += f"""

### 📈 Métricas del Mercado
- **Precio promedio**: ${market_summary['precio_promedio']:.2f}
- **Variación promedio 6M**: {market_summary['variacion_promedio_6m']:.2f}%
- **Dividend Yield promedio**: {market_summary['dividend_yield_promedio']:.2f}%

### 🏆 Mejores Performers (6 meses)"""
        
        for performer in market_summary['top_performers_6m'][:3]:
            analysis_text += f"\n- **{performer['Empresa']}**: {performer['Variacion_6M']*100:.1f}%"
        
        analysis_text += """

### 💎 Mejores Dividendos"""
        
        for dividend in market_summary['mejores_dividendos'][:3]:
            # Yahoo Finance ya devuelve dividendYield como decimal, no multiplicar por 100
            yield_value = dividend['Dividend_Yield']
            if isinstance(yield_value, (int, float)) and yield_value > 1:
                # Si el valor es mayor a 1, probablemente ya está en porcentaje
                analysis_text += f"\n- **{dividend['Empresa']}**: {yield_value:.2f}%"
            else:
                # Si es menor a 1, convertir de decimal a porcentaje
                analysis_text += f"\n- **{dividend['Empresa']}**: {yield_value*100:.2f}%"
        
        analysis_text += """

### ⚠️ Consideraciones de Riesgo
- La distribución busca diversificación entre sectores
- Se priorizan empresas con historial de dividendos
- Los análisis se basan en datos fundamentales históricos
- Se recomienda revisar periódicamente el portafolio

---
*Análisis generado automáticamente*"""
        
        return analysis_text.strip()
    
    def generate_complete_report(self, df_fundamentals: pd.DataFrame, 
                               recommendations: Dict, market_summary: Dict) -> Dict:
        """Genera un reporte completo con todos los gráficos y análisis"""
        
        report = {
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'texto_analisis': self.generate_text_analysis(df_fundamentals, recommendations, market_summary),
            'graficos': {
                'distribucion_portafolio': self.create_portfolio_pie_chart(recommendations),
                'distribucion_sectores': self.create_sector_distribution_chart(recommendations),
                'metricas_comparativas': self.create_metrics_comparison_chart(df_fundamentals, recommendations),
                'performance_temporal': self.create_performance_timeline_chart(df_fundamentals, recommendations),
                'riesgo_retorno': self.create_risk_return_scatter(df_fundamentals, recommendations)
            },
            'recomendaciones': recommendations,
            'resumen_mercado': market_summary
        }
        
        return report


def generate_investment_report(df_fundamentals: pd.DataFrame, 
                             recommendations: Dict, 
                             market_summary: Dict) -> Dict:
    """Función conveniente para generar reporte completo"""
    generator = InvestmentReportGenerator()
    return generator.generate_complete_report(df_fundamentals, recommendations, market_summary)


if __name__ == "__main__":
    # Ejemplo de uso con datos simulados
    print("Generador de reportes de inversión listo")
