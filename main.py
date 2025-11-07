from src.controllers.controle_gastos import ControleFinanceiro, Despesa, Receita
from datetime import datetime, date
import os

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
    print("="*60)
    print("           💰 SISTEMA DE CONTROLE DE GASTOS 💰")
    print("="*60)

def menu_principal():
    """Mostra o menu principal"""
    print("\n📋 MENU PRINCIPAL:")
    print("1️⃣  - Gerenciar Despesas")
    print("2️⃣  - Gerenciar Receitas")
    print("3️⃣  - Definir Saldo do Banco")
    print("4️⃣  - Relatório Mensal")
    print("5️⃣  - Relatório Anual")
    print("0️⃣  - Sair")
    print("-"*40)

def menu_despesas():
    """Mostra o menu de despesas"""
    print("\n💸 GERENCIAR DESPESAS:")
    print("1️⃣  - Adicionar Despesa")
    print("2️⃣  - Listar Despesas")
    print("3️⃣  - Marcar como Pago/Não Pago")
    print("4️⃣  - Remover Despesa")
    print("0️⃣  - Voltar")
    print("-"*40)

def menu_receitas():
    """Mostra o menu de receitas"""
    print("\n💰 GERENCIAR RECEITAS:")
    print("1️⃣  - Adicionar Receita")
    print("2️⃣  - Listar Receitas")
    print("3️⃣  - Remover Receita")
    print("0️⃣  - Voltar")
    print("-"*40)

def adicionar_despesa(controle: ControleFinanceiro):
    """Adiciona uma nova despesa"""
    from datetime import date
    
    while True:
        print("\n➕ ADICIONAR DESPESA")
        print("-"*30)
        
        descricao = input("Descrição da despesa: ")
        valor = obter_valor_valido("Valor (R$): ")
        data_despesa = obter_data_valida("Data da despesa (DD/MM/AAAA): ")
        categoria = input("Categoria (opcional): ") or "Geral"
        
        # Perguntar se foi pago
        print("\n💰 Status do Pagamento:")
        print("1️⃣  - Já foi pago")
        print("2️⃣  - Ainda não foi pago")
        
        while True:
            opcao_pago = input("\nEscolha uma opção: ")
            if opcao_pago in ["1", "2"]:
                break
            print("❌ Opção inválida! Digite 1 ou 2.")
        
        # Determinar se foi pago baseado na escolha do usuário e na data
        data_despesa_obj = datetime.strptime(data_despesa, "%d/%m/%Y").date()
        hoje = date.today()
        
        if opcao_pago == "1":
            # Usuário disse que foi pago
            pago = True
            print(f"✅ Despesa marcada como PAGA")
        else:
            # Usuário disse que não foi pago
            if data_despesa_obj > hoje:
                # Data futura - automaticamente não pago
                pago = False
                print(f"⏳ Despesa marcada como PENDENTE (data futura)")
            else:
                # Data passada ou hoje - respeitar escolha do usuário
                pago = False
                print(f"❌ Despesa marcada como PENDENTE")
        
        print("\nEm qual mês deseja adicionar esta despesa?")
        mes, ano = obter_mes_ano()
        
        despesa = Despesa(descricao, valor, data_despesa, pago, categoria)
        controle.adicionar_despesa(despesa, mes, ano)
        
        status_msg = "PAGA" if pago else "PENDENTE"
        print(f"\n✅ Despesa '{descricao}' adicionada como {status_msg} para {obter_mes_nome(mes)}/{ano}!")
        
        # Pergunta se deseja adicionar outra despesa
        print("\n🔄 Opções:")
        print("1️⃣  - Adicionar outra despesa")
        print("0️⃣  - Voltar ao menu de despesas")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao != "1":
            break

