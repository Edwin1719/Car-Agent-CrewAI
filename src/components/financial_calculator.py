"""
Calculadora Financiera Integrada para CarBot Pro
Componente reutilizable para análisis financiero de vehículos
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any
import pandas as pd
from datetime import datetime, timedelta


class FinancialCalculator:
    """Calculadora financiera inteligente para vehículos"""

    def __init__(self):
        self.default_rate = 5.9  # Tasa base
        self.insurance_rate = 0.012  # 1.2% anual
        self.maintenance_monthly = {
            'bmw': 150,
            'mercedes': 180,
            'audi': 140,
            'honda': 80,
            'toyota': 70,
            'mazda': 85
        }

    def render_calculator(self, vehicle_price: float, vehicle_brand: str = "honda") -> Dict[str, Any]:
        """
        Renderiza calculadora financiera interactiva

        Args:
            vehicle_price: Precio del vehículo
            vehicle_brand: Marca para calcular costos específicos

        Returns:
            Dict con todos los cálculos financieros
        """
        st.markdown("### 💰 **Calculadora Financiera Inteligente**")

        with st.container():
            col1, col2 = st.columns([2, 1])

            with col1:
                # Inputs principales
                st.markdown("#### Configuración del Financiamiento")

                down_payment_pct = st.slider(
                    "💵 Enganche (%)",
                    min_value=10, max_value=50, value=20, step=5,
                    help="Porcentaje del precio total como enganche"
                )

                loan_term = st.selectbox(
                    "📅 Plazo de financiamiento",
                    [24, 36, 48, 60, 72, 84],
                    index=3,  # 60 meses por defecto
                    help="Duración del crédito en meses"
                )

                interest_rate = st.number_input(
                    "📈 Tasa de interés anual (%)",
                    min_value=3.0, max_value=15.0, value=self.default_rate, step=0.1,
                    help="Tasa de interés anual del crédito"
                )

            with col2:
                # Resumen visual rápido
                down_payment = vehicle_price * (down_payment_pct / 100)
                loan_amount = vehicle_price - down_payment

                st.markdown("#### 📊 Resumen Rápido")
                st.metric("Precio del vehículo", f"${vehicle_price:,.0f}")
                st.metric("Enganche", f"${down_payment:,.0f}")
                st.metric("Monto a financiar", f"${loan_amount:,.0f}")

        # Cálculos financieros
        calculations = self._calculate_loan_details(
            loan_amount, interest_rate, loan_term, vehicle_brand
        )

        # Mostrar resultados
        self._render_results(calculations, vehicle_brand)

        # Gráficos interactivos
        self._render_charts(calculations, vehicle_price, down_payment)

        return calculations

    def _calculate_loan_details(self, loan_amount: float, rate: float, term: int, brand: str) -> Dict[str, Any]:
        """Calcula todos los detalles del préstamo"""

        # Cálculo de pago mensual
        monthly_rate = rate / 100 / 12
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** term) / ((1 + monthly_rate) ** term - 1)

        # Total a pagar
        total_payments = monthly_payment * term
        total_interest = total_payments - loan_amount

        # Costos adicionales mensuales
        insurance_monthly = (loan_amount * self.insurance_rate) / 12
        maintenance_monthly = self.maintenance_monthly.get(brand.lower(), 100)

        # Costo total mensual
        total_monthly_cost = monthly_payment + insurance_monthly + maintenance_monthly

        # Cronograma de pagos (primeros 12 meses)
        payment_schedule = []
        remaining_balance = loan_amount

        for month in range(1, min(13, term + 1)):
            interest_payment = remaining_balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_balance -= principal_payment

            payment_schedule.append({
                'mes': month,
                'pago_total': monthly_payment,
                'capital': principal_payment,
                'interes': interest_payment,
                'saldo': remaining_balance
            })

        return {
            'monthly_payment': monthly_payment,
            'total_payments': total_payments,
            'total_interest': total_interest,
            'insurance_monthly': insurance_monthly,
            'maintenance_monthly': maintenance_monthly,
            'total_monthly_cost': total_monthly_cost,
            'payment_schedule': payment_schedule,
            'loan_amount': loan_amount,
            'term': term,
            'rate': rate
        }

    def _render_results(self, calc: Dict[str, Any], brand: str):
        """Renderiza resultados financieros"""

        st.markdown("---")
        st.markdown("### 📈 **Análisis Financiero Completo**")

        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "💳 Pago Mensual",
                f"${calc['monthly_payment']:,.0f}",
                help="Pago mensual del crédito automotriz"
            )

        with col2:
            st.metric(
                "🛡️ Seguro Mensual",
                f"${calc['insurance_monthly']:,.0f}",
                help="Estimado de seguro de cobertura amplia"
            )

        with col3:
            st.metric(
                "🔧 Mantenimiento",
                f"${calc['maintenance_monthly']:,.0f}",
                help=f"Costo promedio mensual mantenimiento {brand.title()}"
            )

        with col4:
            st.metric(
                "💰 Total Mensual",
                f"${calc['total_monthly_cost']:,.0f}",
                help="Costo total mensual (crédito + seguro + mantenimiento)"
            )

        # Desglose de intereses
        col1, col2 = st.columns(2)

        with col1:
            st.info(f"""
            **💡 Resumen del Crédito:**
            - Total a pagar: ${calc['total_payments']:,.0f}
            - Total en intereses: ${calc['total_interest']:,.0f}
            - Ahorro vs. renta: ${calc['monthly_payment'] - 800:,.0f}/mes*

            *Comparado con renta promedio de auto similar
            """)

        with col2:
            # Advice box personalizado por marca
            advice = self._get_brand_financial_advice(brand, calc['total_monthly_cost'])
            st.success(f"""
            **🎯 Recomendación Financiera:**
            {advice}
            """)

    def _render_charts(self, calc: Dict[str, Any], vehicle_price: float, down_payment: float):
        """Renderiza gráficos interactivos"""

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de pastel: Desglose de costos
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Pago del Crédito', 'Seguro', 'Mantenimiento'],
                values=[calc['monthly_payment'], calc['insurance_monthly'], calc['maintenance_monthly']],
                hole=.3,
                marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1']
            )])

            fig_pie.update_layout(
                title="🍰 Desglose de Costos Mensuales",
                height=400
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            # Gráfico de barras: Capital vs Intereses por mes
            df_schedule = pd.DataFrame(calc['payment_schedule'])

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                name='Capital',
                x=df_schedule['mes'],
                y=df_schedule['capital'],
                marker_color='#28a745'
            ))
            fig_bar.add_trace(go.Bar(
                name='Intereses',
                x=df_schedule['mes'],
                y=df_schedule['interes'],
                marker_color='#dc3545'
            ))

            fig_bar.update_layout(
                title='📊 Capital vs Intereses (Primeros 12 meses)',
                xaxis_title='Mes',
                yaxis_title='Pago ($)',
                barmode='stack',
                height=400
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Tabla de cronograma
        if st.checkbox("📅 Ver cronograma de pagos detallado"):
            st.markdown("#### Cronograma de Pagos (Primeros 12 meses)")
            df_display = pd.DataFrame(calc['payment_schedule'])
            df_display.columns = ['Mes', 'Pago Total ($)', 'Capital ($)', 'Intereses ($)', 'Saldo Restante ($)']

            # Formatear números
            for col in ['Pago Total ($)', 'Capital ($)', 'Intereses ($)', 'Saldo Restante ($)']:
                df_display[col] = df_display[col].apply(lambda x: f"${x:,.0f}")

            st.dataframe(df_display, use_container_width=True)

    def _get_brand_financial_advice(self, brand: str, total_monthly: float) -> str:
        """Genera consejo financiero personalizado por marca"""

        advice_map = {
            'bmw': f"BMW mantiene excelente valor de reventa. Con ${total_monthly:,.0f}/mes, es una inversión inteligente en lujo alemán.",
            'mercedes': f"Mercedes ofrece prestigio premium. A ${total_monthly:,.0f}/mes, considera garantía extendida para tranquilidad total.",
            'audi': f"Audi combina tecnología y performance. ${total_monthly:,.0f}/mes es competitivo para su segmento premium.",
            'honda': f"Honda es sinónimo de confiabilidad. A ${total_monthly:,.0f}/mes, tendrás costos predecibles y bajo mantenimiento.",
            'toyota': f"Toyota lidera en confiabilidad mundial. Con ${total_monthly:,.0f}/mes, es la opción más económica a largo plazo.",
            'mazda': f"Mazda ofrece excelente relación calidad-precio. ${total_monthly:,.0f}/mes es un gran valor en su categoría."
        }

        return advice_map.get(brand.lower(), f"Con ${total_monthly:,.0f}/mes total, este vehículo está dentro de parámetros financieros razonables.")


# Función helper para integración fácil
def render_financial_calculator(vehicle_price: float, vehicle_brand: str = "honda") -> Dict[str, Any]:
    """
    Función helper para integrar calculadora en cualquier parte de la app

    Usage:
        calculations = render_financial_calculator(35000, "honda")
    """
    calculator = FinancialCalculator()
    return calculator.render_calculator(vehicle_price, vehicle_brand)


if __name__ == "__main__":
    # Demo/Test
    st.title("🚗 Demo: Calculadora Financiera")
    render_financial_calculator(45000, "bmw")