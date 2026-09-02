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


def calcular_irrf(rendimento_bruto, inss_pago, num_dependentes=0):
    """
    Calcula o IRRF conforme a Tabela 2026:
    - Compara Dedução Legal (INSS + Dependentes) x Dedução Simplificada (R$ 607,20)
    - Aplica alíquotas e deduções de 2026
    - Aplica o Redutor Final conforme faixa de renda
    """
    DEDUCAO_DEPENDENTE = 189.59
    DEDUCAO_SIMPLIFICADA = 607.20

    base_legal = rendimento_bruto - inss_pago - (num_dependentes * DEDUCAO_DEPENDENTE)
    base_simplificada = rendimento_bruto - DEDUCAO_SIMPLIFICADA

    base_calculo = min(base_legal, base_simplificada)

    if base_calculo < 2428.81:
        imposto_inicial = 0.0
        aliquota = 0.0
    elif base_calculo <= 2826.65:
        imposto_inicial = (base_calculo * 0.075) - 182.16
        aliquota = 7.5
    elif base_calculo <= 3751.05:
        imposto_inicial = (base_calculo * 0.15) - 394.16
        aliquota = 15.0
    elif base_calculo <= 4664.68:
        imposto_inicial = (base_calculo * 0.225) - 675.49
        aliquota = 22.5
    else:
        imposto_inicial = (base_calculo * 0.275) - 908.73
        aliquota = 27.5

    imposto_inicial = max(0.0, imposto_inicial)

    # Redutores Finais do Imposto
    if rendimento_bruto <= 5000.00:
        if imposto_inicial <= 312.89:
            imposto_final = 0.0
        else:
            imposto_final = imposto_inicial
    elif 5000.01 <= rendimento_bruto <= 7350.00:
        redutor = 978.62 - (0.133145 * rendimento_bruto)
        redutor = max(0.0, redutor)
        imposto_final = max(0.0, imposto_inicial - redutor)
    else:
        imposto_final = imposto_inicial

    return round(imposto_final, 2), aliquota


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
        st.subheader("📌 Entradas & Proventos")
        salario = st.number_input("Salário Base (R$)", min_value=0.0, value=2000.00, step=100.00, key="sal1")
        dias = st.number_input("Dias Trabalhados no Mês", min_value=1, max_value=31, value=30, key="dias1")
        adicionais = st.number_input("Adicionais (HE, Insalubridade, Periculosidade, etc.) (R$)", min_value=0.0, value=0.00, step=50.00, key="adic1")
        dependentes = st.number_input("Número de Dependentes", min_value=0, value=0, key="dep1")

        st.subheader("🔻 Descontos Específicos")
        desc_vt = st.number_input("Vale-Transporte (R$)", min_value=0.0, value=0.00, step=10.00, key="vt1")
        desc_vr = st.number_input("Vale-Refeição/Alimentação (R$)", min_value=0.0, value=0.00, step=10.00, key="vr1")
        desc_saude = st.number_input("Plano de Saúde / Odonto (R$)", min_value=0.0, value=0.00, step=10.00, key="saude1")
        desc_outros = st.number_input("Outros Descontos (Faltas, Empréstimos, etc.) (R$)", min_value=0.0, value=0.00, step=10.00, key="outros1")

    with col2:
        bruto_proporcional = (salario / 30) * dias
        bruto_total = bruto_proporcional + adicionais
        
        inss = calcular_inss_progressivo(bruto_total)
        irrf, aliquota_ir = calcular_irrf(bruto_total, inss, dependentes)
        
        total_descontos_diversos = desc_vt + desc_vr + desc_saude + desc_outros
        total_descontos_geral = inss + irrf + total_descontos_diversos
        liquido = bruto_total - total_descontos_geral

        st.subheader("📊 Resumo do Cálculo")
        st.metric(label="Proventos Totais (Salário Proporcional + Adicionais)", value=f"R$ {bruto_total:,.2f}")
        st.metric(label="Desconto INSS", value=f"R$ {inss:,.2f}")
        st.metric(label=f"Desconto IRRF ({aliquota_ir}%)", value=f"R$ {irrf:,.2f}")
        
        if total_descontos_diversos > 0:
            st.metric(label="Outros Descontos Somados (VT, VR, Saúde, etc.)", value=f"R$ {total_descontos_diversos:,.2f}")
            
        st.markdown("---")
        st.subheader(f"Valor Líquido a Receber: R$ {liquido:,.2f}")