def listar_despesas(controle: ControleFinanceiro):
    """Lista as despesas de um mês"""
    print("\n📋 LISTAR DESPESAS")
    print("-"*30)
    
    print("Para qual mês deseja ver as despesas?")
    mes, ano = obter_mes_ano()
    
    despesas = controle.obter_despesas_mes(mes, ano)
    
    if not despesas:
        print(f"\n❌ Nenhuma despesa encontrada para {obter_mes_nome(mes)}/{ano}")
    else:
        print(f"\n📋 DESPESAS DE {obter_mes_nome(mes).upper()}/{ano}:")
        print("="*60)
        
        total_despesas = 0
        total_pagas = 0
        
        for i, despesa in enumerate(despesas, 1):
            status = "✅ PAGO" if despesa.pago else "❌ PENDENTE"
            data_pag = f" (Pago em: {despesa.data_pagamento.strftime('%d/%m/%Y')})" if despesa.data_pagamento else ""
            
            print(f"{i:2d}. {despesa.descricao}")
            print(f"    💰 Valor: R$ {despesa.valor:.2f}")
            print(f"    📅 Vencimento: {despesa.data_vencimento.strftime('%d/%m/%Y')}")
            print(f"    📂 Categoria: {despesa.categoria}")
            print(f"    🔄 Status: {status}{data_pag}")
            print("-"*40)
            
            total_despesas += despesa.valor
            if despesa.pago:
                total_pagas += despesa.valor
        
        print(f"\n💰 TOTAL DE DESPESAS: R$ {total_despesas:.2f}")
        print(f"✅ TOTAL PAGO: R$ {total_pagas:.2f}")
        print(f"❌ TOTAL PENDENTE: R$ {total_despesas - total_pagas:.2f}")
    
    input("\nPressione Enter para continuar...")

def marcar_pagamento_despesa(controle: ControleFinanceiro):
    """Marca uma despesa como paga ou não paga"""
    print("\n🔄 ALTERAR STATUS DE PAGAMENTO")
    print("-"*40)
    
    print("Para qual mês?")
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
        escolha = int(input("\nEscolha o número da despesa (0 para cancelar): "))
        if escolha == 0:
            return
        
        if escolha < 1 or escolha > len(despesas):
            print("❌ Opção inválida!")
            input("\nPressione Enter para continuar...")
            return
        
        despesa_selecionada = despesas[escolha - 1]
        
        if despesa_selecionada.pago:
            despesa_selecionada.marcar_como_nao_pago()
            print(f"\n✅ Despesa '{despesa_selecionada.descricao}' marcada como NÃO PAGA!")
        else:
            data_pagamento = input("Data do pagamento (DD/MM/AAAA) ou Enter para hoje: ")
            if data_pagamento and not validar_data(data_pagamento):
                print("❌ Data inválida! Usando data de hoje.")
                data_pagamento = None
            
            despesa_selecionada.marcar_como_pago(data_pagamento)
            print(f"\n✅ Despesa '{despesa_selecionada.descricao}' marcada como PAGA!")
        
        controle.salvar_dados()
        
    except ValueError:
        print("❌ Opção inválida!")
    
    input("\nPressione Enter para continuar...")

def remover_despesa(controle: ControleFinanceiro):
    """Remove uma despesa"""
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
        
        despesa_removida = despesas.pop(escolha - 1)
        controle.salvar_dados()
        
        print(f"\n✅ Despesa '{despesa_removida.descricao}' removida com sucesso!")
        
    except ValueError:
        print("❌ Opção inválida!")
    
    input("\nPressione Enter para continuar...")

def adicionar_receita(controle: ControleFinanceiro):
    """Adiciona uma nova receita"""
    while True:
        print("\n➕ ADICIONAR RECEITA")
        print("-"*30)
        
        descricao = input("Descrição da receita: ")
        valor = obter_valor_valido("Valor (R$): ")
        data_recebimento = obter_data_valida("Data de recebimento (DD/MM/AAAA): ")
        categoria = input("Categoria (opcional): ") or "Salário"
        
        print("\nEm qual mês deseja adicionar esta receita?")
        mes, ano = obter_mes_ano()
        
        receita = Receita(descricao, valor, data_recebimento, categoria)
        controle.adicionar_receita(receita, mes, ano)
        
        print(f"\n✅ Receita '{descricao}' adicionada com sucesso para {obter_mes_nome(mes)}/{ano}!")
        
        # Pergunta se deseja adicionar outra receita
        print("\n🔄 Opções:")
        print("1️⃣  - Adicionar outra receita")
        print("0️⃣  - Voltar ao menu de receitas")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao != "1":
            break

