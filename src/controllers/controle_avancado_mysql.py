from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
from src.controllers.controle_gastos import ControleFinanceiro, Despesa, Receita
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
import warnings
from src.db.db_connection import DatabaseManager
from decimal import Decimal

warnings.filterwarnings('ignore')

class ContaBancaria:
    """Classe para representar uma conta bancária"""
    
    def __init__(self, id: int, nome: str, banco: str, saldo_inicial: float = 0.0):
        self.id = id
        self.nome = nome
        self.banco = banco
        self.saldo_atual = float(saldo_inicial)
        self.historico_saldo = []
    
    def atualizar_saldo(self, novo_saldo: float, operacao: str, valor: float = 0.0):
        """Atualiza o saldo (será sincronizado com o banco via ControleFinanceiroAvancado)"""
        self.saldo_atual = float(novo_saldo)
    
    @classmethod
    def from_db(cls, data: Dict):
        """Cria uma conta a partir de dados do banco"""
        return cls(
            id=data['id'],
            nome=data['nome'],
            banco=data['banco'],
            saldo_inicial=float(data['saldo_atual'])
        )

class MetaGasto:
    """Classe para representar metas de gastos por categoria"""
    
    def __init__(self, id: int, categoria: str, limite_mensal: float, mes: int, ano: int):
        self.id = id
        self.categoria = categoria
        self.limite_mensal = float(limite_mensal)
        self.mes = mes
        self.ano = ano
        self.gasto_atual = 0.0
        self.alertas_enviados = []
    
    def atualizar_gasto(self, valor: float):
        """Atualiza o gasto atual da categoria"""
        self.gasto_atual += float(valor)
    
    def percentual_usado(self) -> float:
        """Retorna o percentual do limite usado"""
        if self.limite_mensal == 0:
            return 0.0
        return (self.gasto_atual / self.limite_mensal) * 100
    
    def precisa_alerta(self) -> bool:
        """Verifica se precisa enviar alerta"""
        percentual = self.percentual_usado()
        return percentual >= 80 and '80%' not in self.alertas_enviados
    
    @classmethod
    def from_db(cls, data: Dict):
        """Cria uma meta a partir de dados do banco"""
        meta = cls(
            id=data['id'],
            categoria=data['categoria'],
            limite_mensal=float(data['limite_mensal']),
            mes=data['mes'],
            ano=data['ano']
        )
        meta.gasto_atual = float(data.get('gasto_atual', 0.0))
        # alertas_enviados pode ser None ou JSON
        meta.alertas_enviados = data.get('alertas_enviados', []) or []
        return meta

