from datetime import datetime, date
import json
import os
from typing import List, Dict, Optional, Tuple
from controle_gastos import ControleFinanceiro, Despesa, Receita
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class ContaBancaria:
    """Classe para representar uma conta bancária"""
    
    def __init__(self, nome: str, banco: str, saldo_inicial: float = 0.0):
        self.nome = nome
        self.banco = banco
        self.saldo_atual = saldo_inicial
        self.historico_saldo = [{
            'data': datetime.now().isoformat(),
            'saldo_anterior': 0.0,
            'saldo_novo': saldo_inicial,
            'operacao': 'Saldo inicial',
            'valor': saldo_inicial
        }]
    
    def atualizar_saldo(self, novo_saldo: float, operacao: str, valor: float = 0.0):
        """Atualiza o saldo e registra no histórico"""
        saldo_anterior = self.saldo_atual
        self.saldo_atual = novo_saldo
        
        self.historico_saldo.append({
            'data': datetime.now().isoformat(),
            'saldo_anterior': saldo_anterior,
            'saldo_novo': novo_saldo,
            'operacao': operacao,
            'valor': valor
        })
    
    def to_dict(self) -> Dict:
        """Converte a conta para dicionário"""
        return {
            'nome': self.nome,
            'banco': self.banco,
            'saldo_atual': self.saldo_atual,
            'historico_saldo': self.historico_saldo
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Cria uma conta a partir de um dicionário"""
        conta = cls(data['nome'], data['banco'], 0.0)
        conta.saldo_atual = data['saldo_atual']
        conta.historico_saldo = data.get('historico_saldo', [])
        return conta

class MetaGasto:
    """Classe para representar metas de gastos por categoria"""
    
    def __init__(self, categoria: str, limite_mensal: float, mes: int, ano: int):
        self.categoria = categoria
        self.limite_mensal = limite_mensal
        self.mes = mes
        self.ano = ano
        self.gasto_atual = 0.0
        self.alertas_enviados = []
    
    def atualizar_gasto(self, valor: float):
        """Atualiza o gasto atual da categoria"""
        self.gasto_atual += valor
    
    def percentual_usado(self) -> float:
        """Retorna o percentual do limite usado"""
        if self.limite_mensal == 0:
            return 0.0
        return (self.gasto_atual / self.limite_mensal) * 100
    
    def precisa_alerta(self) -> bool:
        """Verifica se precisa enviar alerta"""
        percentual = self.percentual_usado()
        return percentual >= 80 and '80%' not in self.alertas_enviados
    
    def to_dict(self) -> Dict:
        return {
            'categoria': self.categoria,
            'limite_mensal': self.limite_mensal,
            'mes': self.mes,
            'ano': self.ano,
            'gasto_atual': self.gasto_atual,
            'alertas_enviados': self.alertas_enviados
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        meta = cls(data['categoria'], data['limite_mensal'], data['mes'], data['ano'])
        meta.gasto_atual = data.get('gasto_atual', 0.0)
        meta.alertas_enviados = data.get('alertas_enviados', [])
        return meta

class ControleFinanceiroAvancado(ControleFinanceiro):
    """Versão avançada do controle financeiro com novas funcionalidades"""
    
    def __init__(self):
        super().__init__()
        self.contas_bancarias: Dict[str, ContaBancaria] = {}
        self.metas_gastos: Dict[str, List[MetaGasto]] = {}
        self.conta_padrao = "Carteira"  # Carteira como conta padrão
        self.arquivo_dados = "dados_financeiros_avancado.json"
        
        # Migrar dados antigos se existirem
        self.migrar_dados_antigos()
        self.carregar_dados()
        
        # Criar carteira padrão se não existir (sempre primeiro)
        if "Carteira" not in self.contas_bancarias:
            self.criar_conta_bancaria("Carteira", "Dinheiro em Espécie", 0.0)
        
        # Criar conta bancária padrão se não existir
        if not self.contas_bancarias or len(self.contas_bancarias) == 1:  # Apenas carteira
            self.criar_conta_bancaria("Conta Principal", "Banco Principal", 0.0)
        
        # Sincronizar saldo atual com soma das contas
        self.saldo_atual = sum(c.saldo_atual for c in self.contas_bancarias.values())
    
    def migrar_dados_antigos(self):
        """Migra dados do sistema antigo para o novo formato"""
        arquivo_antigo = "dados_financeiros.json"
        if os.path.exists(arquivo_antigo) and not os.path.exists(self.arquivo_dados):
            try:
                with open(arquivo_antigo, 'r', encoding='utf-8') as f:
                    dados_antigos = json.load(f)
                
                # Migrar saldos antigos para conta principal
                saldos_antigos = dados_antigos.get('saldo_banco', {})
                if saldos_antigos:
                    conta_principal = ContaBancaria("Conta Principal", "Banco Principal", 0.0)
                    for mes_ano, saldo in saldos_antigos.items():
                        conta_principal.atualizar_saldo(saldo, f"Migração - {mes_ano}", saldo)
                    self.contas_bancarias["Conta Principal"] = conta_principal
                
                # Migrar despesas e receitas
                self.despesas = {}
                self.receitas = {}
                
                for mes_ano, lista_despesas in dados_antigos.get('despesas', {}).items():
                    self.despesas[mes_ano] = [Despesa.from_dict(d) for d in lista_despesas]
                
                for mes_ano, lista_receitas in dados_antigos.get('receitas', {}).items():
                    self.receitas[mes_ano] = [Receita.from_dict(r) for r in lista_receitas]
                
                self.salvar_dados()
                print("✅ Dados migrados com sucesso para o novo formato!")
                
            except Exception as e:
                print(f"⚠️ Erro na migração: {e}")
    
    def criar_conta_bancaria(self, nome: str, banco: str, saldo_inicial: float = 0.0):
        """Cria uma nova conta bancária"""
        if nome in self.contas_bancarias:
            raise ValueError(f"Conta '{nome}' já existe")
        
        self.contas_bancarias[nome] = ContaBancaria(nome, banco, saldo_inicial)
        self.salvar_dados()
    
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
        conta.atualizar_saldo(novo_saldo, operacao, valor_operacao)
        
        # Atualizar saldo geral do sistema
        self.saldo_atual = sum(c.saldo_atual for c in self.contas_bancarias.values())
        
        self.salvar_dados()
    
    def editar_conta_bancaria(self, nome_conta: str, novo_nome: str = None, 
                             novo_banco: str = None) -> bool:
        """Edita informações de uma conta bancária"""
        if nome_conta not in self.contas_bancarias:
            return False
        
        conta = self.contas_bancarias[nome_conta]
        
        # Se o nome mudou, precisamos recriar a entrada no dicionário
        if novo_nome and novo_nome != nome_conta:
            if novo_nome in self.contas_bancarias:
                return False  # Nome já existe
            
            # Atualizar nome da conta
            conta.nome = novo_nome
            
            # Mover para nova chave
            self.contas_bancarias[novo_nome] = conta
            del self.contas_bancarias[nome_conta]
            
            # Atualizar conta padrão se necessário
            if self.conta_padrao == nome_conta:
                self.conta_padrao = novo_nome
        
        # Atualizar banco
        if novo_banco:
            conta.banco = novo_banco
        
        self.salvar_dados()
        return True
    
    def remover_conta_bancaria(self, nome_conta: str) -> bool:
        """Remove uma conta bancária"""
        if nome_conta not in self.contas_bancarias:
            return False
        
        # Não permitir remoção se for a única conta
        if len(self.contas_bancarias) <= 1:
            return False
        
        # Remover conta
        del self.contas_bancarias[nome_conta]
        
        # Se era a conta padrão, definir outra como padrão
        if self.conta_padrao == nome_conta:
            self.conta_padrao = list(self.contas_bancarias.keys())[0]
        
        # Atualizar saldo geral do sistema
        self.saldo_atual = sum(c.saldo_atual for c in self.contas_bancarias.values())
        
        self.salvar_dados()
        return True
    
    def processar_pagamento_despesa(self, despesa: Despesa, nome_conta: str = None, data_pagamento: str = None, forcar_pagamento: bool = False):
        """Processa o pagamento de uma despesa atualizando o saldo automaticamente"""
        if nome_conta is None:
            nome_conta = self.conta_padrao
        
        if nome_conta not in self.contas_bancarias:
            raise ValueError(f"Conta '{nome_conta}' não encontrada")
        
        if despesa.pago:
            return False  # Despesa já foi paga
        
        conta = self.contas_bancarias[nome_conta]
        
        # Verificar se há saldo suficiente (apenas se não forçar pagamento)
        if not forcar_pagamento and conta.saldo_atual < despesa.valor:
            return False  # Saldo insuficiente
        
        novo_saldo = conta.saldo_atual - despesa.valor
        conta.atualizar_saldo(novo_saldo, f"Pagamento: {despesa.descricao}", -despesa.valor)
        
        # Marcar despesa como paga com data/hora
        despesa.marcar_como_pago(data_pagamento)
        
        # Atualizar saldo geral do sistema
        self.saldo_atual = sum(c.saldo_atual for c in self.contas_bancarias.values())
        
        self.salvar_dados()
        return True
    
    def processar_receita(self, receita: Receita, nome_conta: str = None):
        """Processa uma receita atualizando o saldo automaticamente"""
        if nome_conta is None:
            nome_conta = self.conta_padrao
        
        if nome_conta not in self.contas_bancarias:
            raise ValueError(f"Conta '{nome_conta}' não encontrada")
        
        conta = self.contas_bancarias[nome_conta]
        novo_saldo = conta.saldo_atual + receita.valor
        conta.atualizar_saldo(novo_saldo, f"Receita: {receita.descricao}", receita.valor)
        
        # Atualizar saldo geral do sistema
        self.saldo_atual = sum(c.saldo_atual for c in self.contas_bancarias.values())
        
        self.salvar_dados()
        return True
    
    def obter_saldo_carteira(self) -> float:
        """Obtém o saldo da carteira"""
        if "Carteira" in self.contas_bancarias:
            return self.contas_bancarias["Carteira"].saldo_atual
        return 0.0
    
    def adicionar_dinheiro_carteira(self, valor: float, descricao: str = "Adição de dinheiro"):
        """Adiciona dinheiro à carteira"""
        if "Carteira" not in self.contas_bancarias:
            self.criar_conta_bancaria("Carteira", "Dinheiro em Espécie", 0.0)
        
        carteira = self.contas_bancarias["Carteira"]
        novo_saldo = carteira.saldo_atual + valor
        carteira.atualizar_saldo(novo_saldo, descricao, valor)
        
        # Atualizar saldo geral do sistema
        self.saldo_atual = sum(c.saldo_atual for c in self.contas_bancarias.values())
        
        self.salvar_dados()
        return True
    
    def remover_dinheiro_carteira(self, valor: float, descricao: str = "Retirada de dinheiro"):
        """Remove dinheiro da carteira"""
        if "Carteira" not in self.contas_bancarias:
            return False
        
        carteira = self.contas_bancarias["Carteira"]
        
        # Verificar se há saldo suficiente
        if carteira.saldo_atual < valor:
            return False
        
        novo_saldo = carteira.saldo_atual - valor
        carteira.atualizar_saldo(novo_saldo, descricao, -valor)
        
        # Atualizar saldo geral do sistema
        self.saldo_atual = sum(c.saldo_atual for c in self.contas_bancarias.values())
        
        self.salvar_dados()
        return True
    
    def transferir_para_carteira(self, nome_conta_origem: str, valor: float):
        """Transfere dinheiro de uma conta bancária para a carteira"""
        if nome_conta_origem not in self.contas_bancarias or "Carteira" not in self.contas_bancarias:
            return False
        
        conta_origem = self.contas_bancarias[nome_conta_origem]
        carteira = self.contas_bancarias["Carteira"]
        
        # Verificar se há saldo suficiente na conta origem
        if conta_origem.saldo_atual < valor:
            return False
        
        # Remover da conta origem
        novo_saldo_origem = conta_origem.saldo_atual - valor
        conta_origem.atualizar_saldo(novo_saldo_origem, f"Transferência para carteira", -valor)
        
        # Adicionar à carteira
        novo_saldo_carteira = carteira.saldo_atual + valor
        carteira.atualizar_saldo(novo_saldo_carteira, f"Transferência de {nome_conta_origem}", valor)
        
        # Saldo geral permanece o mesmo (transferência interna)
        self.salvar_dados()
        return True
    
    def transferir_da_carteira(self, nome_conta_destino: str, valor: float):
        """Transfere dinheiro da carteira para uma conta bancária"""
        if nome_conta_destino not in self.contas_bancarias or "Carteira" not in self.contas_bancarias:
            return False
        
        carteira = self.contas_bancarias["Carteira"]
        conta_destino = self.contas_bancarias[nome_conta_destino]
        
        # Verificar se há saldo suficiente na carteira
        if carteira.saldo_atual < valor:
            return False
        
        # Remover da carteira
        novo_saldo_carteira = carteira.saldo_atual - valor
        carteira.atualizar_saldo(novo_saldo_carteira, f"Transferência para {nome_conta_destino}", -valor)
        
        # Adicionar à conta destino
        novo_saldo_destino = conta_destino.saldo_atual + valor
        conta_destino.atualizar_saldo(novo_saldo_destino, f"Transferência da carteira", valor)
        
        # Saldo geral permanece o mesmo (transferência interna)
        self.salvar_dados()
        return True
    
    def criar_meta_gasto(self, categoria: str, limite_mensal: float, mes: int, ano: int):
        """Cria uma meta de gasto para uma categoria"""
        mes_ano = self.obter_mes_ano(mes, ano)
        if mes_ano not in self.metas_gastos:
            self.metas_gastos[mes_ano] = []
        
        # Verificar se já existe meta para esta categoria no mês
        for meta in self.metas_gastos[mes_ano]:
            if meta.categoria == categoria:
                meta.limite_mensal = limite_mensal
                self.salvar_dados()
                return
        
        # Criar nova meta
        nova_meta = MetaGasto(categoria, limite_mensal, mes, ano)
        self.metas_gastos[mes_ano].append(nova_meta)
        self.atualizar_gastos_metas(mes, ano)
        self.salvar_dados()
    
    def atualizar_gastos_metas(self, mes: int, ano: int):
        """Atualiza os gastos atuais das metas baseado nas despesas"""
        mes_ano = self.obter_mes_ano(mes, ano)
        if mes_ano not in self.metas_gastos:
            return
        
        # Resetar gastos atuais
        for meta in self.metas_gastos[mes_ano]:
            meta.gasto_atual = 0.0
        
        # Calcular gastos por categoria
        despesas = self.obter_despesas_mes(mes, ano)
        gastos_categoria = defaultdict(float)
        
        for despesa in despesas:
            if despesa.pago:
                gastos_categoria[despesa.categoria] += despesa.valor
        
        # Atualizar metas
        for meta in self.metas_gastos[mes_ano]:
            meta.gasto_atual = gastos_categoria.get(meta.categoria, 0.0)
    
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
    
    def buscar_despesas(self, termo: str = "", categoria: str = "", valor_min: float = 0, 
                       valor_max: float = float('inf'), apenas_pagas: bool = None,
                       data_inicio: str = "", data_fim: str = "") -> List[Tuple[Despesa, int, int]]:
        """Busca despesas com filtros avançados"""
        resultados = []
        
        for mes_ano, despesas in self.despesas.items():
            mes, ano = mes_ano.split('/')
            mes, ano = int(mes), int(ano)
            
            for despesa in despesas:
                # Filtro por termo na descrição
                if termo and termo.lower() not in despesa.descricao.lower():
                    continue
                
                # Filtro por categoria
                if categoria and categoria.lower() != despesa.categoria.lower():
                    continue
                
                # Filtro por valor
                if not (valor_min <= despesa.valor <= valor_max):
                    continue
                
                # Filtro por status de pagamento
                if apenas_pagas is not None and despesa.pago != apenas_pagas:
                    continue
                
                # Filtro por data
                if data_inicio:
                    try:
                        data_inicio_obj = datetime.strptime(data_inicio, "%d/%m/%Y").date()
                        if despesa.data_vencimento < data_inicio_obj:
                            continue
                    except ValueError:
                        pass
                
                if data_fim:
                    try:
                        data_fim_obj = datetime.strptime(data_fim, "%d/%m/%Y").date()
                        if despesa.data_vencimento > data_fim_obj:
                            continue
                    except ValueError:
                        pass
                
                resultados.append((despesa, mes, ano))
        
        return resultados
    
    def buscar_receitas(self, termo: str = "", categoria: str = "", valor_min: float = 0,
                       valor_max: float = float('inf'), data_inicio: str = "", 
                       data_fim: str = "") -> List[Tuple[Receita, int, int]]:
        """Busca receitas com filtros avançados"""
        resultados = []
        
        for mes_ano, receitas in self.receitas.items():
            mes, ano = mes_ano.split('/')
            mes, ano = int(mes), int(ano)
            
            for receita in receitas:
                # Filtro por termo na descrição
                if termo and termo.lower() not in receita.descricao.lower():
                    continue
                
                # Filtro por categoria
                if categoria and categoria.lower() != receita.categoria.lower():
                    continue
                
                # Filtro por valor
                if not (valor_min <= receita.valor <= valor_max):
                    continue
                
                # Filtro por data
                if data_inicio:
                    try:
                        data_inicio_obj = datetime.strptime(data_inicio, "%d/%m/%Y").date()
                        if receita.data_recebimento < data_inicio_obj:
                            continue
                    except ValueError:
                        pass
                
                if data_fim:
                    try:
                        data_fim_obj = datetime.strptime(data_fim, "%d/%m/%Y").date()
                        if receita.data_recebimento > data_fim_obj:
                            continue
                    except ValueError:
                        pass
                
                resultados.append((receita, mes, ano))
        
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
                meses.append(self.obter_mes_nome(mes)[:3])  # Abreviação do mês
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
        
        # Adicionar valores nas barras
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
    
    def salvar_dados(self):
        """Salva os dados em arquivo JSON (versão avançada)"""
        dados = {
            'despesas': {},
            'receitas': {},
            'contas_bancarias': {},
            'metas_gastos': {},
            'conta_padrao': self.conta_padrao
        }
        
        # Converter despesas para dicionário
        for mes_ano, lista_despesas in self.despesas.items():
            dados['despesas'][mes_ano] = [despesa.to_dict() for despesa in lista_despesas]
        
        # Converter receitas para dicionário
        for mes_ano, lista_receitas in self.receitas.items():
            dados['receitas'][mes_ano] = [receita.to_dict() for receita in lista_receitas]
        
        # Converter contas bancárias
        for nome, conta in self.contas_bancarias.items():
            dados['contas_bancarias'][nome] = conta.to_dict()
        
        # Converter metas de gastos
        for mes_ano, lista_metas in self.metas_gastos.items():
            dados['metas_gastos'][mes_ano] = [meta.to_dict() for meta in lista_metas]
        
        with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    
    def carregar_dados(self):
        """Carrega os dados do arquivo JSON (versão avançada)"""
        if not os.path.exists(self.arquivo_dados):
            return
        
        try:
            with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            # Carregar despesas
            for mes_ano, lista_despesas in dados.get('despesas', {}).items():
                self.despesas[mes_ano] = [Despesa.from_dict(d) for d in lista_despesas]
            
            # Carregar receitas
            for mes_ano, lista_receitas in dados.get('receitas', {}).items():
                self.receitas[mes_ano] = [Receita.from_dict(r) for r in lista_receitas]
            
            # Carregar contas bancárias
            for nome, dados_conta in dados.get('contas_bancarias', {}).items():
                self.contas_bancarias[nome] = ContaBancaria.from_dict(dados_conta)
            
            # Carregar metas de gastos
            for mes_ano, lista_metas in dados.get('metas_gastos', {}).items():
                self.metas_gastos[mes_ano] = [MetaGasto.from_dict(m) for m in lista_metas]
            
            # Carregar conta padrão (migrar para Carteira se for antigo)
            conta_padrao_salva = dados.get('conta_padrao', 'Carteira')
            if conta_padrao_salva == 'Conta Principal':
                self.conta_padrao = 'Carteira'  # Migrar para Carteira
            else:
                self.conta_padrao = conta_padrao_salva
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Erro ao carregar dados: {e}")
            print("Iniciando com dados vazios.")

    def exportar_backup_completo(self, nome_arquivo: str = None) -> bool:
        """Exporta backup completo dos dados em Excel"""
        try:
            import pandas as pd
            PANDAS_DISPONIVEL = True
        except ImportError:
            PANDAS_DISPONIVEL = False
            
        if not PANDAS_DISPONIVEL:
            print("❌ Pandas não está instalado. Execute: pip install pandas openpyxl")
            return False
        
        try:
            if nome_arquivo is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nome_arquivo = f"backup_completo_{timestamp}.xlsx"
            
            with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
                # Exportar todas as despesas
                todas_despesas = []
                for mes_ano, despesas in self.despesas.items():
                    for despesa in despesas:
                        todas_despesas.append({
                            'Mês/Ano': mes_ano,
                            'Descrição': despesa.descricao,
                            'Valor': despesa.valor,
                            'Categoria': despesa.categoria,
                            'Vencimento': despesa.data_vencimento.strftime('%d/%m/%Y'),
                            'Pago': 'Sim' if despesa.pago else 'Não',
                            'Data Pagamento': despesa.data_pagamento.strftime('%d/%m/%Y') if despesa.data_pagamento else ''
                        })
                
                if todas_despesas:
                    pd.DataFrame(todas_despesas).to_excel(writer, sheet_name='Todas as Despesas', index=False)
                
                # Exportar todas as receitas
                todas_receitas = []
                for mes_ano, receitas in self.receitas.items():
                    for receita in receitas:
                        todas_receitas.append({
                            'Mês/Ano': mes_ano,
                            'Descrição': receita.descricao,
                            'Valor': receita.valor,
                            'Categoria': receita.categoria,
                            'Data Recebimento': receita.data_recebimento.strftime('%d/%m/%Y')
                        })
                
                if todas_receitas:
                    pd.DataFrame(todas_receitas).to_excel(writer, sheet_name='Todas as Receitas', index=False)
                
                # Exportar contas
                dados_contas = []
                for nome_conta, conta in self.contas_bancarias.items():
                    dados_contas.append({
                        'Nome': nome_conta,
                        'Banco': conta.banco,
                        'Saldo Atual': conta.saldo_atual,
                        'Movimentações': len(conta.historico_saldo)
                    })
                
                if dados_contas:
                    pd.DataFrame(dados_contas).to_excel(writer, sheet_name='Contas Bancárias', index=False)
                
                # Exportar histórico completo das contas
                for nome_conta, conta in self.contas_bancarias.items():
                    if conta.historico_saldo:
                        historico_dados = []
                        for movimento in conta.historico_saldo:
                            data = datetime.fromisoformat(movimento['data'])
                            historico_dados.append({
                                'Data': data.strftime('%d/%m/%Y %H:%M'),
                                'Operação': movimento['operacao'],
                                'Saldo Anterior': movimento['saldo_anterior'],
                                'Saldo Novo': movimento['saldo_novo'],
                                'Variação': movimento['valor']
                            })
                        
                        if historico_dados:
                            sheet_name = f"Histórico {nome_conta}"[:31]  # Limite do Excel
                            pd.DataFrame(historico_dados).to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Exportar metas de gastos
                todas_metas = []
                for mes_ano, metas in self.metas_gastos.items():
                    for meta in metas:
                        todas_metas.append({
                            'Mês/Ano': mes_ano,
                            'Categoria': meta.categoria,
                            'Limite Mensal': meta.limite_mensal,
                            'Gasto Atual': meta.gasto_atual,
                            'Percentual Usado': meta.percentual_usado()
                        })
                
                if todas_metas:
                    pd.DataFrame(todas_metas).to_excel(writer, sheet_name='Metas de Gastos', index=False)
            
            print(f"✅ Backup completo exportado para: {nome_arquivo}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao exportar backup: {e}")
            return False
    
    def criar_backup_json(self, nome_arquivo: str = None) -> bool:
        """Cria backup completo em formato JSON"""
        try:
            if nome_arquivo is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nome_arquivo = f"backup_json_{timestamp}.json"
            
            # Criar cópia dos dados atuais
            dados_backup = {
                'data_backup': datetime.now().isoformat(),
                'versao_sistema': 'avancado_v1.0',
                'despesas': {},
                'receitas': {},
                'contas_bancarias': {},
                'metas_gastos': {},
                'conta_padrao': self.conta_padrao
            }
            
            # Converter despesas
            for mes_ano, lista_despesas in self.despesas.items():
                dados_backup['despesas'][mes_ano] = [despesa.to_dict() for despesa in lista_despesas]
            
            # Converter receitas
            for mes_ano, lista_receitas in self.receitas.items():
                dados_backup['receitas'][mes_ano] = [receita.to_dict() for receita in lista_receitas]
            
            # Converter contas bancárias
            for nome, conta in self.contas_bancarias.items():
                dados_backup['contas_bancarias'][nome] = conta.to_dict()
            
            # Converter metas de gastos
            for mes_ano, lista_metas in self.metas_gastos.items():
                dados_backup['metas_gastos'][mes_ano] = [meta.to_dict() for meta in lista_metas]
            
            # Salvar backup
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_backup, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Backup JSON criado: {nome_arquivo}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar backup JSON: {e}")
            return False
    
    def limpar_todos_dados(self, criar_backup: bool = True) -> bool:
        """Limpa todos os dados do sistema com opção de backup"""
        try:
            # Criar backup se solicitado
            if criar_backup:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nome_backup = f"backup_antes_limpeza_{timestamp}"
                
                print("💾 Criando backup antes da limpeza...")
                
                # Backup em JSON
                if not self.criar_backup_json(f"{nome_backup}.json"):
                    print("⚠️ Falha no backup JSON, mas continuando...")
                
                # Backup em Excel (se disponível)
                try:
                    import pandas as pd
                    if not self.exportar_backup_completo(f"{nome_backup}.xlsx"):
                        print("⚠️ Falha no backup Excel, mas continuando...")
                except ImportError:
                    print("ℹ️ Backup Excel não disponível (Pandas não instalado)")
            
            # Limpar todos os dados
            print("🗑️ Limpando todos os dados...")
            
            # Limpar despesas e receitas
            self.despesas.clear()
            self.receitas.clear()
            
            # Limpar metas de gastos
            self.metas_gastos.clear()
            
            # Resetar contas bancárias (manter apenas a conta principal)
            conta_principal = ContaBancaria("Conta Principal", "Banco Principal", 0.0)
            self.contas_bancarias.clear()
            self.contas_bancarias["Conta Principal"] = conta_principal
            self.conta_padrao = "Conta Principal"
            
            # Salvar dados limpos
            self.salvar_dados()
            
            print("✅ Todos os dados foram limpos com sucesso!")
            print("ℹ️ Sistema resetado para estado inicial.")
            
            if criar_backup:
                print(f"💾 Backups salvos com timestamp: {timestamp}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao limpar dados: {e}")
            return False
    
    def restaurar_backup_json(self, arquivo_backup: str) -> bool:
        """Restaura dados de um backup JSON"""
        try:
            if not os.path.exists(arquivo_backup):
                print(f"❌ Arquivo de backup não encontrado: {arquivo_backup}")
                return False
            
            print(f"📥 Restaurando backup de: {arquivo_backup}")
            
            with open(arquivo_backup, 'r', encoding='utf-8') as f:
                dados_backup = json.load(f)
            
            # Verificar versão do backup
            if 'versao_sistema' in dados_backup:
                print(f"ℹ️ Versão do backup: {dados_backup['versao_sistema']}")
            
            if 'data_backup' in dados_backup:
                data_backup = datetime.fromisoformat(dados_backup['data_backup'])
                print(f"ℹ️ Data do backup: {data_backup.strftime('%d/%m/%Y %H:%M')}")
            
            # Limpar dados atuais
            self.despesas.clear()
            self.receitas.clear()
            self.contas_bancarias.clear()
            self.metas_gastos.clear()
            
            # Restaurar despesas
            for mes_ano, lista_despesas in dados_backup.get('despesas', {}).items():
                self.despesas[mes_ano] = [Despesa.from_dict(d) for d in lista_despesas]
            
            # Restaurar receitas
            for mes_ano, lista_receitas in dados_backup.get('receitas', {}).items():
                self.receitas[mes_ano] = [Receita.from_dict(r) for r in lista_receitas]
            
            # Restaurar contas bancárias
            for nome, dados_conta in dados_backup.get('contas_bancarias', {}).items():
                self.contas_bancarias[nome] = ContaBancaria.from_dict(dados_conta)
            
            # Restaurar metas de gastos
            for mes_ano, lista_metas in dados_backup.get('metas_gastos', {}).items():
                self.metas_gastos[mes_ano] = [MetaGasto.from_dict(m) for m in lista_metas]
            
            # Restaurar conta padrão
            self.conta_padrao = dados_backup.get('conta_padrao', 'Conta Principal')
            
            # Salvar dados restaurados
            self.salvar_dados()
            
            print("✅ Backup restaurado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao restaurar backup: {e}")
            return False

if __name__ == "__main__":
    # Exemplo de uso das novas funcionalidades
    controle = ControleFinanceiroAvancado()
    print("Sistema Avançado de Controle de Gastos iniciado!")
    print("Execute o arquivo 'main_avancado.py' para usar a interface completa.")