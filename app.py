def calcular_irrf(rendimento_bruto, inss_pago, num_dependentes=0):
    """
    Calcula o IRRF conforme a tabela de 2026 enviada na imagem:
    1. Calcula a Base Legal (Bruto - INSS - Dependentes)
    2. Calcula a Base Simplificada (Bruto - R$ 607,20)
    3. Aplica as faixas e parcelas a deduzir na menor base
    4. Aplica os Redutores Finais conforme a faixa de renda
    """
    DEDUCAO_DEPENDENTE = 189.59
    DEDUCAO_SIMPLIFICADA = 607.20

    # 1. Base Legal x Base Simplificada (Aplica a que for melhor pro trabalhador)
    base_legal = rendimento_bruto - inss_pago - (num_dependentes * DEDUCAO_DEPENDENTE)
    base_simplificada = rendimento_bruto - DEDUCAO_SIMPLIFICADA

    base_calculo = min(base_legal, base_simplificada)

    # 2. Aplicação da Tabela Progressiva (01/2026)
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

    # 3. Aplicação dos Redutores Finais do Imposto
    if rendimento_bruto <= 5000.00:
        # Quem ganha até 5 mil e tem imposto até R$ 312,89 fica ISENTO (IR ZERADO)
        if imposto_inicial <= 312.89:
            imposto_final = 0.0
        else:
            imposto_final = imposto_inicial

    elif 5000.01 <= rendimento_bruto <= 7350.00:
        # Redutor de transição: 978,62 - (0,133145 x base tributável sem descontos)
        redutor = 978.62 - (0.133145 * rendimento_bruto)
        redutor = max(0.0, redutor)
        imposto_final = max(0.0, imposto_inicial - redutor)

    else:
        # Acima de R$ 7.350,01 -> Tabela normal sem redutor
        imposto_final = imposto_inicial

    return round(imposto_final, 2), aliquota