class ControleFinanceiroAvancado(ControleFinanceiro):
    """Versão avançada do controle financeiro com MySQL"""
    
    def __init__(self):
        # Não chamar super().__init__() pois não usaremos JSON
        self.despesas = {}
        self.receitas = {}
        self.contas_bancarias: Dict[str, ContaBancaria] = {}
        self.metas_gastos: Dict[str, List[MetaGasto]] = {}
        self.conta_padrao = "Carteira"
        self.saldo_atual = 0.0
        
        # Inicializar gerenciador de banco de dados
        try:
            self.db = DatabaseManager()
            self.carregar_dados()
        except Exception as e:
            print(f"❌ Erro ao conectar ao banco de dados: {e}")
            print("💡 Certifique-se de que:")
            print("   1. O MySQL está rodando")
            print("   2. Execute 'python init_database.py' para inicializar o banco")
            raise
    
    def carregar_dados(self):
        """Carrega dados do MySQL"""
        try:
            # Carregar contas bancárias
            contas_db = self.db.listar_contas_bancarias()
            for conta_data in contas_db:
                conta = ContaBancaria.from_db(conta_data)
                self.contas_bancarias[conta.nome] = conta
                
                # Carregar histórico da conta
                historico = self.db.obter_historico_conta(conta.id, limite=100)
                conta.historico_saldo = historico
            
            # Carregar conta padrão
            conta_padrao_db = self.db.obter_configuracao('conta_padrao')
            if conta_padrao_db:
                self.conta_padrao = conta_padrao_db
            
            # Calcular saldo total
            self.saldo_atual = sum(c.saldo_atual for c in self.contas_bancarias.values())
            
            # Carregar despesas (estrutura em memória para compatibilidade)
            # Vamos carregar apenas dados dos últimos 2 anos para não sobrecarregar
            ano_atual = date.today().year
            for ano in range(ano_atual - 1, ano_atual + 1):
                for mes in range(1, 13):
                    despesas_db = self.db.obter_despesas_mes(mes, ano)
                    if despesas_db:
                        mes_ano = f"{mes}/{ano}"
                        self.despesas[mes_ano] = []
                        for desp_data in despesas_db:
                            despesa = Despesa(
                                descricao=desp_data['descricao'],
                                valor=float(desp_data['valor']),
                                data_vencimento=desp_data['data_vencimento'].strftime('%d/%m/%Y'),
                                categoria=desp_data['categoria']
                            )
                            despesa.pago = bool(desp_data['pago'])
                            if desp_data['data_pagamento']:
                                despesa.data_pagamento = desp_data['data_pagamento']
                            despesa.id = desp_data['id']  # Armazenar ID do banco
                            self.despesas[mes_ano].append(despesa)
            
            # Carregar receitas
            for ano in range(ano_atual - 1, ano_atual + 1):
                for mes in range(1, 13):
                    receitas_db = self.db.obter_receitas_mes(mes, ano)
                    if receitas_db:
                        mes_ano = f"{mes}/{ano}"
                        self.receitas[mes_ano] = []
                        for rec_data in receitas_db:
                            receita = Receita(
                                descricao=rec_data['descricao'],
                                valor=float(rec_data['valor']),
                                data_recebimento=rec_data['data_recebimento'].strftime('%d/%m/%Y'),
                                categoria=rec_data['categoria']
                            )
                            receita.id = rec_data['id']  # Armazenar ID do banco
                            self.receitas[mes_ano].append(receita)
            
            # Carregar metas
            for ano in range(ano_atual - 1, ano_atual + 1):
                for mes in range(1, 13):
                    metas_db = self.db.obter_metas_mes(mes, ano)
                    if metas_db:
                        mes_ano = f"{mes}/{ano}"
                        self.metas_gastos[mes_ano] = []
                        for meta_data in metas_db:
                            meta = MetaGasto.from_db(meta_data)
                            self.metas_gastos[mes_ano].append(meta)
            
        except Exception as e:
            print(f"⚠️  Erro ao carregar dados: {e}")
    
    def salvar_dados(self):
        """Salva dados no MySQL - chamado automaticamente após operações"""
        # Com MySQL, os dados já são salvos em tempo real
        # Este método mantém compatibilidade com a interface antiga
        # Sincronizar quaisquer alterações pendentes
        try:
            # Atualizar status de despesas que foram marcadas como pagas/não pagas
            for mes_ano, despesas in self.despesas.items():
                for despesa in despesas:
                    if hasattr(despesa, 'id'):
                        # Verificar se precisa atualizar no banco
                        despesas_db = self.db.obter_despesas_mes(
                            int(mes_ano.split('/')[0]),
                            int(mes_ano.split('/')[1])
                        )
                        desp_db = next((d for d in despesas_db if d['id'] == despesa.id), None)
                        if desp_db:
                            # Se o status mudou, atualizar no banco
                            if despesa.pago != desp_db['pago']:
                                if despesa.pago:
                                    data_pag = despesa.data_pagamento.strftime('%Y-%m-%d %H:%M:%S') if despesa.data_pagamento else None
                                    self.db.marcar_despesa_paga(despesa.id, data_pag)
                                else:
                                    self.db.marcar_despesa_nao_paga(despesa.id)
        except Exception as e:
            print(f"⚠️  Aviso ao sincronizar dados: {e}")
    
    def criar_conta_bancaria(self, nome: str, banco: str, saldo_inicial: float = 0.0):
        """Cria uma nova conta bancária"""
        if nome in self.contas_bancarias:
            raise ValueError(f"Conta '{nome}' já existe")
        
        conta_id = self.db.criar_conta_bancaria(nome, banco, saldo_inicial)
        if conta_id:
            # Recarregar conta
            conta_data = self.db.obter_conta_por_id(conta_id)
            conta = ContaBancaria.from_db(conta_data)
            self.contas_bancarias[nome] = conta
            
            # Atualizar saldo total
            self.saldo_atual = sum(c.saldo_atual for c in self.contas_bancarias.values())
    
    def obter_contas_bancarias(self) -> List[str]:
        """Retorna lista de nomes das contas bancárias"""
        return list(self.contas_bancarias.keys())
    
    def obter_saldo_conta(self, nome_conta: str) -> float:
        """Obtém o saldo atual de uma conta"""
        if nome_conta not in self.contas_bancarias:
            return 0.0
        return self.contas_bancarias[nome_conta].saldo_atual
    
    def atualizar_saldo_conta(self, nome_conta: str, novo_saldo: float, operacao: str = "Atualização manual"):
        """Atualiza o saldo de uma conta"""
        if nome_conta not in self.contas_bancarias:
            raise ValueError(f"Conta '{nome_conta}' não encontrada")
        
        conta = self.contas_bancarias[nome_conta]
        valor_operacao = novo_saldo - conta.saldo_atual
        
        # Atualizar no banco
        self.db.atualizar_saldo_conta(conta.id, novo_saldo, operacao, valor_operacao)
        
        # Atualizar em memória
        conta.saldo_atual = novo_saldo
        
        # Atualizar saldo geral
        self.saldo_atual = sum(c.saldo_atual for c in self.contas_bancarias.values())
    
    def editar_conta_bancaria(self, nome_conta: str, novo_nome: str = None, 
                             novo_banco: str = None) -> bool:
        """Edita informações de uma conta bancária"""
        if nome_conta not in self.contas_bancarias:
            return False
        
        conta = self.contas_bancarias[nome_conta]
        
        # Atualizar no banco
        sucesso = self.db.editar_conta_bancaria(conta.id, novo_nome, novo_banco)
        
        if sucesso:
            # Atualizar em memória
            if novo_nome and novo_nome != nome_conta:
                if novo_nome in self.contas_bancarias:
                    return False
                
                conta.nome = novo_nome
                self.contas_bancarias[novo_nome] = conta
                del self.contas_bancarias[nome_conta]
                
                if self.conta_padrao == nome_conta:
                    self.conta_padrao = novo_nome
                    self.db.salvar_configuracao('conta_padrao', novo_nome)
            
            if novo_banco:
                conta.banco = novo_banco
            
            return True
        
        return False
    
    def remover_conta_bancaria(self, nome_conta: str) -> bool:
        """Remove uma conta bancária"""
        if nome_conta not in self.contas_bancarias:
            return False
        
        if len(self.contas_bancarias) <= 1:
            return False
        
        conta = self.contas_bancarias[nome_conta]
        
        # Remover do banco
        sucesso = self.db.remover_conta_bancaria(conta.id)
        
        if sucesso:
            # Remover da memória
            del self.contas_bancarias[nome_conta]
            
            # Atualizar conta padrão se necessário
            if self.conta_padrao == nome_conta:
                self.conta_padrao = list(self.contas_bancarias.keys())[0]
                self.db.salvar_configuracao('conta_padrao', self.conta_padrao)
            
            # Atualizar saldo total
            self.saldo_atual = sum(c.saldo_atual for c in self.contas_bancarias.values())
            
            return True
        
        return False
    
    def adicionar_despesa(self, despesa: Despesa, mes: int, ano: int):
        """Adiciona uma nova despesa"""
        mes_ano = self.obter_mes_ano(mes, ano)
        
        # Adicionar no banco
        despesa_id = self.db.adicionar_despesa(
            descricao=despesa.descricao,
            valor=despesa.valor,
            categoria=despesa.categoria,
            data_vencimento=despesa.data_vencimento.strftime('%Y-%m-%d'),
            mes=mes,
            ano=ano
        )
        
        if despesa_id:
            despesa.id = despesa_id
            
            # Adicionar em memória
            if mes_ano not in self.despesas:
                self.despesas[mes_ano] = []
            self.despesas[mes_ano].append(despesa)
    
    def adicionar_receita(self, receita: Receita, mes: int, ano: int):
        """Adiciona uma nova receita"""
        mes_ano = self.obter_mes_ano(mes, ano)
        
        # Adicionar no banco
        receita_id = self.db.adicionar_receita(
            descricao=receita.descricao,
            valor=receita.valor,
            categoria=receita.categoria,
            data_recebimento=receita.data_recebimento.strftime('%Y-%m-%d'),
            mes=mes,
            ano=ano
        )
        
        if receita_id:
            receita.id = receita_id
            
            # Adicionar em memória
            if mes_ano not in self.receitas:
                self.receitas[mes_ano] = []
            self.receitas[mes_ano].append(receita)
    
    def obter_despesas_mes(self, mes: int, ano: int) -> List[Despesa]:
        """Obtém todas as despesas do mês (sempre recarrega do banco para garantir IDs)"""
        # Recarregar do banco para garantir que temos os IDs
        despesas_db = self.db.obter_despesas_mes(mes, ano)
        mes_ano = self.obter_mes_ano(mes, ano)
        
        # Atualizar cache em memória
        if despesas_db:
            self.despesas[mes_ano] = []
            for desp_data in despesas_db:
                despesa = Despesa(
                    descricao=desp_data['descricao'],
                    valor=float(desp_data['valor']),
                    data_vencimento=desp_data['data_vencimento'].strftime('%d/%m/%Y'),
                    categoria=desp_data['categoria']
                )
                despesa.pago = bool(desp_data['pago'])
                if desp_data['data_pagamento']:
                    despesa.data_pagamento = desp_data['data_pagamento']
                despesa.id = desp_data['id']  # Garantir que o ID está presente
                self.despesas[mes_ano].append(despesa)
        
        return self.despesas.get(mes_ano, [])
    
    def obter_receitas_mes(self, mes: int, ano: int) -> List[Receita]:
        """Obtém todas as receitas do mês (sempre recarrega do banco para garantir IDs)"""
        # Recarregar do banco para garantir que temos os IDs
        receitas_db = self.db.obter_receitas_mes(mes, ano)
        mes_ano = self.obter_mes_ano(mes, ano)
        
        # Atualizar cache em memória
        if receitas_db:
            self.receitas[mes_ano] = []
            for rec_data in receitas_db:
                receita = Receita(
                    descricao=rec_data['descricao'],
                    valor=float(rec_data['valor']),
                    data_recebimento=rec_data['data_recebimento'].strftime('%d/%m/%Y'),
                    categoria=rec_data['categoria']
                )
                receita.id = rec_data['id']  # Garantir que o ID está presente
                self.receitas[mes_ano].append(receita)
        
        return self.receitas.get(mes_ano, [])
    
    def processar_pagamento_despesa(self, despesa: Despesa, nome_conta: str = None, 
                                   data_pagamento: str = None, forcar_pagamento: bool = False):
        """Processa o pagamento de uma despesa atualizando o saldo automaticamente"""
        if nome_conta is None:
            nome_conta = self.conta_padrao
        
        if nome_conta not in self.contas_bancarias:
            raise ValueError(f"Conta '{nome_conta}' não encontrada")
        
        if despesa.pago:
            return False
        
        conta = self.contas_bancarias[nome_conta]
        
        if not forcar_pagamento and conta.saldo_atual < despesa.valor:
            return False
        
        # Atualizar saldo da conta
        novo_saldo = conta.saldo_atual - despesa.valor
        self.db.atualizar_saldo_conta(conta.id, novo_saldo, f"Pagamento: {despesa.descricao}", -despesa.valor)
        conta.saldo_atual = novo_saldo
        
        # Marcar despesa como paga no banco
        if data_pagamento is None:
            data_pagamento_db = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data_pagamento_br = datetime.now().strftime('%d/%m/%Y')
        else:
            # Se recebeu uma data, converter para os dois formatos
            try:
                # Tentar interpretar como formato brasileiro
                dt = datetime.strptime(data_pagamento, '%d/%m/%Y')
                data_pagamento_db = dt.strftime('%Y-%m-%d %H:%M:%S')
                data_pagamento_br = data_pagamento
            except ValueError:
                # Se já está no formato do banco, usar direto
                dt = datetime.strptime(data_pagamento, '%Y-%m-%d %H:%M:%S')
                data_pagamento_db = data_pagamento
                data_pagamento_br = dt.strftime('%d/%m/%Y')
        
        self.db.marcar_despesa_paga(despesa.id, data_pagamento_db)
        despesa.marcar_como_pago(data_pagamento_br)
        
        # Atualizar saldo total
        self.saldo_atual = sum(c.saldo_atual for c in self.contas_bancarias.values())
        
        return True
    
    def processar_receita(self, receita: Receita, nome_conta: str = None):
        """Processa uma receita atualizando o saldo automaticamente"""
        if nome_conta is None:
            nome_conta = self.conta_padrao
        
        if nome_conta not in self.contas_bancarias:
            raise ValueError(f"Conta '{nome_conta}' não encontrada")
        
        conta = self.contas_bancarias[nome_conta]
        novo_saldo = conta.saldo_atual + receita.valor
        
        self.db.atualizar_saldo_conta(conta.id, novo_saldo, f"Receita: {receita.descricao}", receita.valor)
        conta.saldo_atual = novo_saldo
        
        # Atualizar saldo total
        self.saldo_atual = sum(c.saldo_atual for c in self.contas_bancarias.values())
        
        return True
    
    def calcular_saldo_final(self, mes: int, ano: int) -> float:
        """
        Calcula o saldo final após todas as despesas.
        Sobrescreve o método da classe pai para usar múltiplas contas bancárias.
        """
        # Saldo inicial = soma de todas as contas
        saldo_inicial = sum(conta.saldo_atual for conta in self.contas_bancarias.values())
        
        # Total de receitas do mês
        total_receitas = self.calcular_total_receitas(mes, ano)
        
        # Total de despesas do mês
        total_despesas = self.calcular_total_despesas(mes, ano)
        
        return saldo_inicial + total_receitas - total_despesas
    
    def remover_despesa(self, despesa: Despesa, mes: int, ano: int) -> bool:
        """Remove uma despesa"""
        mes_ano = self.obter_mes_ano(mes, ano)
        sucesso = False
        
        # Remover do banco
        if hasattr(despesa, 'id') and despesa.id:
            sucesso = self.db.remover_despesa(despesa.id)
        else:
            print(f"⚠️  Aviso: Despesa '{despesa.descricao}' não possui ID para remover do banco")
            sucesso = False
        
        # Remover da memória
        if mes_ano in self.despesas:
            if despesa in self.despesas[mes_ano]:
                self.despesas[mes_ano].remove(despesa)
        
        return sucesso
    
    def remover_receita(self, receita: Receita, mes: int, ano: int) -> bool:
        """Remove uma receita"""
        mes_ano = self.obter_mes_ano(mes, ano)
        sucesso = False
        
        # Remover do banco
        if hasattr(receita, 'id') and receita.id:
            sucesso = self.db.remover_receita(receita.id)
        else:
            print(f"⚠️  Aviso: Receita '{receita.descricao}' não possui ID válido para remover do banco")
            sucesso = False
        
        # Remover da memória
        if mes_ano in self.receitas:
            if receita in self.receitas[mes_ano]:
                self.receitas[mes_ano].remove(receita)
        
        return sucesso
    
    # Métodos de carteira
    def obter_saldo_carteira(self) -> float:
        """Obtém o saldo da carteira"""
        return self.obter_saldo_conta("Carteira")
    
    def adicionar_dinheiro_carteira(self, valor: float, descricao: str = "Adição de dinheiro"):
        """Adiciona dinheiro à carteira"""
        if "Carteira" not in self.contas_bancarias:
            self.criar_conta_bancaria("Carteira", "Dinheiro em Espécie", 0.0)
        
        carteira = self.contas_bancarias["Carteira"]
        novo_saldo = carteira.saldo_atual + valor
        
        self.db.atualizar_saldo_conta(carteira.id, novo_saldo, descricao, valor)
        carteira.saldo_atual = novo_saldo
        
        self.saldo_atual = sum(c.saldo_atual for c in self.contas_bancarias.values())
        return True
    
    def remover_dinheiro_carteira(self, valor: float, descricao: str = "Retirada de dinheiro"):
        """Remove dinheiro da carteira"""
        if "Carteira" not in self.contas_bancarias:
            return False
        
        carteira = self.contas_bancarias["Carteira"]
        
        if carteira.saldo_atual < valor:
            return False
        
        novo_saldo = carteira.saldo_atual - valor
        
        self.db.atualizar_saldo_conta(carteira.id, novo_saldo, descricao, -valor)
        carteira.saldo_atual = novo_saldo
        
        self.saldo_atual = sum(c.saldo_atual for c in self.contas_bancarias.values())
        return True
    
    def transferir_para_carteira(self, nome_conta_origem: str, valor: float):
        """Transfere dinheiro de uma conta bancária para a carteira"""
        if nome_conta_origem not in self.contas_bancarias or "Carteira" not in self.contas_bancarias:
            return False
        
        conta_origem = self.contas_bancarias[nome_conta_origem]
        carteira = self.contas_bancarias["Carteira"]
        
        if conta_origem.saldo_atual < valor:
            return False
        
        # Remover da conta origem
        novo_saldo_origem = conta_origem.saldo_atual - valor
        self.db.atualizar_saldo_conta(conta_origem.id, novo_saldo_origem, "Transferência para carteira", -valor)
        conta_origem.saldo_atual = novo_saldo_origem
        
        # Adicionar à carteira
        novo_saldo_carteira = carteira.saldo_atual + valor
        self.db.atualizar_saldo_conta(carteira.id, novo_saldo_carteira, f"Transferência de {nome_conta_origem}", valor)
        carteira.saldo_atual = novo_saldo_carteira
        
        return True
    
    def transferir_da_carteira(self, nome_conta_destino: str, valor: float):
        """Transfere dinheiro da carteira para uma conta bancária"""
        if nome_conta_destino not in self.contas_bancarias or "Carteira" not in self.contas_bancarias:
            return False
        
        carteira = self.contas_bancarias["Carteira"]
        conta_destino = self.contas_bancarias[nome_conta_destino]
        
        if carteira.saldo_atual < valor:
            return False
        
        # Remover da carteira
        novo_saldo_carteira = carteira.saldo_atual - valor
        self.db.atualizar_saldo_conta(carteira.id, novo_saldo_carteira, f"Transferência para {nome_conta_destino}", -valor)
        carteira.saldo_atual = novo_saldo_carteira
        
        # Adicionar à conta destino
        novo_saldo_destino = conta_destino.saldo_atual + valor
        self.db.atualizar_saldo_conta(conta_destino.id, novo_saldo_destino, "Transferência da carteira", valor)
        conta_destino.saldo_atual = novo_saldo_destino
        
        return True
    
    def transferir_entre_contas(self, nome_conta_origem: str, nome_conta_destino: str, valor: float):
        """Transfere dinheiro entre duas contas bancárias"""
        if nome_conta_origem not in self.contas_bancarias or nome_conta_destino not in self.contas_bancarias:
            return False
        
        if nome_conta_origem == nome_conta_destino:
            return False
        
        conta_origem = self.contas_bancarias[nome_conta_origem]
        conta_destino = self.contas_bancarias[nome_conta_destino]
        
        if conta_origem.saldo_atual < valor:
            return False
        
        # Remover da conta origem
        novo_saldo_origem = conta_origem.saldo_atual - valor
        self.db.atualizar_saldo_conta(conta_origem.id, novo_saldo_origem, f"Transferência para {nome_conta_destino}", -valor)
        conta_origem.saldo_atual = novo_saldo_origem
        
        # Adicionar à conta destino
        novo_saldo_destino = conta_destino.saldo_atual + valor
        self.db.atualizar_saldo_conta(conta_destino.id, novo_saldo_destino, f"Transferência de {nome_conta_origem}", valor)
        conta_destino.saldo_atual = novo_saldo_destino
        
        return True
    
    # Métodos de metas
    def criar_meta_gasto(self, categoria: str, limite_mensal: float, mes: int, ano: int):
        """Cria uma meta de gasto para uma categoria"""
        mes_ano = self.obter_mes_ano(mes, ano)
        
        # Criar no banco
        meta_id = self.db.criar_meta_gasto(categoria, limite_mensal, mes, ano)
        
        if meta_id:
            # Recarregar metas do mês
            metas_db = self.db.obter_metas_mes(mes, ano)
            self.metas_gastos[mes_ano] = []
            for meta_data in metas_db:
                meta = MetaGasto.from_db(meta_data)
                self.metas_gastos[mes_ano].append(meta)
            
            # Atualizar gastos
            self.atualizar_gastos_metas(mes, ano)
    
    def atualizar_gastos_metas(self, mes: int, ano: int):
        """Atualiza os gastos atuais das metas"""
        self.db.atualizar_gastos_metas(mes, ano)
        
        # Recarregar metas atualizadas
        mes_ano = self.obter_mes_ano(mes, ano)
        metas_db = self.db.obter_metas_mes(mes, ano)
        self.metas_gastos[mes_ano] = []
        for meta_data in metas_db:
            meta = MetaGasto.from_db(meta_data)
            self.metas_gastos[mes_ano].append(meta)
    
    def obter_alertas_metas(self, mes: int, ano: int) -> List[str]:
        """Obtém alertas de metas excedidas ou próximas do limite"""
        mes_ano = self.obter_mes_ano(mes, ano)
        if mes_ano not in self.metas_gastos:
            return []
        
        alertas = []
        self.atualizar_gastos_metas(mes, ano)
        
        for meta in self.metas_gastos[mes_ano]:
            percentual = meta.percentual_usado()
            if percentual >= 100:
                alertas.append(f"🚨 Meta EXCEDIDA para '{meta.categoria}': R$ {meta.gasto_atual:.2f} / R$ {meta.limite_mensal:.2f} ({percentual:.1f}%)")
            elif percentual >= 80:
                alertas.append(f"⚠️ Meta próxima do limite para '{meta.categoria}': R$ {meta.gasto_atual:.2f} / R$ {meta.limite_mensal:.2f} ({percentual:.1f}%)")
        
        return alertas
    
    # Métodos de busca
    def buscar_despesas(self, termo: str = "", categoria: str = "", valor_min: float = 0, 
                       valor_max: float = float('inf'), apenas_pagas: bool = None,
                       data_inicio: str = "", data_fim: str = "") -> List[Tuple[Despesa, int, int]]:
        """Busca despesas com filtros avançados"""
        filtros = {
            'termo': termo,
            'categoria': categoria,
            'valor_min': valor_min,
            'valor_max': valor_max,
            'pago': apenas_pagas,
            'data_inicio': data_inicio,
            'data_fim': data_fim
        }
        
        resultados_db = self.db.buscar_despesas(filtros)
        
        resultados = []
        for desp_data in resultados_db:
            despesa = Despesa(
                descricao=desp_data['descricao'],
                valor=float(desp_data['valor']),
                data_vencimento=desp_data['data_vencimento'].strftime('%d/%m/%Y'),
                categoria=desp_data['categoria']
            )
            despesa.pago = bool(desp_data['pago'])
            if desp_data['data_pagamento']:
                despesa.data_pagamento = desp_data['data_pagamento']
            despesa.id = desp_data['id']
            
            resultados.append((despesa, desp_data['mes'], desp_data['ano']))
        
        return resultados
    
    def buscar_receitas(self, termo: str = "", categoria: str = "", valor_min: float = 0,
                       valor_max: float = float('inf'), data_inicio: str = "", 
                       data_fim: str = "") -> List[Tuple[Receita, int, int]]:
        """Busca receitas com filtros avançados"""
        filtros = {
            'termo': termo,
            'categoria': categoria,
            'valor_min': valor_min,
            'valor_max': valor_max,
            'data_inicio': data_inicio,
            'data_fim': data_fim
        }
        
        resultados_db = self.db.buscar_receitas(filtros)
        
        resultados = []
        for rec_data in resultados_db:
            receita = Receita(
                descricao=rec_data['descricao'],
                valor=float(rec_data['valor']),
                data_recebimento=rec_data['data_recebimento'].strftime('%d/%m/%Y'),
                categoria=rec_data['categoria']
            )
            receita.id = rec_data['id']
            
            resultados.append((receita, rec_data['mes'], rec_data['ano']))
        
        return resultados
    
    def obter_despesas_vencendo(self, dias: int = 7) -> List[Tuple[Despesa, int, int]]:
        """Obtém despesas que vencem nos próximos X dias"""
        hoje = date.today()
        data_limite = date.fromordinal(hoje.toordinal() + dias)
        
        despesas_vencendo = []
        
        for mes_ano, despesas in self.despesas.items():
            mes, ano = mes_ano.split('/')
            mes, ano = int(mes), int(ano)
            
            for despesa in despesas:
                if not despesa.pago and hoje <= despesa.data_vencimento <= data_limite:
                    despesas_vencendo.append((despesa, mes, ano))
        
        return sorted(despesas_vencendo, key=lambda x: x[0].data_vencimento)
    
    # Métodos de gráficos (mantidos do original)
    def gerar_grafico_gastos_categoria(self, mes: int, ano: int, salvar_arquivo: bool = True):
        """Gera gráfico de pizza dos gastos por categoria"""
        despesas = self.obter_despesas_mes(mes, ano)
        if not despesas:
            print("Nenhuma despesa encontrada para gerar gráfico.")
            return
        
        gastos_categoria = defaultdict(float)
        for despesa in despesas:
            if despesa.pago:
                gastos_categoria[despesa.categoria] += despesa.valor
        
        if not gastos_categoria:
            print("Nenhuma despesa paga encontrada para gerar gráfico.")
            return
        
        plt.figure(figsize=(10, 8))
        categorias = list(gastos_categoria.keys())
        valores = list(gastos_categoria.values())
        
        plt.pie(valores, labels=categorias, autopct='%1.1f%%', startangle=90)
        plt.title(f'Gastos por Categoria - {self.obter_mes_nome(mes)}/{ano}')
        plt.axis('equal')
        
        if salvar_arquivo:
            nome_arquivo = f'gastos_categoria_{mes:02d}_{ano}.png'
            plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
            print(f"Gráfico salvo como: {nome_arquivo}")
        
        plt.show()
    
    def gerar_grafico_comparativo_mensal(self, ano: int, salvar_arquivo: bool = True):
        """Gera gráfico comparativo de gastos e receitas por mês"""
        meses = []
        receitas_mes = []
        despesas_mes = []
        
        for mes in range(1, 13):
            total_receitas = self.calcular_total_receitas(mes, ano)
            total_despesas = self.calcular_total_despesas_pagas(mes, ano)
            
            if total_receitas > 0 or total_despesas > 0:
                meses.append(self.obter_mes_nome(mes)[:3])
                receitas_mes.append(total_receitas)
                despesas_mes.append(total_despesas)
        
        if not meses:
            print("Nenhum dado encontrado para gerar gráfico comparativo.")
            return
        
        plt.figure(figsize=(12, 6))
        x = range(len(meses))
        width = 0.35
        
        plt.bar([i - width/2 for i in x], receitas_mes, width, label='Receitas', color='green', alpha=0.7)
        plt.bar([i + width/2 for i in x], despesas_mes, width, label='Despesas', color='red', alpha=0.7)
        
        plt.xlabel('Meses')
        plt.ylabel('Valor (R$)')
        plt.title(f'Comparativo Mensal - {ano}')
        plt.xticks(x, meses)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        for i, (receita, despesa) in enumerate(zip(receitas_mes, despesas_mes)):
            if receita > 0:
                plt.text(i - width/2, receita + max(receitas_mes) * 0.01, f'R${receita:.0f}', 
                        ha='center', va='bottom', fontsize=8)
            if despesa > 0:
                plt.text(i + width/2, despesa + max(despesas_mes) * 0.01, f'R${despesa:.0f}', 
                        ha='center', va='bottom', fontsize=8)
        
        if salvar_arquivo:
            nome_arquivo = f'comparativo_mensal_{ano}.png'
            plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
            print(f"Gráfico salvo como: {nome_arquivo}")
        
        plt.show()
    
    def obter_mes_nome(self, mes: int) -> str:
        """Retorna o nome do mês"""
        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        return meses.get(mes, "Mês Inválido")


if __name__ == "__main__":
    print("Sistema Avançado de Controle de Gastos com MySQL iniciado!")
    print("Execute o arquivo 'main_avancado.py' para usar a interface completa.")

