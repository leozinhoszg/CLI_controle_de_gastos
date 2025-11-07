1
# Importar versão MySQL do controle financeiro
from src.controllers.controle_avancado_mysql import ControleFinanceiroAvancado, ContaBancaria, MetaGasto
from src.controllers.controle_gastos import Despesa, Receita
from datetime import datetime, date
import os
import sys

def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def obter_mes_nome(mes: int) -> str:
    """Retorna o nome do mês"""
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    return meses.get(mes, "Mês Inválido")

def validar_data(data_str: str) -> bool:
    """Valida se a data está no formato correto"""
    try:
        datetime.strptime(data_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def obter_data_valida(mensagem: str) -> str:
    """Obtém uma data válida do usuário"""
    while True:
        data = input(mensagem)
        if not data:  # Permitir data vazia
            return ""
        if validar_data(data):
            return data
        print("❌ Data inválida! Use o formato DD/MM/AAAA")

def obter_valor_valido(mensagem: str) -> float:
    """Obtém um valor monetário válido do usuário"""
    while True:
        try:
            valor = float(input(mensagem).replace(',', '.'))
            if valor < 0:
                print("❌ O valor não pode ser negativo!")
                continue
            return valor
        except ValueError:
            print("❌ Valor inválido! Digite um número válido.")

def obter_mes_ano():
    """Obtém mês e ano do usuário"""
    while True:
        try:
            mes = int(input("Digite o mês (1-12): "))
            if mes < 1 or mes > 12:
                print("❌ Mês inválido! Digite um número entre 1 e 12.")
                continue
            
            ano = int(input("Digite o ano (ex: 2024): "))
            if ano < 2000 or ano > 2100:
                print("❌ Ano inválido! Digite um ano entre 2000 e 2100.")
                continue
            
            return mes, ano
        except ValueError:
            print("❌ Valor inválido! Digite números válidos.")

def mostrar_cabecalho():
    """Mostra o cabeçalho do sistema"""
    print("="*70)
    print("        💰 SISTEMA AVANÇADO DE CONTROLE DE GASTOS 💰")
    print("="*70)

def menu_principal():
    """Mostra o menu principal"""
    print("\n📋 MENU PRINCIPAL:")
    print("1️⃣  - Gerenciar Contas Bancárias")
    print("2️⃣  - Gerenciar Despesas")
    print("3️⃣  - Gerenciar Receitas")
    print("4️⃣  - Metas de Gastos")
    print("5️⃣  - Busca e Filtros")
    print("6️⃣  - Relatórios e Gráficos")
    print("7️⃣  - Alertas e Notificações")
    print("8️⃣  - Exportar Dados")
    print("9️⃣  - Limpar Dados")
    print("0️⃣  - Sair")
    print("-"*50)

def menu_contas():
    """Menu de gerenciamento de contas bancárias"""
    print("\n🏦 GERENCIAR CONTAS BANCÁRIAS:")
    print("1️⃣  - Criar Nova Conta")
    print("2️⃣  - Listar Contas")
    print("3️⃣  - Atualizar Saldo")
    print("4️⃣  - Histórico de Saldo")
    print("5️⃣  - Editar Conta")
    print("6️⃣  - Remover Conta")
    print("7️⃣  - Definir Conta Padrão")
    print("8️⃣  - Gerenciar Carteira")
    print("9️⃣  - Transferir Entre Contas")
    print("0️⃣  - Voltar")
    print("-"*40)

def menu_despesas():
    """Mostra o menu de despesas"""
    print("\n💸 GERENCIAR DESPESAS:")
    print("1️⃣  - Adicionar Despesa")
    print("2️⃣  - Listar Despesas")
    print("3️⃣  - Pagar Despesa (Saldo Automático)")
    print("4️⃣  - Marcar como Pago/Não Pago")
    print("5️⃣  - Remover Despesa")
    print("0️⃣  - Voltar")
    print("-"*40)

def menu_receitas():
    """Mostra o menu de receitas"""
    print("\n💰 GERENCIAR RECEITAS:")
    print("1️⃣  - Adicionar Receita")
    print("2️⃣  - Processar Receita (Saldo Automático)")
    print("3️⃣  - Listar Receitas")
    print("4️⃣  - Remover Receita")
    print("0️⃣  - Voltar")
    print("-"*40)

def menu_busca():
    """Menu de busca e filtros"""
    print("\n🔍 BUSCA E FILTROS:")
    print("1️⃣  - Buscar Despesas")
    print("2️⃣  - Buscar Receitas")
    print("3️⃣  - Despesas Vencendo")
    print("0️⃣  - Voltar")
    print("-"*40)

def menu_relatorios():
    """Menu de relatórios e gráficos"""
    print("\n📊 RELATÓRIOS E GRÁFICOS:")
    print("1️⃣  - Relatório Mensal Completo")
    print("2️⃣  - Gráfico de Gastos por Categoria")
    print("3️⃣  - Gráfico Comparativo Mensal")
    print("4️⃣  - Análise por Categoria")
    print("5️⃣  - Relatório de Contas")
    print("0️⃣  - Voltar")
    print("-"*40)

def criar_conta_bancaria(controle: ControleFinanceiroAvancado):
    """Cria uma nova conta bancária"""
    print("\n🏦 CRIAR NOVA CONTA BANCÁRIA")
    print("-"*40)
    
    nome = input("Nome da conta: ")
    if not nome:
        print("❌ Nome da conta é obrigatório!")
        input("\nPressione Enter para continuar...")
        return
    
    if nome in controle.obter_contas_bancarias():
        print(f"❌ Conta '{nome}' já existe!")
        input("\nPressione Enter para continuar...")
        return
    
    banco = input("Nome do banco: ") or "Banco"
    saldo_inicial = obter_valor_valido("Saldo inicial (R$): ")
    
    try:
        controle.criar_conta_bancaria(nome, banco, saldo_inicial)
        print(f"\n✅ Conta '{nome}' criada com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar conta: {e}")
    
    input("\nPressione Enter para continuar...")

def listar_contas(controle: ControleFinanceiroAvancado):
    """Lista todas as contas bancárias"""
    print("\n🏦 CONTAS BANCÁRIAS")
    print("-"*50)
    
    contas = controle.obter_contas_bancarias()
    if not contas:
        print("❌ Nenhuma conta bancária encontrada.")
    else:
        total_saldo = 0
        for i, nome_conta in enumerate(contas, 1):
            conta = controle.contas_bancarias[nome_conta]
            saldo = conta.saldo_atual
            total_saldo += saldo
            
            padrao = " (PADRÃO)" if nome_conta == controle.conta_padrao else ""
            print(f"{i:2d}. {nome_conta}{padrao}")
            print(f"    🏛️ Banco: {conta.banco}")
            print(f"    💰 Saldo: R$ {saldo:.2f}")
            print(f"    📊 Histórico: {len(conta.historico_saldo)} movimentações")
            print("-"*30)
        
        print(f"\n💰 SALDO TOTAL: R$ {total_saldo:.2f}")
    
    input("\nPressione Enter para continuar...")

def atualizar_saldo_conta(controle: ControleFinanceiroAvancado):
    """Atualiza o saldo de uma conta"""
    print("\n💰 ATUALIZAR SALDO DA CONTA")
    print("-"*40)
    
    contas = controle.obter_contas_bancarias()
    if not contas:
        print("❌ Nenhuma conta bancária encontrada.")
        input("\nPressione Enter para continuar...")
        return
    
    print("Contas disponíveis:")
    for i, nome_conta in enumerate(contas, 1):
        saldo = controle.obter_saldo_conta(nome_conta)
        print(f"{i:2d}. {nome_conta} - R$ {saldo:.2f}")
    
    try:
        escolha = int(input("\nEscolha a conta (0 para cancelar): "))
        if escolha == 0:
            return
        
        if escolha < 1 or escolha > len(contas):
            print("❌ Opção inválida!")
            input("\nPressione Enter para continuar...")
            return
        
        nome_conta = contas[escolha - 1]
        saldo_atual = controle.obter_saldo_conta(nome_conta)
        
        print(f"\nConta: {nome_conta}")
        print(f"Saldo atual: R$ {saldo_atual:.2f}")
        
        novo_saldo = obter_valor_valido("Novo saldo (R$): ")
        operacao = input("Descrição da operação (opcional): ") or "Atualização manual"
        
        controle.atualizar_saldo_conta(nome_conta, novo_saldo, operacao)
        
        diferenca = novo_saldo - saldo_atual
        if diferenca > 0:
            print(f"\n✅ Saldo atualizado! Aumento de R$ {diferenca:.2f}")
        elif diferenca < 0:
            print(f"\n✅ Saldo atualizado! Redução de R$ {abs(diferenca):.2f}")
        else:
            print("\n✅ Saldo mantido igual.")
        
    except ValueError:
        print("❌ Opção inválida!")
    
    input("\nPressione Enter para continuar...")

def mostrar_historico_saldo(controle: ControleFinanceiroAvancado):
    """Mostra o histórico de saldo de uma conta"""
    print("\n📊 HISTÓRICO DE SALDO")
    print("-"*40)
    
    contas = controle.obter_contas_bancarias()
    if not contas:
        print("❌ Nenhuma conta bancária encontrada.")
        input("\nPressione Enter para continuar...")
        return
    
    print("Contas disponíveis:")
    for i, nome_conta in enumerate(contas, 1):
        print(f"{i:2d}. {nome_conta}")
    
    try:
        escolha = int(input("\nEscolha a conta (0 para cancelar): "))
        if escolha == 0:
            return
        
        if escolha < 1 or escolha > len(contas):
            print("❌ Opção inválida!")
            input("\nPressione Enter para continuar...")
            return
        
        nome_conta = contas[escolha - 1]
        conta = controle.contas_bancarias[nome_conta]
        
        print(f"\n📊 HISTÓRICO DA CONTA: {nome_conta}")
        print("="*60)
        
        if not conta.historico_saldo:
            print("❌ Nenhum histórico encontrado.")
        else:
            for i, movimento in enumerate(reversed(conta.historico_saldo[-10:]), 1):  # Últimos 10
                data = datetime.fromisoformat(movimento['data']).strftime("%d/%m/%Y %H:%M")
                print(f"{i:2d}. {data}")
                print(f"    📝 Operação: {movimento['operacao']}")
                print(f"    💰 Saldo: R$ {movimento['saldo_anterior']:.2f} → R$ {movimento['saldo_novo']:.2f}")
                if movimento['valor'] != 0:
                    sinal = "+" if movimento['valor'] > 0 else ""
                    print(f"    🔄 Variação: {sinal}R$ {movimento['valor']:.2f}")
                print("-"*40)
            
            if len(conta.historico_saldo) > 10:
                print(f"... e mais {len(conta.historico_saldo) - 10} movimentações anteriores")
        
    except ValueError:
        print("❌ Opção inválida!")
    
    input("\nPressione Enter para continuar...")

def pagar_despesa_automatico(controle: ControleFinanceiroAvancado):
    """Paga uma despesa atualizando automaticamente o saldo"""
    print("\n💳 PAGAR DESPESA (SALDO AUTOMÁTICO)")
    print("-"*45)
    
    print("Para qual mês?")
    mes, ano = obter_mes_ano()
    
    despesas = controle.obter_despesas_mes(mes, ano)
    despesas_nao_pagas = [d for d in despesas if not d.pago]
    
    if not despesas_nao_pagas:
        print(f"\n❌ Nenhuma despesa pendente encontrada para {obter_mes_nome(mes)}/{ano}")
        input("\nPressione Enter para continuar...")
        return
    
    print(f"\n💸 DESPESAS PENDENTES - {obter_mes_nome(mes).upper()}/{ano}:")
    for i, despesa in enumerate(despesas_nao_pagas, 1):
        print(f"{i:2d}. {despesa.descricao} - R$ {despesa.valor:.2f}")
        print(f"    📅 Vencimento: {despesa.data_vencimento.strftime('%d/%m/%Y')}")
    
    try:
        escolha = int(input("\nEscolha a despesa para pagar (0 para cancelar): "))
        if escolha == 0:
            return
        
        if escolha < 1 or escolha > len(despesas_nao_pagas):
            print("❌ Opção inválida!")
            input("\nPressione Enter para continuar...")
            return
        
        despesa_selecionada = despesas_nao_pagas[escolha - 1]
        
        # Escolher conta para débito
        contas = controle.obter_contas_bancarias()
        print("\nEscolha a conta para débito:")
        for i, nome_conta in enumerate(contas, 1):
            saldo = controle.obter_saldo_conta(nome_conta)
            print(f"{i:2d}. {nome_conta} - R$ {saldo:.2f}")
        
        try:
            escolha_conta = int(input("\nEscolha a conta (0 para usar padrão): "))
            
            if escolha_conta == 0:
                nome_conta = controle.conta_padrao
                print(f"💳 Usando conta padrão: {nome_conta}")
            elif escolha_conta < 1 or escolha_conta > len(contas):
                print("❌ Conta inválida! Usando conta padrão.")
                nome_conta = controle.conta_padrao
            else:
                nome_conta = contas[escolha_conta - 1]
                print(f"💳 Conta selecionada: {nome_conta}")
        except ValueError:
            print("❌ Entrada inválida! Usando conta padrão.")
            nome_conta = controle.conta_padrao
        
        saldo_atual = controle.obter_saldo_conta(nome_conta)
        
        if saldo_atual < despesa_selecionada.valor:
            print(f"\n⚠️ ATENÇÃO: Saldo insuficiente!")
            print(f"Saldo atual: R$ {saldo_atual:.2f}")
            print(f"Valor da despesa: R$ {despesa_selecionada.valor:.2f}")
            print(f"Faltam: R$ {despesa_selecionada.valor - saldo_atual:.2f}")
            
            confirmar = input("\nDeseja pagar mesmo assim? (s/N): ").lower()
            if confirmar != 's':
                return
        
        # Processar pagamento
        controle.processar_pagamento_despesa(despesa_selecionada, nome_conta)
        
        novo_saldo = controle.obter_saldo_conta(nome_conta)
        
        print(f"\n✅ Despesa '{despesa_selecionada.descricao}' paga com sucesso!")
        print(f"💳 Conta: {nome_conta}")
        print(f"💰 Saldo anterior: R$ {saldo_atual:.2f}")
        print(f"💰 Saldo atual: R$ {novo_saldo:.2f}")
        
    except ValueError as e:
        print(f"❌ Entrada inválida: {e}")
    except Exception as e:
        print(f"❌ Erro ao processar pagamento: {e}")
    
    input("\nPressione Enter para continuar...")

def processar_receita_automatico(controle: ControleFinanceiroAvancado):
    """Processa uma receita atualizando automaticamente o saldo"""
    print("\n💰 PROCESSAR RECEITA (SALDO AUTOMÁTICO)")
    print("-"*50)
    
    descricao = input("Descrição da receita: ")
    valor = obter_valor_valido("Valor (R$): ")
    data_recebimento = obter_data_valida("Data de recebimento (DD/MM/AAAA): ")
    categoria = input("Categoria (opcional): ") or "Receita"
    
    print("\nEm qual mês deseja adicionar esta receita?")
    mes, ano = obter_mes_ano()
    
    # Escolher conta para crédito
    contas = controle.obter_contas_bancarias()
    print("\nEscolha a conta para crédito:")
    for i, nome_conta in enumerate(contas, 1):
        saldo = controle.obter_saldo_conta(nome_conta)
        print(f"{i:2d}. {nome_conta} - R$ {saldo:.2f}")
    
    try:
        try:
            escolha_conta = int(input("\nEscolha a conta (0 para usar padrão): "))
            
            if escolha_conta == 0:
                nome_conta = controle.conta_padrao
                print(f"💳 Usando conta padrão: {nome_conta}")
            elif escolha_conta < 1 or escolha_conta > len(contas):
                print("❌ Conta inválida! Usando conta padrão.")
                nome_conta = controle.conta_padrao
            else:
                nome_conta = contas[escolha_conta - 1]
                print(f"💳 Conta selecionada: {nome_conta}")
        except ValueError:
            print("❌ Entrada inválida! Usando conta padrão.")
            nome_conta = controle.conta_padrao
        
        saldo_atual = controle.obter_saldo_conta(nome_conta)
        
        # Criar e processar receita
        receita = Receita(descricao, valor, data_recebimento, categoria)
        controle.adicionar_receita(receita, mes, ano)
        controle.processar_receita(receita, nome_conta)
        
        novo_saldo = controle.obter_saldo_conta(nome_conta)
        
        print(f"\n✅ Receita '{descricao}' processada com sucesso!")
        print(f"💳 Conta: {nome_conta}")
        print(f"💰 Saldo anterior: R$ {saldo_atual:.2f}")
        print(f"💰 Saldo atual: R$ {novo_saldo:.2f}")
        
    except Exception as e:
        print(f"❌ Erro ao processar receita: {e}")
    
    input("\nPressione Enter para continuar...")

def buscar_despesas_avancado(controle: ControleFinanceiroAvancado):
    """Busca avançada de despesas"""
    print("\n🔍 BUSCA AVANÇADA DE DESPESAS")
    print("-"*40)
    
    termo = input("Termo na descrição (opcional): ")
    categoria = input("Categoria (opcional): ")
    
    valor_min_str = input("Valor mínimo (opcional): ")
    valor_min = float(valor_min_str.replace(',', '.')) if valor_min_str else 0
    
    valor_max_str = input("Valor máximo (opcional): ")
    valor_max = float(valor_max_str.replace(',', '.')) if valor_max_str else float('inf')
    
    print("\nStatus de pagamento:")
    print("1 - Apenas pagas")
    print("2 - Apenas pendentes")
    print("3 - Todas")
    
    try:
        status_opcao = int(input("Escolha (3 para todas): ") or "3")
        if status_opcao == 1:
            apenas_pagas = True
        elif status_opcao == 2:
            apenas_pagas = False
        else:
            apenas_pagas = None
    except ValueError:
        apenas_pagas = None
    
    data_inicio = obter_data_valida("Data início (DD/MM/AAAA, opcional): ")
    data_fim = obter_data_valida("Data fim (DD/MM/AAAA, opcional): ")
    
    # Realizar busca
    resultados = controle.buscar_despesas(
        termo=termo,
        categoria=categoria,
        valor_min=valor_min,
        valor_max=valor_max,
        apenas_pagas=apenas_pagas,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    
    print(f"\n🔍 RESULTADOS DA BUSCA ({len(resultados)} encontrados):")
    print("="*60)
    
    if not resultados:
        print("❌ Nenhuma despesa encontrada com os critérios especificados.")
    else:
        total_valor = 0
        for i, (despesa, mes, ano) in enumerate(resultados, 1):
            status = "✅ PAGO" if despesa.pago else "❌ PENDENTE"
            print(f"{i:2d}. {despesa.descricao}")
            print(f"    💰 Valor: R$ {despesa.valor:.2f}")
            print(f"    📅 Vencimento: {despesa.data_vencimento.strftime('%d/%m/%Y')}")
            print(f"    📂 Categoria: {despesa.categoria}")
            print(f"    📆 Mês/Ano: {obter_mes_nome(mes)}/{ano}")
            print(f"    🔄 Status: {status}")
            print("-"*40)
            total_valor += despesa.valor
        
        print(f"\n💰 VALOR TOTAL: R$ {total_valor:.2f}")
    
    input("\nPressione Enter para continuar...")

def buscar_receitas_avancado(controle: ControleFinanceiroAvancado):
    """Busca avançada de receitas"""
    print("\n🔍 BUSCA AVANÇADA DE RECEITAS")
    print("-"*40)
    
    termo = input("Termo na descrição (opcional): ")
    categoria = input("Categoria (opcional): ")
    
    valor_min_str = input("Valor mínimo (opcional): ")
    valor_min = float(valor_min_str.replace(',', '.')) if valor_min_str else 0
    
    valor_max_str = input("Valor máximo (opcional): ")
    valor_max = float(valor_max_str.replace(',', '.')) if valor_max_str else float('inf')
    
    data_inicio = obter_data_valida("Data início (DD/MM/AAAA, opcional): ")
    data_fim = obter_data_valida("Data fim (DD/MM/AAAA, opcional): ")
    
    # Realizar busca
    try:
        resultados = controle.buscar_receitas(
            termo=termo,
            categoria=categoria,
            valor_min=valor_min,
            valor_max=valor_max,
            data_inicio=data_inicio,
            data_fim=data_fim
        )
        
        print(f"\n🔍 RESULTADOS DA BUSCA ({len(resultados)} encontrados):")
        print("="*60)
        
        if not resultados:
            print("❌ Nenhuma receita encontrada com os critérios especificados.")
        else:
            total_valor = 0
            for i, (receita, mes, ano) in enumerate(resultados, 1):
                print(f"{i:2d}. {receita.descricao}")
                print(f"    💰 Valor: R$ {receita.valor:.2f}")
                print(f"    📅 Data de Recebimento: {receita.data_recebimento.strftime('%d/%m/%Y')}")
                print(f"    📂 Categoria: {receita.categoria}")
                print(f"    📆 Mês/Ano: {obter_mes_nome(mes)}/{ano}")
                print("-"*40)
                total_valor += receita.valor
            
            print(f"\n💰 VALOR TOTAL: R$ {total_valor:.2f}")
    
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    
    input("\nPressione Enter para continuar...")

def mostrar_despesas_vencendo(controle: ControleFinanceiroAvancado):
    """Mostra despesas que estão vencendo"""
    print("\n⏰ DESPESAS VENCENDO")
    print("-"*30)
    
    try:
        dias = int(input("Vencimento nos próximos quantos dias? (padrão 7): ") or "7")
    except ValueError:
        dias = 7
    
    despesas_vencendo = controle.obter_despesas_vencendo(dias)
    
    if not despesas_vencendo:
        print(f"\n✅ Nenhuma despesa vencendo nos próximos {dias} dias!")
    else:
        print(f"\n⚠️ DESPESAS VENCENDO NOS PRÓXIMOS {dias} DIAS:")
        print("="*60)
        
        hoje = date.today()
        total_valor = 0
        
        for i, (despesa, mes, ano) in enumerate(despesas_vencendo, 1):
            dias_vencimento = (despesa.data_vencimento - hoje).days
            
            if dias_vencimento < 0:
                status_venc = f"❗ VENCIDA há {abs(dias_vencimento)} dias"
            elif dias_vencimento == 0:
                status_venc = "🔥 VENCE HOJE"
            elif dias_vencimento == 1:
                status_venc = "⚠️ VENCE AMANHÃ"
            else:
                status_venc = f"📅 Vence em {dias_vencimento} dias"
            
            print(f"{i:2d}. {despesa.descricao}")
            print(f"    💰 Valor: R$ {despesa.valor:.2f}")
            print(f"    📅 Vencimento: {despesa.data_vencimento.strftime('%d/%m/%Y')}")
            print(f"    📂 Categoria: {despesa.categoria}")
            print(f"    📆 Mês/Ano: {obter_mes_nome(mes)}/{ano}")
            print(f"    ⏰ Status: {status_venc}")
            print("-"*40)
            total_valor += despesa.valor
        
        print(f"\n💰 VALOR TOTAL: R$ {total_valor:.2f}")
    
    input("\nPressione Enter para continuar...")

def gerar_grafico_categoria(controle: ControleFinanceiroAvancado):
    """Gera gráfico de gastos por categoria"""
    print("\n📊 GRÁFICO DE GASTOS POR CATEGORIA")
    print("-"*45)
    
    print("Para qual mês deseja gerar o gráfico?")
    mes, ano = obter_mes_ano()
    
    try:
        print("\n📊 Gerando gráfico...")
        controle.gerar_grafico_gastos_categoria(mes, ano, salvar_arquivo=True)
        print("✅ Gráfico gerado com sucesso!")
    except ImportError:
        print("❌ Matplotlib não está instalado. Execute: pip install matplotlib")
    except Exception as e:
        print(f"❌ Erro ao gerar gráfico: {e}")
    
    input("\nPressione Enter para continuar...")

def gerar_grafico_comparativo(controle: ControleFinanceiroAvancado):
    """Gera gráfico comparativo mensal"""
    print("\n📊 GRÁFICO COMPARATIVO MENSAL")
    print("-"*40)
    
    try:
        ano = int(input("Digite o ano para comparação: "))
        print("\n📊 Gerando gráfico comparativo...")
        controle.gerar_grafico_comparativo_mensal(ano, salvar_arquivo=True)
        print("✅ Gráfico gerado com sucesso!")
    except ImportError:
        print("❌ Matplotlib não está instalado. Execute: pip install matplotlib")
    except ValueError:
        print("❌ Ano inválido!")
    except Exception as e:
        print(f"❌ Erro ao gerar gráfico: {e}")
    
    input("\nPressione Enter para continuar...")

def remover_conta_bancaria(controle: ControleFinanceiroAvancado):
    """Remove uma conta bancária"""
    print("\n🗑️ REMOVER CONTA BANCÁRIA")
    print("-"*30)
    
    contas = controle.obter_contas_bancarias()
    if not contas:
        print("❌ Nenhuma conta bancária encontrada.")
        input("\nPressione Enter para continuar...")
        return
    
    if len(contas) == 1:
        print("❌ Não é possível remover a única conta bancária do sistema.")
        print("💡 Dica: Crie outra conta antes de remover esta.")
        input("\nPressione Enter para continuar...")
        return
    
    print("\n🏦 CONTAS DISPONÍVEIS:")
    for i, nome_conta in enumerate(contas, 1):
        saldo = controle.obter_saldo_conta(nome_conta)
        conta = controle.contas_bancarias[nome_conta]
        padrao = " (PADRÃO)" if nome_conta == controle.conta_padrao else ""
        print(f"{i:2d}. {nome_conta}{padrao} - {conta.banco} - R$ {saldo:.2f}")
    
    try:
        escolha = int(input("\nEscolha a conta para remover (0 para cancelar): "))
        if escolha == 0:
            return
        
        if escolha < 1 or escolha > len(contas):
            print("❌ Opção inválida!")
            input("\nPressione Enter para continuar...")
            return
        
        nome_conta_remover = contas[escolha - 1]
        conta = controle.contas_bancarias[nome_conta_remover]
        saldo = controle.obter_saldo_conta(nome_conta_remover)
        
        # Mostrar informações da conta
        print(f"\n📋 INFORMAÇÕES DA CONTA:")
        print(f"Nome: {nome_conta_remover}")
        print(f"Banco: {conta.banco}")
        print(f"Saldo atual: R$ {saldo:.2f}")
        
        # Avisos importantes
        if nome_conta_remover == controle.conta_padrao:
            print("\n⚠️ ATENÇÃO: Esta é a conta padrão do sistema!")
            print("A conta padrão será alterada automaticamente.")
        
        if saldo != 0:
            print(f"\n⚠️ ATENÇÃO: A conta possui saldo de R$ {saldo:.2f}!")
            print("O saldo será perdido ao remover a conta.")
        
        # Confirmação dupla
        print(f"\n❓ Tem certeza que deseja remover a conta '{nome_conta_remover}'?")
        confirmacao1 = input("Digite 'SIM' para confirmar (ou qualquer coisa para cancelar): ").upper()
        
        if confirmacao1 != 'SIM':
            print("❌ Operação cancelada.")
            input("\nPressione Enter para continuar...")
            return
        
        print(f"\n⚠️ ÚLTIMA CONFIRMAÇÃO: Remover '{nome_conta_remover}' PERMANENTEMENTE?")
        confirmacao2 = input("Digite 'CONFIRMAR' para prosseguir: ").upper()
        
        if confirmacao2 != 'CONFIRMAR':
            print("❌ Operação cancelada.")
            input("\nPressione Enter para continuar...")
            return
        
        # Remover conta
        sucesso = controle.remover_conta_bancaria(nome_conta_remover)
        
        if sucesso:
            print(f"\n✅ Conta '{nome_conta_remover}' removida com sucesso!")
            if nome_conta_remover != controle.conta_padrao:
                print(f"💡 Nova conta padrão: {controle.conta_padrao}")
        else:
            print("\n❌ Erro ao remover conta bancária!")
        
    except ValueError:
        print("❌ Opção inválida!")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    input("\nPressione Enter para continuar...")

def editar_conta_avancado(controle: ControleFinanceiroAvancado):
    """Edita uma conta bancária"""
    print("\n✏️ EDITAR CONTA BANCÁRIA")
    print("-"*30)
    
    contas = controle.obter_contas_bancarias()
    if not contas:
        print("❌ Nenhuma conta bancária encontrada.")
        input("\nPressione Enter para continuar...")
        return
    
    print("\n🏦 CONTAS DISPONÍVEIS:")
    for i, nome_conta in enumerate(contas, 1):
        conta = controle.contas_bancarias[nome_conta]
        padrao = " (PADRÃO)" if nome_conta == controle.conta_padrao else ""
        print(f"{i:2d}. {nome_conta}{padrao} - {conta.banco} - R$ {conta.saldo_atual:.2f}")
    
    try:
        escolha = int(input("\nEscolha a conta para editar (0 para cancelar): "))
        if escolha == 0:
            return
        
        if escolha < 1 or escolha > len(contas):
            print("❌ Opção inválida!")
            input("\nPressione Enter para continuar...")
            return
        
        nome_conta_atual = contas[escolha - 1]
        conta = controle.contas_bancarias[nome_conta_atual]
        
        print(f"\n✏️ EDITANDO: {nome_conta_atual}")
        print("(Deixe em branco para manter o valor atual)")
        
        # Novo nome
        print(f"\nNome atual: {nome_conta_atual}")
        novo_nome = input("Novo nome da conta: ").strip()
        if not novo_nome:
            novo_nome = None
        elif novo_nome in controle.contas_bancarias and novo_nome != nome_conta_atual:
            print("❌ Já existe uma conta com este nome!")
            input("\nPressione Enter para continuar...")
            return
        
        # Novo banco
        print(f"\nBanco atual: {conta.banco}")
        novo_banco = input("Novo banco: ").strip()
        if not novo_banco:
            novo_banco = None
        
        # Confirmar alterações
        if novo_nome or novo_banco:
            print("\n📋 RESUMO DAS ALTERAÇÕES:")
            if novo_nome:
                print(f"Nome: {nome_conta_atual} → {novo_nome}")
            if novo_banco:
                print(f"Banco: {conta.banco} → {novo_banco}")
            
            confirmacao = input("\n❓ Confirmar alterações? (s/N): ").lower()
            if confirmacao != 's':
                print("❌ Operação cancelada.")
                input("\nPressione Enter para continuar...")
                return
            
            # Aplicar edições
            sucesso = controle.editar_conta_bancaria(nome_conta_atual, novo_nome, novo_banco)
            
            if sucesso:
                nome_final = novo_nome if novo_nome else nome_conta_atual
                print(f"\n✅ Conta '{nome_final}' editada com sucesso!")
            else:
                print("\n❌ Erro ao editar conta! (Nome pode já existir)")
        else:
            print("\n💡 Nenhuma alteração foi feita.")
        
    except ValueError:
        print("❌ Opção inválida!")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    input("\nPressione Enter para continuar...")

def gerenciar_carteira(controle: ControleFinanceiroAvancado):
    """Gerencia a carteira (dinheiro em espécie)"""
    while True:
        limpar_tela()
        mostrar_cabecalho()
        
        # Mostrar saldo atual da carteira
        saldo_carteira = controle.obter_saldo_carteira()
        print(f"\n💰 CARTEIRA (Dinheiro em Espécie)")
        print(f"💵 Saldo atual: R$ {saldo_carteira:.2f}")
        print("-"*40)
        
        print("\n🏦 GERENCIAR CARTEIRA:")
        print("1️⃣  - Adicionar Dinheiro")
        print("2️⃣  - Remover Dinheiro")
        print("3️⃣  - Transferir de Conta para Carteira")
        print("4️⃣  - Transferir da Carteira para Conta")
        print("5️⃣  - Ver Histórico da Carteira")
        print("0️⃣  - Voltar")
        print("-"*40)
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            adicionar_dinheiro_carteira(controle)
        elif opcao == "2":
            remover_dinheiro_carteira(controle)
        elif opcao == "3":
            transferir_para_carteira(controle)
        elif opcao == "4":
            transferir_da_carteira(controle)
        elif opcao == "5":
            ver_historico_carteira(controle)
        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida!")
            input("\nPressione Enter para continuar...")

def adicionar_dinheiro_carteira(controle: ControleFinanceiroAvancado):
    """Adiciona dinheiro à carteira"""
    print("\n💰 ADICIONAR DINHEIRO À CARTEIRA")
    print("-"*35)
    
    saldo_atual = controle.obter_saldo_carteira()
    print(f"💵 Saldo atual da carteira: R$ {saldo_atual:.2f}")
    
    try:
        valor = float(input("\n💵 Valor a adicionar (R$): ").replace(',', '.'))
        if valor <= 0:
            print("❌ Valor deve ser positivo!")
            input("\nPressione Enter para continuar...")
            return
        
        descricao = input("📝 Descrição (opcional): ").strip()
        if not descricao:
            descricao = "Adição de dinheiro à carteira"
        
        sucesso = controle.adicionar_dinheiro_carteira(valor, descricao)
        
        if sucesso:
            novo_saldo = controle.obter_saldo_carteira()
            print(f"\n✅ Dinheiro adicionado com sucesso!")
            print(f"💰 Saldo anterior: R$ {saldo_atual:.2f}")
            print(f"💰 Saldo atual: R$ {novo_saldo:.2f}")
        else:
            print("\n❌ Erro ao adicionar dinheiro à carteira!")
        
    except ValueError:
        print("❌ Valor inválido!")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    input("\nPressione Enter para continuar...")

def remover_dinheiro_carteira(controle: ControleFinanceiroAvancado):
    """Remove dinheiro da carteira"""
    print("\n💸 REMOVER DINHEIRO DA CARTEIRA")
    print("-"*35)
    
    saldo_atual = controle.obter_saldo_carteira()
    print(f"💵 Saldo atual da carteira: R$ {saldo_atual:.2f}")
    
    if saldo_atual <= 0:
        print("❌ Não há dinheiro na carteira para remover!")
        input("\nPressione Enter para continuar...")
        return
    
    try:
        valor = float(input("\n💸 Valor a remover (R$): ").replace(',', '.'))
        if valor <= 0:
            print("❌ Valor deve ser positivo!")
            input("\nPressione Enter para continuar...")
            return
        
        if valor > saldo_atual:
            print(f"❌ Saldo insuficiente! Disponível: R$ {saldo_atual:.2f}")
            input("\nPressione Enter para continuar...")
            return
        
        descricao = input("📝 Descrição (opcional): ").strip()
        if not descricao:
            descricao = "Retirada de dinheiro da carteira"
        
        sucesso = controle.remover_dinheiro_carteira(valor, descricao)
        
        if sucesso:
            novo_saldo = controle.obter_saldo_carteira()
            print(f"\n✅ Dinheiro removido com sucesso!")
            print(f"💰 Saldo anterior: R$ {saldo_atual:.2f}")
            print(f"💰 Saldo atual: R$ {novo_saldo:.2f}")
        else:
            print("\n❌ Erro ao remover dinheiro da carteira!")
        
    except ValueError:
        print("❌ Valor inválido!")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    input("\nPressione Enter para continuar...")

def transferir_para_carteira(controle: ControleFinanceiroAvancado):
    """Transfere dinheiro de uma conta bancária para a carteira"""
    print("\n🏦➡️💰 TRANSFERIR PARA CARTEIRA")
    print("-"*35)
    
    contas = [nome for nome in controle.obter_contas_bancarias() if nome != "Carteira"]
    if not contas:
        print("❌ Nenhuma conta bancária disponível para transferência!")
        input("\nPressione Enter para continuar...")
        return
    
    print("\n🏦 CONTAS DISPONÍVEIS:")
    for i, nome_conta in enumerate(contas, 1):
        saldo = controle.obter_saldo_conta(nome_conta)
        print(f"{i:2d}. {nome_conta} - R$ {saldo:.2f}")
    
    try:
        escolha = int(input("\nEscolha a conta origem (0 para cancelar): "))
        if escolha == 0:
            return
        
        if escolha < 1 or escolha > len(contas):
            print("❌ Opção inválida!")
            input("\nPressione Enter para continuar...")
            return
        
        conta_origem = contas[escolha - 1]
        saldo_origem = controle.obter_saldo_conta(conta_origem)
        
        print(f"\n💰 Saldo da {conta_origem}: R$ {saldo_origem:.2f}")
        
        valor = float(input("💸 Valor a transferir (R$): ").replace(',', '.'))
        if valor <= 0:
            print("❌ Valor deve ser positivo!")
            input("\nPressione Enter para continuar...")
            return
        
        if valor > saldo_origem:
            print(f"❌ Saldo insuficiente na {conta_origem}!")
            input("\nPressione Enter para continuar...")
            return
        
        sucesso = controle.transferir_para_carteira(conta_origem, valor)
        
        if sucesso:
            novo_saldo_origem = controle.obter_saldo_conta(conta_origem)
            novo_saldo_carteira = controle.obter_saldo_carteira()
            
            print(f"\n✅ Transferência realizada com sucesso!")
            print(f"🏦 {conta_origem}: R$ {saldo_origem:.2f} → R$ {novo_saldo_origem:.2f}")
            print(f"💰 Carteira: R$ {novo_saldo_carteira - valor:.2f} → R$ {novo_saldo_carteira:.2f}")
        else:
            print("\n❌ Erro ao realizar transferência!")
        
    except ValueError:
        print("❌ Valor inválido!")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    input("\nPressione Enter para continuar...")

def transferir_da_carteira(controle: ControleFinanceiroAvancado):
    """Transfere dinheiro da carteira para uma conta bancária"""
    print("\n💰➡️🏦 TRANSFERIR DA CARTEIRA")
    print("-"*35)
    
    saldo_carteira = controle.obter_saldo_carteira()
    print(f"💵 Saldo da carteira: R$ {saldo_carteira:.2f}")
    
    if saldo_carteira <= 0:
        print("❌ Não há dinheiro na carteira para transferir!")
        input("\nPressione Enter para continuar...")
        return
    
    contas = [nome for nome in controle.obter_contas_bancarias() if nome != "Carteira"]
    if not contas:
        print("❌ Nenhuma conta bancária disponível para transferência!")
        input("\nPressione Enter para continuar...")
        return
    
    print("\n🏦 CONTAS DISPONÍVEIS:")
    for i, nome_conta in enumerate(contas, 1):
        saldo = controle.obter_saldo_conta(nome_conta)
        print(f"{i:2d}. {nome_conta} - R$ {saldo:.2f}")
    
    try:
        escolha = int(input("\nEscolha a conta destino (0 para cancelar): "))
        if escolha == 0:
            return
        
        if escolha < 1 or escolha > len(contas):
            print("❌ Opção inválida!")
            input("\nPressione Enter para continuar...")
            return
        
        conta_destino = contas[escolha - 1]
        saldo_destino = controle.obter_saldo_conta(conta_destino)
        
        valor = float(input("💸 Valor a transferir (R$): ").replace(',', '.'))
        if valor <= 0:
            print("❌ Valor deve ser positivo!")
            input("\nPressione Enter para continuar...")
            return
        
        if valor > saldo_carteira:
            print(f"❌ Saldo insuficiente na carteira!")
            input("\nPressione Enter para continuar...")
            return
        
        sucesso = controle.transferir_da_carteira(conta_destino, valor)
        
        if sucesso:
            novo_saldo_carteira = controle.obter_saldo_carteira()
            novo_saldo_destino = controle.obter_saldo_conta(conta_destino)
            
            print(f"\n✅ Transferência realizada com sucesso!")
            print(f"💰 Carteira: R$ {saldo_carteira:.2f} → R$ {novo_saldo_carteira:.2f}")
            print(f"🏦 {conta_destino}: R$ {saldo_destino:.2f} → R$ {novo_saldo_destino:.2f}")
        else:
            print("\n❌ Erro ao realizar transferência!")
        
    except ValueError:
        print("❌ Valor inválido!")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    input("\nPressione Enter para continuar...")

def ver_historico_carteira(controle: ControleFinanceiroAvancado):
    """Mostra o histórico da carteira"""
    print("\n📊 HISTÓRICO DA CARTEIRA")
    print("-"*30)
    
    if "Carteira" not in controle.contas_bancarias:
        print("❌ Carteira não encontrada!")
        input("\nPressione Enter para continuar...")
        return
    
    carteira = controle.contas_bancarias["Carteira"]
    historico = carteira.historico_saldo
    
    if not historico:
        print("📝 Nenhuma movimentação registrada na carteira.")
        input("\nPressione Enter para continuar...")
        return
    
    print(f"💰 Saldo atual: R$ {carteira.saldo_atual:.2f}")
    print(f"📊 Total de movimentações: {len(historico)}")
    print("\n📋 HISTÓRICO DE MOVIMENTAÇÕES:")
    print("-"*60)
    
    # Mostrar últimas 10 movimentações
    for i, mov in enumerate(reversed(historico[-10:]), 1):
        data = mov['data']
        operacao = mov['operacao']
        valor = mov['valor']
        saldo_anterior = mov['saldo_anterior']
        saldo_novo = mov['saldo_novo']
        
        # Determinar símbolo baseado no valor
        simbolo = "➕" if valor >= 0 else "➖"
        cor_valor = "💚" if valor >= 0 else "❤️"
        
        print(f"{i:2d}. {data} - {operacao}")
        print(f"    {simbolo} {cor_valor} R$ {abs(valor):.2f}")
        print(f"    💰 R$ {saldo_anterior:.2f} → R$ {saldo_novo:.2f}")
        print()
    
    if len(historico) > 10:
        print(f"... e mais {len(historico) - 10} movimentações anteriores")
    
    input("\nPressione Enter para continuar...")

def transferir_entre_contas(controle: ControleFinanceiroAvancado):
    """Transfere dinheiro entre duas contas bancárias"""
    print("\n💸 TRANSFERIR ENTRE CONTAS")
    print("-"*35)
    
    contas = controle.obter_contas_bancarias()
    
    if len(contas) < 2:
        print("❌ É necessário ter pelo menos 2 contas para fazer transferências!")
        input("\nPressione Enter para continuar...")
        return
    
    # Mostrar contas disponíveis
    print("\n🏦 CONTAS DISPONÍVEIS:")
    for i, nome_conta in enumerate(contas, 1):
        saldo = controle.obter_saldo_conta(nome_conta)
        conta = controle.contas_bancarias[nome_conta]
        print(f"{i:2d}. {nome_conta} ({conta.banco}) - R$ {saldo:.2f}")
    
    try:
        # Selecionar conta origem
        print("\n📤 CONTA ORIGEM:")
        escolha_origem = int(input("Escolha a conta de origem (0 para cancelar): "))
        if escolha_origem == 0:
            return
        
        if escolha_origem < 1 or escolha_origem > len(contas):
            print("❌ Opção inválida!")
            input("\nPressione Enter para continuar...")
            return
        
        conta_origem = contas[escolha_origem - 1]
        saldo_origem = controle.obter_saldo_conta(conta_origem)
        
        print(f"\n💰 Conta selecionada: {conta_origem}")
        print(f"💵 Saldo disponível: R$ {saldo_origem:.2f}")
        
        # Selecionar conta destino
        print("\n📥 CONTA DESTINO:")
        print("Contas disponíveis:")
        for i, nome_conta in enumerate(contas, 1):
            if nome_conta != conta_origem:
                saldo = controle.obter_saldo_conta(nome_conta)
                conta = controle.contas_bancarias[nome_conta]
                print(f"{i:2d}. {nome_conta} ({conta.banco}) - R$ {saldo:.2f}")
        
        escolha_destino = int(input("\nEscolha a conta de destino (0 para cancelar): "))
        if escolha_destino == 0:
            return
        
        if escolha_destino < 1 or escolha_destino > len(contas):
            print("❌ Opção inválida!")
            input("\nPressione Enter para continuar...")
            return
        
        conta_destino = contas[escolha_destino - 1]
        
        if conta_origem == conta_destino:
            print("❌ As contas de origem e destino não podem ser iguais!")
            input("\nPressione Enter para continuar...")
            return
        
        saldo_destino = controle.obter_saldo_conta(conta_destino)
        
        # Solicitar valor
        valor = obter_valor_valido("\n💸 Valor a transferir (R$): ")
        
        if valor <= 0:
            print("❌ O valor deve ser maior que zero!")
            input("\nPressione Enter para continuar...")
            return
        
        if valor > saldo_origem:
            print(f"\n❌ Saldo insuficiente na conta {conta_origem}!")
            print(f"Saldo disponível: R$ {saldo_origem:.2f}")
            print(f"Valor solicitado: R$ {valor:.2f}")
            print(f"Faltam: R$ {valor - saldo_origem:.2f}")
            input("\nPressione Enter para continuar...")
            return
        
        # Confirmar transferência
        print("\n📋 RESUMO DA TRANSFERÊNCIA:")
        print("-"*50)
        print(f"🔹 Origem: {conta_origem} (R$ {saldo_origem:.2f})")
        print(f"🔹 Destino: {conta_destino} (R$ {saldo_destino:.2f})")
        print(f"🔹 Valor: R$ {valor:.2f}")
        print("-"*50)
        print(f"📊 Saldos após transferência:")
        print(f"   {conta_origem}: R$ {saldo_origem - valor:.2f}")
        print(f"   {conta_destino}: R$ {saldo_destino + valor:.2f}")
        
        confirmacao = input("\n❓ Confirmar transferência? (s/N): ").lower()
        
        if confirmacao != 's':
            print("❌ Transferência cancelada.")
            input("\nPressione Enter para continuar...")
            return
        
        # Realizar transferência
        sucesso = controle.transferir_entre_contas(conta_origem, conta_destino, valor)
        
        if sucesso:
            novo_saldo_origem = controle.obter_saldo_conta(conta_origem)
            novo_saldo_destino = controle.obter_saldo_conta(conta_destino)
            
            print(f"\n✅ Transferência realizada com sucesso!")
            print(f"📤 {conta_origem}: R$ {saldo_origem:.2f} → R$ {novo_saldo_origem:.2f}")
            print(f"📥 {conta_destino}: R$ {saldo_destino:.2f} → R$ {novo_saldo_destino:.2f}")
        else:
            print("\n❌ Erro ao realizar transferência!")
        
    except ValueError:
        print("❌ Valor inválido!")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    input("\nPressione Enter para continuar...")

def mostrar_alertas(controle: ControleFinanceiroAvancado):
    """Mostra alertas e notificações"""
    print("\n🚨 ALERTAS E NOTIFICAÇÕES")
    print("-"*35)
    
    print("Para qual mês deseja ver os alertas?")
    mes, ano = obter_mes_ano()
    
    # Alertas de metas
    alertas_metas = controle.obter_alertas_metas(mes, ano)
    
    # Alertas de vencimento
    despesas_vencendo = controle.obter_despesas_vencendo(7)
    
    # Alertas de saldo baixo
    alertas_saldo = []
    for nome_conta in controle.obter_contas_bancarias():
        saldo = controle.obter_saldo_conta(nome_conta)
        if saldo < 100:  # Critério de saldo baixo
            alertas_saldo.append(f"💰 Saldo baixo na conta '{nome_conta}': R$ {saldo:.2f}")
    
    total_alertas = len(alertas_metas) + len(despesas_vencendo) + len(alertas_saldo)
    
    if total_alertas == 0:
        print("\n✅ Nenhum alerta no momento! Tudo sob controle.")
    else:
        print(f"\n🚨 {total_alertas} ALERTA(S) ENCONTRADO(S):")
        print("="*50)
        
        # Mostrar alertas de metas
        if alertas_metas:
            print("\n📊 ALERTAS DE METAS:")
            for alerta in alertas_metas:
                print(f"  {alerta}")
        
        # Mostrar alertas de vencimento
        if despesas_vencendo:
            print("\n⏰ DESPESAS VENCENDO (próximos 7 dias):")
            for despesa, mes_desp, ano_desp in despesas_vencendo[:5]:  # Mostrar apenas 5
                dias = (despesa.data_vencimento - date.today()).days
                if dias <= 0:
                    print(f"  🔥 {despesa.descricao} - R$ {despesa.valor:.2f} (VENCIDA)")
                else:
                    print(f"  ⚠️ {despesa.descricao} - R$ {despesa.valor:.2f} ({dias} dias)")
        
        # Mostrar alertas de saldo
        if alertas_saldo:
            print("\n💰 ALERTAS DE SALDO:")
            for alerta in alertas_saldo:
                print(f"  {alerta}")
    
    input("\nPressione Enter para continuar...")

def relatorio_mensal_avancado(controle: ControleFinanceiroAvancado):
    """Mostra o relatório mensal completo com saldo total de todas as contas"""
    print("\n📊 RELATÓRIO MENSAL AVANÇADO")
    print("-"*40)
    
    print("Para qual mês deseja ver o relatório?")
    mes, ano = obter_mes_ano()
    
    print(f"\n📊 RELATÓRIO DE {obter_mes_nome(mes).upper()}/{ano}")
    print("="*60)
    
    # Calcular saldo total de todas as contas
    contas = controle.obter_contas_bancarias()
    saldo_total_contas = 0.0
    
    if contas:
        saldo_total_contas = sum(controle.obter_saldo_conta(conta) for conta in contas)
        print(f"🏦 Saldo Total das Contas: R$ {saldo_total_contas:.2f}")
        
        # Mostrar detalhamento por conta
        print("\n📋 DETALHAMENTO POR CONTA:")
        for nome_conta in contas:
            saldo_conta = controle.obter_saldo_conta(nome_conta)
            conta = controle.contas_bancarias[nome_conta]
            padrao = " (PADRÃO)" if nome_conta == controle.conta_padrao else ""
            print(f"  💳 {nome_conta}{padrao} - {conta.banco}: R$ {saldo_conta:.2f}")
    else:
        print("🏦 Saldo Total das Contas: R$ 0,00")
        print("⚠️  Nenhuma conta bancária cadastrada.")
    
    # Receitas
    total_receitas = controle.calcular_total_receitas(mes, ano)
    print(f"\n💰 Total de Receitas: R$ {total_receitas:.2f}")
    
    # Despesas
    total_despesas = controle.calcular_total_despesas(mes, ano)
    total_despesas_pagas = controle.calcular_total_despesas_pagas(mes, ano)
    despesas_pendentes = total_despesas - total_despesas_pagas
    
    print(f"💸 Total de Despesas: R$ {total_despesas:.2f}")
    print(f"   ✅ Pagas: R$ {total_despesas_pagas:.2f}")
    print(f"   ❌ Pendentes: R$ {despesas_pendentes:.2f}")
    
    # Saldo final
    saldo_final = controle.calcular_saldo_final(mes, ano)
    saldo_disponivel = saldo_total_contas + total_receitas - total_despesas_pagas
    
    print("-"*60)
    print(f"💵 Saldo Disponível (após pagos): R$ {saldo_disponivel:.2f}")
    print(f"💵 Saldo Final (após todas despesas): R$ {saldo_final:.2f}")
    
    # Análise inteligente de fluxo de caixa
    print("\n🧠 ANÁLISE INTELIGENTE DE FLUXO DE CAIXA:")
    print("-"*50)
    
    # Calcular saldo considerando receitas futuras (apenas despesas pendentes)
    saldo_com_receitas_futuras = saldo_total_contas + total_receitas - despesas_pendentes
    
    if saldo_final < 0 and saldo_com_receitas_futuras > 0:
        print(f"💡 INSIGHT: Suas receitas futuras cobrem as despesas pendentes!")
        print(f"   🎯 Saldo final esperado: R$ {saldo_com_receitas_futuras:.2f}")
        print("   ✅ Situação financeira: Tudo sob controle!")
    elif saldo_final < 0:
        print("⚠️  ATENÇÃO: Saldo final negativo!")
        print("💡 Dica: Considere adicionar mais receitas ou reduzir despesas.")
    elif despesas_pendentes > saldo_disponivel:
        print("⚠️  ATENÇÃO: Despesas pendentes excedem saldo disponível!")
        print("💡 Dica: Aguarde as receitas futuras ou transfira dinheiro entre contas.")
    else:
        print("✅ SITUAÇÃO FINANCEIRA: Tudo sob controle!")
        print(f"💵 Saldo positivo: R$ {saldo_final:.2f}")
    
    # Mostrar apenas despesas próximas do vencimento (próximos 7 dias)
    despesas = controle.obter_despesas_mes(mes, ano)
    despesas_nao_pagas = [d for d in despesas if not d.pago]
    hoje = date.today()
    
    despesas_proximas = [d for d in despesas_nao_pagas if (d.data_vencimento - hoje).days <= 7]
    
    if despesas_proximas:
        print(f"\n⏰ DESPESAS VENCENDO (próximos 7 dias):")
        for despesa in despesas_proximas:
            dias_vencimento = (despesa.data_vencimento - hoje).days
            
            if dias_vencimento < 0:
                status_venc = f"🔥 VENCIDA há {abs(dias_vencimento)} dias"
            elif dias_vencimento == 0:
                status_venc = "🔥 VENCE HOJE"
            elif dias_vencimento == 1:
                status_venc = "⚠️ VENCE AMANHÃ"
            else:
                status_venc = f"⚠️ Vence em {dias_vencimento} dias"
            
            print(f"  💸 {despesa.descricao} - R$ {despesa.valor:.2f} - {status_venc}")
    
    input("\nPressione Enter para continuar...")

def limpar_dados(controle: ControleFinanceiroAvancado):
    """Limpa todos os dados do sistema"""
    print("\n🗑️ LIMPAR TODOS OS DADOS")
    print("="*50)
    print("⚠️  ATENÇÃO: OPERAÇÃO IRREVERSÍVEL!")
    print("="*50)
    
    # Mostrar informações atuais
    contas = controle.obter_contas_bancarias()
    total_despesas = sum(len(controle.obter_despesas_mes(m, a)) 
                         for m in range(1, 13) 
                         for a in range(2020, 2030))
    total_receitas = sum(len(controle.obter_receitas_mes(m, a)) 
                         for m in range(1, 13) 
                         for a in range(2020, 2030))
    
    print(f"\n📊 DADOS ATUAIS NO SISTEMA:")
    print(f"  🏦 Contas Bancárias: {len(contas)}")
    print(f"  💸 Despesas: {total_despesas}")
    print(f"  💰 Receitas: {total_receitas}")
    
    if contas:
        saldo_total = sum(controle.obter_saldo_conta(conta) for conta in contas)
        print(f"  💵 Saldo Total: R$ {saldo_total:.2f}")
    
    print("\n⚠️  ESTA OPERAÇÃO IRÁ:")
    print("  ❌ Apagar todas as contas bancárias")
    print("  ❌ Apagar todas as despesas")
    print("  ❌ Apagar todas as receitas")
    print("  ❌ Apagar todas as metas")
    print("  ❌ Apagar todo o histórico")
    print("  ❌ Resetar o sistema ao estado inicial")
    
    print("\n" + "="*50)
    print("CONFIRMAÇÃO DE SEGURANÇA")
    print("="*50)
    
    # Primeira confirmação
    print("\n1️⃣ PRIMEIRA CONFIRMAÇÃO:")
    confirmacao1 = input("   Digite 'LIMPAR' para continuar (ou qualquer coisa para cancelar): ").upper()
    
    if confirmacao1 != 'LIMPAR':
        print("\n✅ Operação cancelada. Seus dados estão seguros.")
        input("\nPressione Enter para continuar...")
        return False
    
    # Segunda confirmação
    print("\n2️⃣ SEGUNDA CONFIRMAÇÃO:")
    print("   Você tem certeza ABSOLUTA de que deseja apagar TODOS os dados?")
    confirmacao2 = input("   Digite 'SIM, APAGAR TUDO' para confirmar: ").upper()
    
    if confirmacao2 != 'SIM, APAGAR TUDO':
        print("\n✅ Operação cancelada. Seus dados estão seguros.")
        input("\nPressione Enter para continuar...")
        return False
    
    # Terceira confirmação (última chance)
    print("\n3️⃣ CONFIRMAÇÃO FINAL:")
    print("   ⚠️  ÚLTIMA CHANCE! Esta ação NÃO pode ser desfeita!")
    confirmacao3 = input("   Digite 'CONFIRMAR' para prosseguir: ").upper()
    
    if confirmacao3 != 'CONFIRMAR':
        print("\n✅ Operação cancelada. Seus dados estão seguros.")
        input("\nPressione Enter para continuar...")
        return False
    
    # Executar limpeza
    print("\n🔄 Limpando dados...")
    
    try:
        # Remover arquivos de dados
        import os
        arquivos_dados = [
            'dados_financeiros_avancado.json',
            'dados_financeiros.json'
        ]
        
        for arquivo in arquivos_dados:
            if os.path.exists(arquivo):
                os.remove(arquivo)
                print(f"  ✅ {arquivo} removido")
        
        # Reinicializar o controle
        controle.contas_bancarias = {}
        controle.despesas = {}
        controle.receitas = {}
        controle.metas_gastos = {}
        controle.conta_padrao = "Carteira"  # Carteira como padrão
        
        # Criar carteira padrão inicial
        controle.criar_conta_bancaria("Carteira", "Dinheiro em Espécie", 0.0)
        
        print("\n✅ DADOS LIMPOS COM SUCESSO!")
        print("🔄 Sistema reiniciado com configurações padrão.")
        print("💵 Carteira definida como conta padrão.")
        
    except Exception as e:
        print(f"\n❌ Erro ao limpar dados: {e}")
        print("⚠️  Pode ser necessário reiniciar o sistema.")
        input("\nPressione Enter para continuar...")
        return False
    
    input("\nPressione Enter para continuar...")
    return True

def remover_despesa_mysql(controle: ControleFinanceiroAvancado):
    """Remove uma despesa do sistema MySQL"""
    print("\n🗑️ REMOVER DESPESA")
    print("-"*30)
    
    print("De qual mês?")
    mes, ano = obter_mes_ano()
    
    despesas = controle.obter_despesas_mes(mes, ano)
    
    if not despesas:
        print(f"\n❌ Nenhuma despesa encontrada para {obter_mes_nome(mes)}/{ano}")
        input("\nPressione Enter para continuar...")
        return
    
    print(f"\n📋 DESPESAS DE {obter_mes_nome(mes).upper()}/{ano}:")
    for i, despesa in enumerate(despesas, 1):
        status = "✅ PAGO" if despesa.pago else "❌ PENDENTE"
        print(f"{i:2d}. {despesa.descricao} - R$ {despesa.valor:.2f} - {status}")
    
    try:
        escolha = int(input("\nEscolha o número da despesa para remover (0 para cancelar): "))
        if escolha == 0:
            return
        
        if escolha < 1 or escolha > len(despesas):
            print("❌ Opção inválida!")
            input("\nPressione Enter para continuar...")
            return
        
        despesa_selecionada = despesas[escolha - 1]
        
        # Usar o método específico do MySQL
        sucesso = controle.remover_despesa(despesa_selecionada, mes, ano)
        
        if sucesso:
            print(f"\n✅ Despesa '{despesa_selecionada.descricao}' removida com sucesso!")
        else:
            print(f"\n❌ Erro ao remover despesa '{despesa_selecionada.descricao}'!")
        
    except ValueError:
        print("❌ Opção inválida!")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    
    input("\nPressione Enter para continuar...")

def remover_receita_mysql(controle: ControleFinanceiroAvancado):
    """Remove uma receita do sistema MySQL"""
    print("\n🗑️ REMOVER RECEITA")
    print("-"*30)
    
    print("De qual mês?")
    mes, ano = obter_mes_ano()
    
    receitas = controle.obter_receitas_mes(mes, ano)
    
    if not receitas:
        print(f"\n❌ Nenhuma receita encontrada para {obter_mes_nome(mes)}/{ano}")
        input("\nPressione Enter para continuar...")
        return
    
    print(f"\n📋 RECEITAS DE {obter_mes_nome(mes).upper()}/{ano}:")
    for i, receita in enumerate(receitas, 1):
        print(f"{i:2d}. {receita.descricao} - R$ {receita.valor:.2f}")
    
    try:
        escolha = int(input("\nEscolha o número da receita para remover (0 para cancelar): "))
        if escolha == 0:
            return
        
        if escolha < 1 or escolha > len(receitas):
            print("❌ Opção inválida!")
            input("\nPressione Enter para continuar...")
            return
        
        receita_selecionada = receitas[escolha - 1]
        
        # Usar o método específico do MySQL
        sucesso = controle.remover_receita(receita_selecionada, mes, ano)
        
        if sucesso:
            print(f"\n✅ Receita '{receita_selecionada.descricao}' removida com sucesso!")
        else:
            print(f"\n❌ Erro ao remover receita '{receita_selecionada.descricao}'!")
        
    except ValueError:
        print("❌ Opção inválida!")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    
    input("\nPressione Enter para continuar...")

def migrar_conta_padrao_para_carteira(controle: ControleFinanceiroAvancado):
    """Migra a conta padrão para Carteira se necessário"""
    if controle.conta_padrao != "Carteira":
        print("🔄 Migrando conta padrão para Carteira...")
        controle.conta_padrao = "Carteira"
        controle.salvar_dados()
        print("✅ Conta padrão alterada para Carteira.")

def main():
    """Função principal do programa avançado"""
    # Verificar dependências
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
    except ImportError:
        print("⚠️ ATENÇÃO: Algumas funcionalidades avançadas não estão disponíveis.")
        print("Para usar gráficos e exportação, instale as dependências:")
        print("pip install matplotlib pandas openpyxl reportlab")
        print("\nPressione Enter para continuar com funcionalidades básicas...")
        input()
    
    controle = ControleFinanceiroAvancado()
    
    # Migrar conta padrão para Carteira se necessário
    migrar_conta_padrao_para_carteira(controle)
    
    while True:
        limpar_tela()
        mostrar_cabecalho()
        
        # Mostrar resumo rápido
        contas = controle.obter_contas_bancarias()
        if contas:
            saldo_total = sum(controle.obter_saldo_conta(conta) for conta in contas)
            print(f"💰 Saldo Total: R$ {saldo_total:.2f} | 🏦 Contas: {len(contas)}")
        
        menu_principal()
        
        try:
            opcao = input("Escolha uma opção: ")
            
            if opcao == "1":
                # Gerenciar Contas Bancárias
                while True:
                    limpar_tela()
                    mostrar_cabecalho()
                    menu_contas()
                    
                    opcao_conta = input("Escolha uma opção: ")
                    
                    if opcao_conta == "1":
                        criar_conta_bancaria(controle)
                    elif opcao_conta == "2":
                        listar_contas(controle)
                    elif opcao_conta == "3":
                        atualizar_saldo_conta(controle)
                    elif opcao_conta == "4":
                        mostrar_historico_saldo(controle)
                    elif opcao_conta == "5":
                        editar_conta_avancado(controle)
                    elif opcao_conta == "6":
                        remover_conta_bancaria(controle)
                    elif opcao_conta == "7":
                        # Definir conta padrão
                        contas = controle.obter_contas_bancarias()
                        if contas:
                            print("\nContas disponíveis:")
                            for i, nome in enumerate(contas, 1):
                                padrao = " (ATUAL)" if nome == controle.conta_padrao else ""
                                print(f"{i}. {nome}{padrao}")
                            try:
                                escolha = int(input("\nEscolha a nova conta padrão: "))
                                if 1 <= escolha <= len(contas):
                                    controle.conta_padrao = contas[escolha - 1]
                                    controle.salvar_dados()
                                    print(f"✅ Conta padrão alterada para: {controle.conta_padrao}")
                                else:
                                    print("❌ Opção inválida!")
                            except ValueError:
                                print("❌ Opção inválida!")
                            input("\nPressione Enter para continuar...")
                    elif opcao_conta == "8":
                        gerenciar_carteira(controle)
                    elif opcao_conta == "9":
                        transferir_entre_contas(controle)
                    elif opcao_conta == "0":
                        break
                    else:
                        print("❌ Opção inválida!")
                        input("\nPressione Enter para continuar...")
            
            elif opcao == "2":
                # Gerenciar Despesas (usando funções adaptadas para MySQL)
                from main import adicionar_despesa, listar_despesas, marcar_pagamento_despesa
                
                while True:
                    limpar_tela()
                    mostrar_cabecalho()
                    menu_despesas()
                    
                    opcao_despesa = input("Escolha uma opção: ")
                    
                    if opcao_despesa == "1":
                        adicionar_despesa(controle)
                    elif opcao_despesa == "2":
                        listar_despesas(controle)
                    elif opcao_despesa == "3":
                        pagar_despesa_automatico(controle)
                    elif opcao_despesa == "4":
                        marcar_pagamento_despesa(controle)
                    elif opcao_despesa == "5":
                        remover_despesa_mysql(controle)
                    elif opcao_despesa == "0":
                        break
                    else:
                        print("❌ Opção inválida!")
                        input("\nPressione Enter para continuar...")
            
            elif opcao == "3":
                # Gerenciar Receitas
                from main import adicionar_receita, listar_receitas
                
                while True:
                    limpar_tela()
                    mostrar_cabecalho()
                    menu_receitas()
                    
                    opcao_receita = input("Escolha uma opção: ")
                    
                    if opcao_receita == "1":
                        adicionar_receita(controle)
                    elif opcao_receita == "2":
                        processar_receita_automatico(controle)
                    elif opcao_receita == "3":
                        listar_receitas(controle)
                    elif opcao_receita == "4":
                        remover_receita_mysql(controle)
                    elif opcao_receita == "0":
                        break
                    else:
                        print("❌ Opção inválida!")
                        input("\nPressione Enter para continuar...")
            
            elif opcao == "5":
                # Busca e Filtros
                while True:
                    limpar_tela()
                    mostrar_cabecalho()
                    menu_busca()
                    
                    opcao_busca = input("Escolha uma opção: ")
                    
                    if opcao_busca == "1":
                        buscar_despesas_avancado(controle)
                    elif opcao_busca == "2":
                        buscar_receitas_avancado(controle)
                    elif opcao_busca == "3":
                        mostrar_despesas_vencendo(controle)
                    elif opcao_busca == "0":
                        break
                    else:
                        print("❌ Opção inválida!")
                        input("\nPressione Enter para continuar...")
            
            elif opcao == "6":
                # Relatórios e Gráficos
                while True:
                    limpar_tela()
                    mostrar_cabecalho()
                    menu_relatorios()
                    
                    opcao_relatorio = input("Escolha uma opção: ")
                    
                    if opcao_relatorio == "1":
                        relatorio_mensal_avancado(controle)
                    elif opcao_relatorio == "2":
                        gerar_grafico_categoria(controle)
                    elif opcao_relatorio == "3":
                        gerar_grafico_comparativo(controle)
                    elif opcao_relatorio == "4":
                        print("📊 Análise por categoria disponível nos gráficos")
                        input("\nPressione Enter para continuar...")
                    elif opcao_relatorio == "5":
                        listar_contas(controle)
                    elif opcao_relatorio == "0":
                        break
                    else:
                        print("❌ Opção inválida!")
                        input("\nPressione Enter para continuar...")
            
            elif opcao == "7":
                # Alertas e Notificações
                mostrar_alertas(controle)
            
            elif opcao == "8":
                # Exportar Dados
                print("\n📤 EXPORTAR DADOS")
                print("Funcionalidade de exportação em desenvolvimento...")
                print("Dados salvos automaticamente em JSON.")
                input("\nPressione Enter para continuar...")
            
            elif opcao == "9":
                # Limpar Dados
                limpar_dados(controle)
            
            elif opcao == "0":
                print("\n👋 Obrigado por usar o Sistema Avançado de Controle de Gastos!")
                print("💾 Todos os dados foram salvos automaticamente.")
                break
            
            else:
                print("❌ Opção inválida!")
                input("\nPressione Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Saindo do sistema...")
            break
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()