def listar_receitas(controle: ControleFinanceiro):
    """Lista as receitas de um mês"""
    print("\n📋 LISTAR RECEITAS")
    print("-"*30)
    
    print("Para qual mês deseja ver as receitas?")
    mes, ano = obter_mes_ano()
    
    receitas = controle.obter_receitas_mes(mes, ano)
    
    if not receitas:
        print(f"\n❌ Nenhuma receita encontrada para {obter_mes_nome(mes)}/{ano}")
    else:
        print(f"\n📋 RECEITAS DE {obter_mes_nome(mes).upper()}/{ano}:")
        print("="*60)
        
        total_receitas = 0
        
        for i, receita in enumerate(receitas, 1):
            print(f"{i:2d}. {receita.descricao}")
            print(f"    💰 Valor: R$ {receita.valor:.2f}")
            print(f"    📅 Data: {receita.data_recebimento.strftime('%d/%m/%Y')}")
            print(f"    📂 Categoria: {receita.categoria}")
            print("-"*40)
            
            total_receitas += receita.valor
        
        print(f"\n💰 TOTAL DE RECEITAS: R$ {total_receitas:.2f}")
    
    input("\nPressione Enter para continuar...")

def remover_receita(controle: ControleFinanceiro):
    """Remove uma receita"""
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
        
        receita_removida = receitas.pop(escolha - 1)
        controle.salvar_dados()
        
        print(f"\n✅ Receita '{receita_removida.descricao}' removida com sucesso!")
        
    except ValueError:
        print("❌ Opção inválida!")
    
    input("\nPressione Enter para continuar...")

def definir_saldo_banco(controle: ControleFinanceiro):
    """Define o saldo do banco para um mês"""
    print("\n🏦 DEFINIR SALDO DO BANCO")
    print("-"*35)
    
    print("Para qual mês deseja definir o saldo?")
    mes, ano = obter_mes_ano()
    
    saldo_atual = controle.obter_saldo_banco(mes, ano)
    if saldo_atual > 0:
        print(f"\n💰 Saldo atual para {obter_mes_nome(mes)}/{ano}: R$ {saldo_atual:.2f}")
    
    novo_saldo = obter_valor_valido("Novo saldo (R$): ")
    controle.definir_saldo_banco(novo_saldo, mes, ano)
    
    print(f"\n✅ Saldo definido com sucesso para {obter_mes_nome(mes)}/{ano}: R$ {novo_saldo:.2f}")
    input("\nPressione Enter para continuar...")

def relatorio_mensal(controle: ControleFinanceiro):
    """Mostra o relatório mensal completo"""
    print("\n📊 RELATÓRIO MENSAL")
    print("-"*30)
    
    print("Para qual mês deseja ver o relatório?")
    mes, ano = obter_mes_ano()
    
    print(f"\n📊 RELATÓRIO DE {obter_mes_nome(mes).upper()}/{ano}")
    print("="*60)
    
    # Saldo do banco
    saldo_banco = controle.obter_saldo_banco(mes, ano)
    print(f"🏦 Saldo do Banco: R$ {saldo_banco:.2f}")
    
    # Receitas
    total_receitas = controle.calcular_total_receitas(mes, ano)
    print(f"💰 Total de Receitas: R$ {total_receitas:.2f}")
    
    # Despesas
    total_despesas = controle.calcular_total_despesas(mes, ano)
    total_despesas_pagas = controle.calcular_total_despesas_pagas(mes, ano)
    despesas_pendentes = total_despesas - total_despesas_pagas
    
    print(f"💸 Total de Despesas: R$ {total_despesas:.2f}")
    print(f"   ✅ Pagas: R$ {total_despesas_pagas:.2f}")
    print(f"   ❌ Pendentes: R$ {despesas_pendentes:.2f}")
    
    # Saldo final
    saldo_final = controle.calcular_saldo_final(mes, ano)
    saldo_disponivel = saldo_banco + total_receitas - total_despesas_pagas
    
    print("-"*60)
    print(f"💵 Saldo Disponível (após pagos): R$ {saldo_disponivel:.2f}")
    print(f"💵 Saldo Final (após todas despesas): R$ {saldo_final:.2f}")
    
    if saldo_final < 0:
        print("⚠️  ATENÇÃO: Saldo final negativo!")
    elif despesas_pendentes > saldo_disponivel:
        print("⚠️  ATENÇÃO: Despesas pendentes excedem saldo disponível!")
    
    # Despesas próximas do vencimento
    despesas = controle.obter_despesas_mes(mes, ano)
    despesas_nao_pagas = [d for d in despesas if not d.pago]
    
    if despesas_nao_pagas:
        print("\n⏰ DESPESAS PENDENTES:")
        print("-"*40)
        for despesa in sorted(despesas_nao_pagas, key=lambda x: x.data_vencimento):
            dias_vencimento = (despesa.data_vencimento - date.today()).days
            if dias_vencimento < 0:
                status_venc = f"❗ VENCIDA há {abs(dias_vencimento)} dias"
            elif dias_vencimento == 0:
                status_venc = "🔥 VENCE HOJE"
            elif dias_vencimento <= 7:
                status_venc = f"⚠️  Vence em {dias_vencimento} dias"
            else:
                status_venc = f"📅 Vence em {dias_vencimento} dias"
            
            print(f"• {despesa.descricao} - R$ {despesa.valor:.2f} - {status_venc}")
    
    input("\nPressione Enter para continuar...")