# --- ABA 2: DÉCIMO TERCEIRO ---
with aba2:
    st.header("Cálculo de 13º Salário Proporcional")
    col1, col2 = st.columns(2)
    
    with col1:
        parcela_13 = st.radio("Selecione a Parcela:", ["1ª Parcela (Adiantamento sem impostos)", "2ª Parcela / Parcela Única"], key="parc13")
        salario_13 = st.number_input("Salário Base (R$)", min_value=0.0, value=2000.00, step=100.00, key="sal2")
        meses_13 = st.number_input("Meses Trabalhados no Ano (mín. 15 dias)", min_value=1, max_value=12, value=12, key="mes2")
        adicionais_13 = st.number_input("Média de Adicionais/Comissões no Ano (R$)", min_value=0.0, value=0.00, step=50.00, key="adic2")
        dep_13 = st.number_input("Número de Dependentes", min_value=0, value=0, key="dep2")

        st.subheader("🔻 Descontos do 13º")
        adiantamento_13 = st.number_input("Adiantamento Já Pago da 1ª Parcela (R$)", min_value=0.0, value=0.00, step=100.00, key="adiant2")
        outros_desc_13 = st.number_input("Outros Descontos no 13º (R$)", min_value=0.0, value=0.00, step=10.00, key="desc_outros2")

    with col2:
        bruto_13 = ((salario_13 + adicionais_13) / 12) * meses_13
        
        if "1ª Parcela" in parcela_13:
            # 1ª parcela é 50% do bruto sem incidência de INSS e IRRF
            bruto_parcela = bruto_13 / 2
            inss_13 = 0.0
            irrf_13 = 0.0
            aliq_13 = 0.0
            liq_13 = bruto_parcela - outros_desc_13
            st.info("ℹ️ A 1ª Parcela do 13º Salário não tem incidência de INSS e IRRF.")
        else:
            # 2ª parcela calcula INSS/IRRF sobre o total e desconta o adiantamento
            inss_13 = calcular_inss_progressivo(bruto_13)
            irrf_13, aliq_13 = calcular_irrf(bruto_13, inss_13, dep_13)
            liq_13 = bruto_13 - inss_13 - irrf_13 - adiantamento_13 - outros_desc_13

        st.subheader("📊 Resumo do 13º")
        st.metric(label="13º Bruto Integral Proporcional", value=f"R$ {bruto_13:,.2f}")
        st.metric(label="Desconto INSS", value=f"R$ {inss_13:,.2f}")
        st.metric(label=f"Desconto IRRF ({aliq_13}%)", value=f"R$ {irrf_13:,.2f}")
        if adiantamento_13 > 0 and "2ª Parcela" in parcela_13:
            st.metric(label="Dedução do Adiantamento (1ª Parcela)", value=f"R$ {adiantamento_13:,.2f}")
        if outros_desc_13 > 0:
            st.metric(label="Outros Descontos", value=f"R$ {outros_desc_13:,.2f}")
            
        st.markdown("---")
        st.subheader(f"13º Líquido a Receber: R$ {liq_13:,.2f}")

