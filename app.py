import streamlit as st

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Sistema +DP | Cálculos Trabalhistas",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Sistema +DP — Calculadora Trabalhista")
st.caption("Ferramenta de apoio para cálculos rápidos do dia a dia do Departamento Pessoal.")

# ==========================================
# FUNÇÕES DE CÁLCULO
# ==========================================

def calcular_inss_progressivo(salario_bruto):
    faixas = [
        (1621.00, 0.075),
        (2902.84, 0.09),
        (4354.27, 0.12),
        (8475.55, 0.14)
    ]
    
    total_inss = 0
    salario_restante = salario_bruto
    limite_anterior = 0
    
    for limite, aliquota in faixas:
        if salario_restante <= 0:
            break
            
        largura_faixa = limite - limite_anterior
        
        if salario_restante > largura_faixa:
            valor_tributavel = largura_faixa
            salario_restante -= largura_faixa
        else:
            valor_tributavel = salario_restante
            salario_restante = 0
            
        total_inss += valor_tributavel * aliquota
        limite_anterior = limite

    return round(total_inss, 2)


def calcular_irrf(base_calculo, num_dependentes=0):
    DEDUCAO_DEPENDENTE = 189.59
    base_calculo -= (num_dependentes * DEDUCAO_DEPENDENTE)

    if base_calculo <= 2259.20:
        return 0.0, 0.0
    elif base_calculo <= 2826.65:
        imposto = (base_calculo * 0.075) - 169.44
        aliquota = 7.5
    elif base_calculo <= 3751.05:
        imposto = (base_calculo * 0.15) - 381.44
        aliquota = 15.0
    elif base_calculo <= 4664.68:
        imposto = (base_calculo * 0.225) - 662.77
        aliquota = 22.5
    else:
        imposto = (base_calculo * 0.275) - 896.00
        aliquota = 27.5

    return round(max(imposto, 0.0), 2), aliquota


# ==========================================
# INTERFACE DO USUÁRIO (ABAS)
# ==========================================

aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "💵 Saldo de Salário", 
    "🎁 13º Salário", 
    "🏖️ Férias", 
    "📄 Aviso Prévio", 
    "🏦 FGTS Mensal", 
    "⚖️ Multa FGTS"
])

# --- ABA 1: SALDO DE SALÁRIO ---
with aba1:
    st.header("Cálculo de Saldo de Salário")
    col1, col2 = st.columns(2)
    
    with col1:
        salario = st.number_input("Salário Base (R$)", min_value=0.0, value=2000.00, step=100.00, key="sal1")
        dias = st.number_input("Dias Trabalhados no Mês", min_value=1, max_value=31, value=30, key="dias1")
        dependentes = st.number_input("Número de Dependentes", min_value=0, value=0, key="dep1")

    with col2:
        bruto = (salario / 30) * dias
        inss = calcular_inss_progressivo(bruto)
        irrf, aliquota_ir = calcular_irrf(bruto - inss, dependentes)
        liquido = bruto - inss - irrf

        st.metric(label="Salário Bruto Proporcional", value=f"R$ {bruto:,.2f}")
        st.metric(label="Desconto INSS", value=f"R$ {inss:,.2f}", delta_color="inverse")
        st.metric(label=f"Desconto IRRF ({aliquota_ir}%)", value=f"R$ {irrf:,.2f}", delta_color="inverse")
        st.subheader(f"Valor Líquido: R$ {liquido:,.2f}")

# --- ABA 2: DÉCIMO TERCEIRO ---
with aba2:
    st.header("Cálculo de 13º Salário Proporcional")
    col1, col2 = st.columns(2)
    
    with col1:
        salario_13 = st.number_input("Salário Base (R$)", min_value=0.0, value=2000.00, step=100.00, key="sal2")
        meses_13 = st.number_input("Meses Trabalhados no Ano (mín. 15 dias)", min_value=1, max_value=12, value=12, key="mes2")
        dep_13 = st.number_input("Número de Dependentes", min_value=0, value=0, key="dep2")

    with col2:
        bruto_13 = (salario_13 / 12) * meses_13
        inss_13 = calcular_inss_progressivo(bruto_13)
        irrf_13, aliq_13 = calcular_irrf(bruto_13 - inss_13, dep_13)
        liq_13 = bruto_13 - inss_13 - irrf_13

        st.metric(label="13º Bruto", value=f"R$ {bruto_13:,.2f}")
        st.metric(label="Desconto INSS", value=f"R$ {inss_13:,.2f}")
        st.metric(label=f"Desconto IRRF ({aliq_13}%)", value=f"R$ {irrf_13:,.2f}")
        st.subheader(f"13º Líquido: R$ {liq_13:,.2f}")

# --- ABA 3: FÉRIAS ---
with aba3:
    st.header("Cálculo de Férias Proporcionais + 1/3")
    col1, col2 = st.columns(2)
    
    with col1:
        salario_ferias = st.number_input("Salário Base (R$)", min_value=0.0, value=2000.00, step=100.00, key="sal3")
        meses_ferias = st.number_input("Meses do Período Aquisitivo", min_value=1, max_value=12, value=12, key="mes3")

    with col2:
        ferias_simples = (salario_ferias / 12) * meses_ferias
        terco = ferias_simples / 3
        total_ferias = ferias_simples + terco

        st.metric(label="Férias Proporcionais", value=f"R$ {ferias_simples:,.2f}")
        st.metric(label="Adicional Constitucional (1/3)", value=f"R$ {terco:,.2f}")
        st.subheader(f"Total a Receber: R$ {total_ferias:,.2f}")

# --- ABA 4: AVISO PRÉVIO ---
with aba4:
    st.header("Aviso Prévio Indenizado (Lei 12.506)")
    col1, col2 = st.columns(2)
    
    with col1:
        salario_aviso = st.number_input("Salário Base (R$)", min_value=0.0, value=2000.00, step=100.00, key="sal4")
        anos_trabalhados = st.number_input("Anos Completos na Empresa", min_value=0, max_value=30, value=1, key="ano4")

    with col2:
        dias_aviso = min(30 + (anos_trabalhados * 3), 90)
        valor_aviso = (salario_aviso / 30) * dias_aviso

        st.info(f"Direito adquirido: **{dias_aviso} dias** de aviso prévio.")
        st.subheader(f"Valor do Aviso Prévio: R$ {valor_aviso:,.2f}")

# --- ABA 5: FGTS MENSAL ---
with aba5:
    st.header("Recolhimento Mensal do FGTS")
    col1, col2 = st.columns(2)
    
    with col1:
        salario_fgts = st.number_input("Salário Bruto do Mês (R$)", min_value=0.0, value=2000.00, step=100.00, key="sal5")

    with col2:
        valor_fgts = salario_fgts * 0.08
        st.subheader(f"Valor do Depósito (8%): R$ {valor_fgts:,.2f}")

# --- ABA 6: MULTA DO FGTS ---
with aba6:
    st.header("Multa Rescisória do FGTS (40%)")
    col1, col2 = st.columns(2)
    
    with col1:
        saldo_fgts = st.number_input("Saldo Acumulado no Extrato do FGTS (R$)", min_value=0.0, value=5000.00, step=500.00, key="sal6")

    with col2:
        multa = saldo_fgts * 0.40
        st.subheader(f"Valor da Multa (40%): R$ {multa:,.2f}")