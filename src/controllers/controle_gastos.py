from datetime import datetime, date
import json
import os
from typing import List, Dict, Optional

class Despesa:
    """Classe para representar uma despesa"""
    
    def __init__(self, descricao: str, valor: float, data_vencimento: str = None, pago: bool = False, categoria: str = "Geral", 
                 despesa_fixa: bool = False, tipo: str = "normal", pago_imediatamente: bool = False):
        self.descricao = descricao
        self.valor = valor
        
        # Para despesas pagas imediatamente, não há vencimento
        if pago_imediatamente or tipo == "instantanea":
            self.data_vencimento = None
            self.pago = True
            self.data_pagamento = date.today()
            self.tipo = "instantanea"
        else:
            self.data_vencimento = datetime.strptime(data_vencimento, "%d/%m/%Y").date() if data_vencimento else date.today()
            self.pago = pago
            self.data_pagamento = None
        
        self.categoria = categoria
        self.despesa_fixa = despesa_fixa  # True para gastos fixos (luz, água, aluguel)
        self.tipo = tipo  # "normal", "fixa", "instantanea"
        self.pago_imediatamente = pago_imediatamente  # True para despesas pagas na hora
    
    def marcar_como_pago(self, data_pagamento: str = None):
        """Marca a despesa como paga"""
        self.pago = True
        if data_pagamento:
            self.data_pagamento = datetime.strptime(data_pagamento, "%d/%m/%Y").date()
        else:
            self.data_pagamento = date.today()
    
    def marcar_como_nao_pago(self):
        """Marca a despesa como não paga"""
        # Não permite desmarcar despesas instantâneas
        if self.tipo != "instantanea":
            self.pago = False
            self.data_pagamento = None
    
    def is_gasto_fixo(self) -> bool:
        """Verifica se é um gasto fixo"""
        return self.despesa_fixa or self.tipo == "fixa"
    
    def is_despesa_instantanea(self) -> bool:
        """Verifica se é uma despesa paga imediatamente"""
        return self.tipo == "instantanea" or self.pago_imediatamente
    
    def is_despesa_normal(self) -> bool:
        """Verifica se é uma despesa normal (com vencimento)"""
        return self.tipo == "normal" and not self.despesa_fixa
    
    def obter_tipo_display(self) -> str:
        """Retorna o tipo da despesa para exibição"""
        if self.is_despesa_instantanea():
            return "Pago Imediatamente"
        elif self.is_gasto_fixo():
            return "Gasto Fixo"
        else:
            return "Despesa Normal"
    
    def to_dict(self) -> Dict:
        """Converte a despesa para dicionário"""
        return {
            'descricao': self.descricao,
            'valor': self.valor,
            'data_vencimento': self.data_vencimento.strftime("%d/%m/%Y") if self.data_vencimento else None,
            'pago': self.pago,
            'categoria': self.categoria,
            'data_pagamento': self.data_pagamento.strftime("%d/%m/%Y") if self.data_pagamento else None,
            'despesa_fixa': self.despesa_fixa,
            'tipo': self.tipo,
            'pago_imediatamente': self.pago_imediatamente
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Cria uma despesa a partir de um dicionário"""
        # Compatibilidade com dados antigos
        despesa_fixa = data.get('despesa_fixa', False)
        tipo = data.get('tipo', 'normal')
        pago_imediatamente = data.get('pago_imediatamente', False)
        
        despesa = cls(
            data['descricao'],
            data['valor'],
            data.get('data_vencimento'),  # Pode ser None para despesas instantâneas
            data.get('pago', False),
            data.get('categoria', 'Geral'),
            despesa_fixa,
            tipo,
            pago_imediatamente
        )
        
        if data.get('data_pagamento'):
            despesa.data_pagamento = datetime.strptime(data['data_pagamento'], "%d/%m/%Y").date()
        
        return despesa

class Receita:
    """Classe para representar uma receita"""
    
    def __init__(self, descricao: str, valor: float, data_recebimento: str, categoria: str = "Salário"):
        self.descricao = descricao
        self.valor = valor
        self.data_recebimento = datetime.strptime(data_recebimento, "%d/%m/%Y").date()
        self.categoria = categoria
    
    def to_dict(self) -> Dict:
        """Converte a receita para dicionário"""
        return {
            'descricao': self.descricao,
            'valor': self.valor,
            'data_recebimento': self.data_recebimento.strftime("%d/%m/%Y"),
            'categoria': self.categoria
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Cria uma receita a partir de um dicionário"""
        return cls(
            data['descricao'],
            data['valor'],
            data['data_recebimento'],
            data['categoria']
        )

class ControleFinanceiro:
    """Classe principal para controle financeiro"""
    
    def __init__(self):
        self.despesas: Dict[str, List[Despesa]] = {}
        self.receitas: Dict[str, List[Receita]] = {}
        self.saldo_banco: Dict[str, float] = {}
        self.saldo_atual: float = 0.0  # Saldo automático atual
        self.historico_saldo: List[Dict] = []  # Histórico de movimentações
        self.arquivo_dados = "dados_financeiros.json"
        self.carregar_dados()
    
    def obter_mes_ano(self, mes: int, ano: int) -> str:
        """Retorna string no formato MM/YYYY"""
        return f"{mes:02d}/{ano}"
    
    def adicionar_despesa(self, despesa: Despesa, mes: int, ano: int):
        """Adiciona uma despesa ao mês especificado"""
        mes_ano = self.obter_mes_ano(mes, ano)
        if mes_ano not in self.despesas:
            self.despesas[mes_ano] = []
        self.despesas[mes_ano].append(despesa)
        self.salvar_dados()
    
    def adicionar_receita(self, receita: Receita, mes: int, ano: int):
        """Adiciona uma receita ao mês especificado"""
        mes_ano = self.obter_mes_ano(mes, ano)
        if mes_ano not in self.receitas:
            self.receitas[mes_ano] = []
        self.receitas[mes_ano].append(receita)
        self.salvar_dados()
    
    def definir_saldo_banco(self, saldo: float, mes: int, ano: int):
        """Define o saldo do banco para o mês"""
        mes_ano = self.obter_mes_ano(mes, ano)
        self.saldo_banco[mes_ano] = saldo
        self.salvar_dados()
    
    def obter_saldo_banco(self, mes: int, ano: int) -> float:
        """Obtém o saldo do banco para o mês"""
        mes_ano = self.obter_mes_ano(mes, ano)
        return self.saldo_banco.get(mes_ano, 0.0)
    
    def calcular_total_despesas(self, mes: int, ano: int) -> float:
        """Calcula o total de despesas do mês"""
        mes_ano = self.obter_mes_ano(mes, ano)
        if mes_ano not in self.despesas:
            return 0.0
        return sum(despesa.valor for despesa in self.despesas[mes_ano])
    
    def calcular_total_despesas_pagas(self, mes: int, ano: int) -> float:
        """Calcula o total de despesas pagas do mês"""
        mes_ano = self.obter_mes_ano(mes, ano)
        if mes_ano not in self.despesas:
            return 0.0
        return sum(despesa.valor for despesa in self.despesas[mes_ano] if despesa.pago)
    
    def calcular_total_receitas(self, mes: int, ano: int) -> float:
        """Calcula o total de receitas do mês"""
        mes_ano = self.obter_mes_ano(mes, ano)
        if mes_ano not in self.receitas:
            return 0.0
        return sum(receita.valor for receita in self.receitas[mes_ano])
    
    def calcular_saldo_final(self, mes: int, ano: int) -> float:
        """Calcula o saldo final após todas as despesas"""
        saldo_inicial = self.obter_saldo_banco(mes, ano)
        total_receitas = self.calcular_total_receitas(mes, ano)
        total_despesas = self.calcular_total_despesas(mes, ano)
        return saldo_inicial + total_receitas - total_despesas
    
    def processar_pagamento_despesa(self, despesa: Despesa, data_pagamento: str = None) -> bool:
        """Processa o pagamento de uma despesa e atualiza o saldo automaticamente"""
        if despesa.pago:
            return False  # Despesa já foi paga
        
        # Verificar se há saldo suficiente
        if self.saldo_atual < despesa.valor:
            return False  # Saldo insuficiente
        
        # Marcar despesa como paga
        despesa.marcar_como_pago(data_pagamento)
        
        # Atualizar saldo
        saldo_anterior = self.saldo_atual
        self.saldo_atual -= despesa.valor
        
        # Registrar no histórico
        self.registrar_movimentacao(
            tipo="pagamento",
            descricao=f"Pagamento: {despesa.descricao}",
            valor=-despesa.valor,
            saldo_anterior=saldo_anterior,
            saldo_novo=self.saldo_atual,
            data=data_pagamento or datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        )
        
        self.salvar_dados()
        return True
    
    def processar_receita(self, receita: Receita) -> bool:
        """Processa uma receita e atualiza o saldo automaticamente"""
        # Atualizar saldo
        saldo_anterior = self.saldo_atual
        self.saldo_atual += receita.valor
        
        # Registrar no histórico
        self.registrar_movimentacao(
            tipo="receita",
            descricao=f"Receita: {receita.descricao}",
            valor=receita.valor,
            saldo_anterior=saldo_anterior,
            saldo_novo=self.saldo_atual,
            data=receita.data_recebimento.strftime("%d/%m/%Y")
        )
        
        self.salvar_dados()
        return True
    
    def registrar_movimentacao(self, tipo: str, descricao: str, valor: float, 
                              saldo_anterior: float, saldo_novo: float, data: str):
        """Registra uma movimentação no histórico"""
        movimentacao = {
            'tipo': tipo,
            'descricao': descricao,
            'valor': valor,
            'saldo_anterior': saldo_anterior,
            'saldo_novo': saldo_novo,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.historico_saldo.append(movimentacao)
    
    def obter_saldo_atual(self) -> float:
        """Obtém o saldo atual"""
        return self.saldo_atual
    
    def definir_saldo_inicial(self, saldo: float):
        """Define o saldo inicial do sistema"""
        saldo_anterior = self.saldo_atual
        self.saldo_atual = saldo
        
        self.registrar_movimentacao(
            tipo="ajuste",
            descricao="Definição de saldo inicial",
            valor=saldo - saldo_anterior,
            saldo_anterior=saldo_anterior,
            saldo_novo=saldo,
            data=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        )
        
        self.salvar_dados()
    
    def obter_despesas_mes(self, mes: int, ano: int) -> List[Despesa]:
        """Obtém todas as despesas do mês"""
        mes_ano = self.obter_mes_ano(mes, ano)
        return self.despesas.get(mes_ano, [])
    
    def obter_receitas_mes(self, mes: int, ano: int) -> List[Receita]:
        """Obtém todas as receitas do mês"""
        mes_ano = self.obter_mes_ano(mes, ano)
        return self.receitas.get(mes_ano, [])
    
    def editar_despesa(self, despesa: Despesa, nova_descricao: str = None, 
                      novo_valor: float = None, nova_data_vencimento: str = None, 
                      nova_categoria: str = None) -> bool:
        """Edita uma despesa existente"""
        try:
            if nova_descricao is not None:
                despesa.descricao = nova_descricao
            
            if novo_valor is not None and novo_valor > 0:
                # Se a despesa já foi paga, ajustar o saldo
                if despesa.pago:
                    diferenca = novo_valor - despesa.valor
                    self.saldo_atual -= diferenca
                    
                    self.registrar_movimentacao(
                        tipo="ajuste",
                        descricao=f"Ajuste por edição de despesa: {despesa.descricao}",
                        valor=-diferenca,
                        saldo_anterior=self.saldo_atual + diferenca,
                        saldo_novo=self.saldo_atual,
                        data=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    )
                
                despesa.valor = novo_valor
            
            if nova_data_vencimento is not None:
                despesa.data_vencimento = datetime.strptime(nova_data_vencimento, "%d/%m/%Y").date()
            
            if nova_categoria is not None:
                despesa.categoria = nova_categoria
            
            self.salvar_dados()
            return True
        except Exception:
            return False
    
    def editar_receita(self, receita: Receita, nova_descricao: str = None, 
                      novo_valor: float = None, nova_data_recebimento: str = None, 
                      nova_categoria: str = None) -> bool:
        """Edita uma receita existente"""
        try:
            if nova_descricao is not None:
                receita.descricao = nova_descricao
            
            if novo_valor is not None and novo_valor > 0:
                # Ajustar o saldo pela diferença
                diferenca = novo_valor - receita.valor
                self.saldo_atual += diferenca
                
                self.registrar_movimentacao(
                    tipo="ajuste",
                    descricao=f"Ajuste por edição de receita: {receita.descricao}",
                    valor=diferenca,
                    saldo_anterior=self.saldo_atual - diferenca,
                    saldo_novo=self.saldo_atual,
                    data=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                )
                
                receita.valor = novo_valor
            
            if nova_data_recebimento is not None:
                receita.data_recebimento = datetime.strptime(nova_data_recebimento, "%d/%m/%Y").date()
            
            if nova_categoria is not None:
                receita.categoria = nova_categoria
            
            self.salvar_dados()
            return True
        except Exception:
            return False
    
    def remover_despesa(self, despesa: Despesa, mes: int, ano: int) -> bool:
        """Remove uma despesa"""
        mes_ano = self.obter_mes_ano(mes, ano)
        if mes_ano in self.despesas and despesa in self.despesas[mes_ano]:
            # Se a despesa foi paga, devolver o valor ao saldo
            if despesa.pago:
                saldo_anterior = self.saldo_atual
                self.saldo_atual += despesa.valor
                
                self.registrar_movimentacao(
                    tipo="estorno",
                    descricao=f"Estorno por remoção de despesa: {despesa.descricao}",
                    valor=despesa.valor,
                    saldo_anterior=saldo_anterior,
                    saldo_novo=self.saldo_atual,
                    data=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                )
            
            self.despesas[mes_ano].remove(despesa)
            self.salvar_dados()
            return True
        return False
    
    def remover_receita(self, receita: Receita, mes: int, ano: int) -> bool:
        """Remove uma receita"""
        mes_ano = self.obter_mes_ano(mes, ano)
        if mes_ano in self.receitas and receita in self.receitas[mes_ano]:
            # Remover o valor da receita do saldo
            saldo_anterior = self.saldo_atual
            self.saldo_atual -= receita.valor
            
            self.registrar_movimentacao(
                tipo="estorno",
                descricao=f"Estorno por remoção de receita: {receita.descricao}",
                valor=-receita.valor,
                saldo_anterior=saldo_anterior,
                saldo_novo=self.saldo_atual,
                data=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            )
            
            self.receitas[mes_ano].remove(receita)
            self.salvar_dados()
            return True
        return False
    
    def buscar_despesas(self, termo: str = "", categoria: str = "", 
                       apenas_pagas: bool = None) -> List[tuple]:
        """Busca despesas com filtros"""
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
                
                # Filtro por status de pagamento
                if apenas_pagas is not None and despesa.pago != apenas_pagas:
                    continue
                
                resultados.append((despesa, mes, ano))
        
        return resultados
    
    def buscar_receitas(self, termo: str = "", categoria: str = "") -> List[tuple]:
        """Busca receitas com filtros"""
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
                
                resultados.append((receita, mes, ano))
        
        return resultados
    
    def obter_historico_saldo(self) -> List[Dict]:
        """Obtém o histórico completo de movimentações do saldo"""
        return self.historico_saldo.copy()
    
    def salvar_dados(self):
        """Salva os dados em arquivo JSON"""
        dados = {
            'despesas': {},
            'receitas': {},
            'saldo_banco': self.saldo_banco,
            'saldo_atual': self.saldo_atual,
            'historico_saldo': self.historico_saldo
        }
        
        # Converter despesas para dicionário
        for mes_ano, lista_despesas in self.despesas.items():
            dados['despesas'][mes_ano] = [despesa.to_dict() for despesa in lista_despesas]
        
        # Converter receitas para dicionário
        for mes_ano, lista_receitas in self.receitas.items():
            dados['receitas'][mes_ano] = [receita.to_dict() for receita in lista_receitas]
        
        with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    
    def carregar_dados(self):
        """Carrega os dados do arquivo JSON"""
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
            
            # Carregar saldo do banco
            self.saldo_banco = dados.get('saldo_banco', {})
            
            # Carregar saldo atual e histórico
            self.saldo_atual = dados.get('saldo_atual', 0.0)
            self.historico_saldo = dados.get('historico_saldo', [])
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Erro ao carregar dados: {e}")
            print("Iniciando com dados vazios.")

if __name__ == "__main__":
    # Exemplo de uso básico
    controle = ControleFinanceiro()
    print("Sistema de Controle de Gastos iniciado!")
    print("Execute o arquivo 'main.py' para usar a interface completa.")