# --- ABA 3: FÉRIAS ---
with aba3:
    st.header("Cálculo de Férias Proporcionais + 1/3")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📌 Entradas de Férias")
        salario_ferias = st.number_input("Salário Base (R$)", min_value=0.0, value=2000.00, step=100.00, key="sal3")
        adicionais_ferias = st.number_input("Média de Adicionais no Período (R$)", min_value=0.0, value=0.00, step=50.00, key="adic3")
        meses_ferias = st.number_input("Meses do Período Aquisitivo", min_value=1, max_value=12, value=12, key="mes3")
        dep_ferias = st.number_input("Número de Dependentes", min_value=0, value=0, key="dep3")

        st.subheader("🔻 Descontos de Férias")
        desc_faltas_ferias = st.number_input("Desconto por Faltas Não Justificadas (R$)", min_value=0.0, value=0.00, step=10.00, key="faltas3")
        outros_desc_ferias = st.number_input("Outros Descontos (R$)", min_value=0.0, value=0.00, step=10.00, key="desc_outros3")

    with col2:
        base_ferias = salario_ferias + adicionais_ferias
        ferias_simples = (base_ferias / 12) * meses_ferias
        terco = ferias_simples / 3
        total_ferias_bruto = ferias_simples + terco
        
        # Férias têm incidência de INSS e IRRF sobre o valor bruto (Férias + 1/3)
        inss_ferias = calcular_inss_progressivo(total_ferias_bruto)
        irrf_ferias, aliq_ferias = calcular_irrf(total_ferias_bruto, inss_ferias, dep_ferias)
        
        total_descontos_ferias = inss_ferias + irrf_ferias + desc_faltas_ferias + outros_desc_ferias
        total_ferias_liquido = total_ferias_bruto - total_descontos_ferias

        st.subheader("📊 Resumo das Férias")
        st.metric(label="Férias Proporcionais", value=f"R$ {ferias_simples:,.2f}")
        st.metric(label="Adicional Constitucional (1/3)", value=f"R$ {terco:,.2f}")
        st.metric(label="Total Bruto das Férias", value=f"R$ {total_ferias_bruto:,.2f}")
        st.metric(label="Desconto INSS", value=f"R$ {inss_ferias:,.2f}")
        st.metric(label=f"Desconto IRRF ({aliq_ferias}%)", value=f"R$ {irrf_ferias:,.2f}")
        
        if (desc_faltas_ferias + outros_desc_ferias) > 0:
            st.metric(label="Outros Descontos (Faltas, etc.)", value=f"R$ {(desc_faltas_ferias + outros_desc_ferias):,.2f}")
            
        st.markdown("---")
        st.subheader(f"Total Líquido de Férias: R$ {total_ferias_liquido:,.2f}")

# --- ABA 4: AVISO PRÉVIO ---
with aba4:
    st.header("Aviso Prévio Indenizado (Lei 12.506)")
    col1, col2 = st.columns(2)
    
    with col1:
        salario_aviso = st.number_input("Salário Base (R$)", min_value=0.0, value=2000.00, step=100.00, key="sal4")
        adicionais_aviso = st.number_input("Média de Adicionais (R$)", min_value=0.0, value=0.00, step=50.00, key="adic4")
        anos_trabalhados = st.number_input("Anos Completos na Empresa", min_value=0, max_value=30, value=1, key="ano4")

    with col2:
        base_aviso = salario_aviso + adicionais_aviso
        dias_aviso = min(30 + (anos_trabalhados * 3), 90)
        valor_aviso = (base_aviso / 30) * dias_aviso

        st.info(f"Direito adquirido: **{dias_aviso} dias** de aviso prévio.")
        st.subheader(f"Valor do Aviso Prévio: R$ {valor_aviso:,.2f}")

# --- ABA 5: FGTS MENSAL ---
with aba5:
    st.header("Recolhimento Mensal do FGTS")
    col1, col2 = st.columns(2)
    
    with col1:
        salario_fgts = st.number_input("Salário Bruto Total do Mês (Salário + Adicionais) (R$)", min_value=0.0, value=2000.00, step=100.00, key="sal5")

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