def relatorio_anual(controle: ControleFinanceiro):
    """Mostra o relatório anual"""
    print("\n📊 RELATÓRIO ANUAL")
    print("-"*30)
    
    ano = int(input("Digite o ano para o relatório: "))
    
    print(f"\n📊 RELATÓRIO ANUAL DE {ano}")
    print("="*80)
    
    total_receitas_ano = 0
    total_despesas_ano = 0
    total_despesas_pagas_ano = 0
    
    for mes in range(1, 13):
        receitas_mes = controle.calcular_total_receitas(mes, ano)
        despesas_mes = controle.calcular_total_despesas(mes, ano)
        despesas_pagas_mes = controle.calcular_total_despesas_pagas(mes, ano)
        saldo_banco_mes = controle.obter_saldo_banco(mes, ano)
        
        if receitas_mes > 0 or despesas_mes > 0 or saldo_banco_mes > 0:
            saldo_final_mes = saldo_banco_mes + receitas_mes - despesas_mes
            
            print(f"{obter_mes_nome(mes):>12} | Receitas: R$ {receitas_mes:>8.2f} | "
                  f"Despesas: R$ {despesas_mes:>8.2f} | Saldo: R$ {saldo_final_mes:>8.2f}")
            
            total_receitas_ano += receitas_mes
            total_despesas_ano += despesas_mes
            total_despesas_pagas_ano += despesas_pagas_mes
    
    print("="*80)
    print(f"{'TOTAL ANUAL':>12} | Receitas: R$ {total_receitas_ano:>8.2f} | "
          f"Despesas: R$ {total_despesas_ano:>8.2f} | "
          f"Economia: R$ {total_receitas_ano - total_despesas_pagas_ano:>8.2f}")
    
    if total_despesas_ano > total_despesas_pagas_ano:
        pendente = total_despesas_ano - total_despesas_pagas_ano
        print(f"\n⚠️  Despesas pendentes no ano: R$ {pendente:.2f}")
    
    input("\nPressione Enter para continuar...")

def main():
    """Função principal do programa"""
    controle = ControleFinanceiro()
    
    while True:
        limpar_tela()
        mostrar_cabecalho()
        menu_principal()
        
        try:
            opcao = input("Escolha uma opção: ")
            
            if opcao == "1":
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
                        marcar_pagamento_despesa(controle)
                    elif opcao_despesa == "4":
                        remover_despesa(controle)
                    elif opcao_despesa == "0":
                        break
                    else:
                        print("❌ Opção inválida!")
                        input("\nPressione Enter para continuar...")
            
            elif opcao == "2":
                while True:
                    limpar_tela()
                    mostrar_cabecalho()
                    menu_receitas()
                    
                    opcao_receita = input("Escolha uma opção: ")
                    
                    if opcao_receita == "1":
                        adicionar_receita(controle)
                    elif opcao_receita == "2":
                        listar_receitas(controle)
                    elif opcao_receita == "3":
                        remover_receita(controle)
                    elif opcao_receita == "0":
                        break
                    else:
                        print("❌ Opção inválida!")
                        input("\nPressione Enter para continuar...")
            
            elif opcao == "3":
                definir_saldo_banco(controle)
            
            elif opcao == "4":
                relatorio_mensal(controle)
            
            elif opcao == "5":
                relatorio_anual(controle)
            
            elif opcao == "0":
                print("\n👋 Obrigado por usar o Sistema de Controle de Gastos!")
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