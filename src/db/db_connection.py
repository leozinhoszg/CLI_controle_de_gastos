"""
Classe de conexão e operações com o banco de dados MySQL
"""
import mysql.connector
from mysql.connector import Error, pooling
from typing import List, Dict, Optional, Tuple, Any
from contextlib import contextmanager
from src.db.db_config import DB_CONFIG
import json

class DatabaseConnection:
    """Gerenciador de conexão com MySQL usando connection pooling"""
    
    _pool = None
    
    @classmethod
    def initialize_pool(cls):
        """Inicializa o pool de conexões"""
        if cls._pool is None:
            try:
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="cli_gastos_pool",
                    pool_size=5,
                    pool_reset_session=True,
                    **DB_CONFIG
                )
                print("✅ Pool de conexões MySQL inicializado com sucesso!")
            except Error as e:
                print(f"❌ Erro ao inicializar pool de conexões: {e}")
                raise
    
    @classmethod
    @contextmanager
    def get_connection(cls):
        """Context manager para obter conexão do pool"""
        if cls._pool is None:
            cls.initialize_pool()
        
        connection = None
        try:
            connection = cls._pool.get_connection()
            yield connection
        except Error as e:
            print(f"❌ Erro na conexão: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @classmethod
    def execute_query(cls, query: str, params: Tuple = None, fetch: bool = False) -> Optional[List]:
        """Executa uma query SQL"""
        with cls.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                
                if fetch:
                    result = cursor.fetchall()
                    return result
                else:
                    conn.commit()
                    return cursor.lastrowid
            except Error as e:
                print(f"❌ Erro ao executar query: {e}")
                print(f"Query: {query}")
                print(f"Params: {params}")
                conn.rollback()
                raise
            finally:
                cursor.close()
    
    @classmethod
    def execute_many(cls, query: str, data: List[Tuple]) -> bool:
        """Executa múltiplas queries de uma vez"""
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany(query, data)
                conn.commit()
                return True
            except Error as e:
                print(f"❌ Erro ao executar queries múltiplas: {e}")
                conn.rollback()
                return False
            finally:
                cursor.close()
    
    @classmethod
    def test_connection(cls) -> bool:
        """Testa a conexão com o banco de dados"""
        try:
            with cls.get_connection() as conn:
                if conn.is_connected():
                    cursor = conn.cursor()
                    cursor.execute("SELECT DATABASE()")
                    db_name = cursor.fetchone()
                    cursor.close()
                    print(f"✅ Conectado ao banco de dados: {db_name[0]}")
                    return True
        except Error as e:
            print(f"❌ Falha ao conectar ao banco de dados: {e}")
            return False
        return False


class DatabaseManager:
    """Classe para gerenciar operações do banco de dados"""
    
    def __init__(self):
        self.db = DatabaseConnection
        self.db.initialize_pool()
    
    # ==================== CONTAS BANCÁRIAS ====================
    
    def criar_conta_bancaria(self, nome: str, banco: str, saldo_inicial: float = 0.0) -> Optional[int]:
        """Cria uma nova conta bancária"""
        query = """
            INSERT INTO contas_bancarias (nome, banco, saldo_atual)
            VALUES (%s, %s, %s)
        """
        try:
            conta_id = self.db.execute_query(query, (nome, banco, saldo_inicial))
            
            # Registrar saldo inicial no histórico
            if conta_id and saldo_inicial != 0:
                self.adicionar_historico_saldo(
                    conta_id, 0.0, saldo_inicial, saldo_inicial, "Saldo inicial"
                )
            
            return conta_id
        except Error:
            return None
    
    def obter_conta_por_nome(self, nome: str) -> Optional[Dict]:
        """Obtém informações de uma conta pelo nome"""
        query = "SELECT * FROM contas_bancarias WHERE nome = %s"
        result = self.db.execute_query(query, (nome,), fetch=True)
        return result[0] if result else None
    
    def obter_conta_por_id(self, conta_id: int) -> Optional[Dict]:
        """Obtém informações de uma conta pelo ID"""
        query = "SELECT * FROM contas_bancarias WHERE id = %s"
        result = self.db.execute_query(query, (conta_id,), fetch=True)
        return result[0] if result else None
    
    def listar_contas_bancarias(self) -> List[Dict]:
        """Lista todas as contas bancárias"""
        query = "SELECT * FROM contas_bancarias ORDER BY nome"
        return self.db.execute_query(query, fetch=True) or []
    
    def atualizar_saldo_conta(self, conta_id: int, novo_saldo: float, operacao: str, valor: float = 0.0) -> bool:
        """Atualiza o saldo de uma conta"""
        # Obter saldo anterior
        conta = self.obter_conta_por_id(conta_id)
        if not conta:
            return False
        
        saldo_anterior = float(conta['saldo_atual'])
        
        # Atualizar saldo
        query = "UPDATE contas_bancarias SET saldo_atual = %s WHERE id = %s"
        self.db.execute_query(query, (novo_saldo, conta_id))
        
        # Adicionar ao histórico
        self.adicionar_historico_saldo(conta_id, saldo_anterior, novo_saldo, valor, operacao)
        
        return True
    
    def editar_conta_bancaria(self, conta_id: int, novo_nome: Optional[str] = None, 
                             novo_banco: Optional[str] = None) -> bool:
        """Edita informações de uma conta bancária"""
        updates = []
        params = []
        
        if novo_nome:
            updates.append("nome = %s")
            params.append(novo_nome)
        
        if novo_banco:
            updates.append("banco = %s")
            params.append(novo_banco)
        
        if not updates:
            return False
        
        params.append(conta_id)
        query = f"UPDATE contas_bancarias SET {', '.join(updates)} WHERE id = %s"
        
        try:
            self.db.execute_query(query, tuple(params))
            return True
        except Error:
            return False
    
    def remover_conta_bancaria(self, conta_id: int) -> bool:
        """Remove uma conta bancária"""
        query = "DELETE FROM contas_bancarias WHERE id = %s"
        try:
            self.db.execute_query(query, (conta_id,))
            return True
        except Error:
            return False
    
    # ==================== HISTÓRICO DE SALDO ====================
    
    def adicionar_historico_saldo(self, conta_id: int, saldo_anterior: float, 
                                  saldo_novo: float, valor: float, operacao: str) -> Optional[int]:
        """Adiciona um registro ao histórico de saldo"""
        query = """
            INSERT INTO historico_saldo 
            (conta_id, saldo_anterior, saldo_novo, valor_movimentacao, operacao)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.db.execute_query(query, (conta_id, saldo_anterior, saldo_novo, valor, operacao))
    
    def obter_historico_conta(self, conta_id: int, limite: int = 10) -> List[Dict]:
        """Obtém o histórico de uma conta"""
        query = """
            SELECT * FROM historico_saldo 
            WHERE conta_id = %s 
            ORDER BY data_movimentacao DESC 
            LIMIT %s
        """
        return self.db.execute_query(query, (conta_id, limite), fetch=True) or []
    
    # ==================== DESPESAS ====================
    
    def adicionar_despesa(self, descricao: str, valor: float, categoria: str, 
                         data_vencimento: str, mes: int, ano: int, 
                         conta_id: Optional[int] = None) -> Optional[int]:
        """Adiciona uma nova despesa"""
        query = """
            INSERT INTO despesas 
            (descricao, valor, categoria, data_vencimento, mes, ano, conta_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.db.execute_query(
            query, (descricao, valor, categoria, data_vencimento, mes, ano, conta_id)
        )
    
    def obter_despesas_mes(self, mes: int, ano: int) -> List[Dict]:
        """Obtém todas as despesas de um mês"""
        query = "SELECT * FROM despesas WHERE mes = %s AND ano = %s ORDER BY data_vencimento"
        return self.db.execute_query(query, (mes, ano), fetch=True) or []
    
    def marcar_despesa_paga(self, despesa_id: int, data_pagamento: Optional[str] = None) -> bool:
        """Marca uma despesa como paga"""
        if data_pagamento is None:
            from datetime import datetime
            data_pagamento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        query = "UPDATE despesas SET pago = TRUE, data_pagamento = %s WHERE id = %s"
        try:
            self.db.execute_query(query, (data_pagamento, despesa_id))
            return True
        except Error:
            return False
    
    def marcar_despesa_nao_paga(self, despesa_id: int) -> bool:
        """Marca uma despesa como não paga"""
        query = "UPDATE despesas SET pago = FALSE, data_pagamento = NULL WHERE id = %s"
        try:
            self.db.execute_query(query, (despesa_id,))
            return True
        except Error:
            return False
    
    def editar_despesa(self, despesa_id: int, descricao: Optional[str] = None,
                       valor: Optional[float] = None, categoria: Optional[str] = None,
                       data_vencimento: Optional[str] = None) -> bool:
        """Edita uma despesa existente"""
        updates = []
        params = []
        
        if descricao is not None:
            updates.append("descricao = %s")
            params.append(descricao)
        
        if valor is not None:
            updates.append("valor = %s")
            params.append(valor)
        
        if categoria is not None:
            updates.append("categoria = %s")
            params.append(categoria)
        
        if data_vencimento is not None:
            updates.append("data_vencimento = %s")
            params.append(data_vencimento)
        
        if not updates:
            return False
        
        params.append(despesa_id)
        query = f"UPDATE despesas SET {', '.join(updates)} WHERE id = %s"
        
        try:
            self.db.execute_query(query, tuple(params))
            return True
        except Error:
            return False
    
    def remover_despesa(self, despesa_id: int) -> bool:
        """Remove uma despesa"""
        query = "DELETE FROM despesas WHERE id = %s"
        try:
            # Executar DELETE com verificação detalhada
            with self.db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                try:
                    # Desabilitar autocommit para controle manual da transação
                    conn.autocommit = False
                    
                    # Primeiro, verificar se a despesa existe
                    check_query = "SELECT id, descricao FROM despesas WHERE id = %s"
                    cursor.execute(check_query, (despesa_id,))
                    existe = cursor.fetchone()
                    
                    if not existe:
                        conn.rollback()
                        return False
                    
                    # Executar DELETE
                    cursor.execute(query, (despesa_id,))
                    rows_affected = cursor.rowcount
                    
                    if rows_affected == 0:
                        conn.rollback()
                        return False
                    
                    # Commit da transação
                    conn.commit()
                    
                    # Verificar se realmente removeu
                    cursor.execute(check_query, (despesa_id,))
                    ainda_existe = cursor.fetchone()
                    
                    if ainda_existe:
                        return False
                    else:
                        return True
                        
                except Exception as e:
                    conn.rollback()
                    return False
                finally:
                    # Reabilitar autocommit
                    conn.autocommit = True
                    cursor.close()
                    
        except Exception as e:
            return False
    
    def buscar_despesas(self, filtros: Dict[str, Any]) -> List[Dict]:
        """Busca despesas com filtros"""
        query = "SELECT * FROM despesas WHERE 1=1"
        params = []
        
        if 'termo' in filtros and filtros['termo']:
            query += " AND descricao LIKE %s"
            params.append(f"%{filtros['termo']}%")
        
        if 'categoria' in filtros and filtros['categoria']:
            query += " AND categoria = %s"
            params.append(filtros['categoria'])
        
        if 'valor_min' in filtros and filtros['valor_min'] > 0:
            query += " AND valor >= %s"
            params.append(filtros['valor_min'])
        
        if 'valor_max' in filtros and filtros['valor_max'] != float('inf'):
            query += " AND valor <= %s"
            params.append(filtros['valor_max'])
        
        if 'pago' in filtros and filtros['pago'] is not None:
            query += " AND pago = %s"
            params.append(filtros['pago'])
        
        if 'data_inicio' in filtros and filtros['data_inicio']:
            query += " AND data_vencimento >= %s"
            # Converter de DD/MM/YYYY para YYYY-MM-DD
            data_inicio = filtros['data_inicio']
            if '/' in data_inicio:
                partes = data_inicio.split('/')
                data_inicio = f"{partes[2]}-{partes[1]}-{partes[0]}"
            params.append(data_inicio)
        
        if 'data_fim' in filtros and filtros['data_fim']:
            query += " AND data_vencimento <= %s"
            # Converter de DD/MM/YYYY para YYYY-MM-DD
            data_fim = filtros['data_fim']
            if '/' in data_fim:
                partes = data_fim.split('/')
                data_fim = f"{partes[2]}-{partes[1]}-{partes[0]}"
            params.append(data_fim)
        
        query += " ORDER BY data_vencimento DESC"
        
        return self.db.execute_query(query, tuple(params), fetch=True) or []
    
    # ==================== RECEITAS ====================
    
    def buscar_receitas(self, filtros: Dict[str, Any]) -> List[Dict]:
        """Busca receitas com filtros"""
        query = "SELECT * FROM receitas WHERE 1=1"
        params = []
        
        if 'termo' in filtros and filtros['termo']:
            query += " AND descricao LIKE %s"
            params.append(f"%{filtros['termo']}%")
        
        if 'categoria' in filtros and filtros['categoria']:
            query += " AND categoria = %s"
            params.append(filtros['categoria'])
        
        if 'valor_min' in filtros and filtros['valor_min'] > 0:
            query += " AND valor >= %s"
            params.append(filtros['valor_min'])
        
        if 'valor_max' in filtros and filtros['valor_max'] != float('inf'):
            query += " AND valor <= %s"
            params.append(filtros['valor_max'])
        
        if 'data_inicio' in filtros and filtros['data_inicio']:
            query += " AND data_recebimento >= %s"
            # Converter de DD/MM/YYYY para YYYY-MM-DD
            data_inicio = filtros['data_inicio']
            if '/' in data_inicio:
                partes = data_inicio.split('/')
                data_inicio = f"{partes[2]}-{partes[1]}-{partes[0]}"
            params.append(data_inicio)
        
        if 'data_fim' in filtros and filtros['data_fim']:
            query += " AND data_recebimento <= %s"
            # Converter de DD/MM/YYYY para YYYY-MM-DD
            data_fim = filtros['data_fim']
            if '/' in data_fim:
                partes = data_fim.split('/')
                data_fim = f"{partes[2]}-{partes[1]}-{partes[0]}"
            params.append(data_fim)
        
        query += " ORDER BY data_recebimento DESC"
        
        return self.db.execute_query(query, tuple(params), fetch=True) or []
    
    def adicionar_receita(self, descricao: str, valor: float, categoria: str, 
                         data_recebimento: str, mes: int, ano: int,
                         conta_id: Optional[int] = None) -> Optional[int]:
        """Adiciona uma nova receita"""
        query = """
            INSERT INTO receitas 
            (descricao, valor, categoria, data_recebimento, mes, ano, conta_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.db.execute_query(
            query, (descricao, valor, categoria, data_recebimento, mes, ano, conta_id)
        )
    
    def obter_receitas_mes(self, mes: int, ano: int) -> List[Dict]:
        """Obtém todas as receitas de um mês"""
        query = "SELECT * FROM receitas WHERE mes = %s AND ano = %s ORDER BY data_recebimento"
        return self.db.execute_query(query, (mes, ano), fetch=True) or []
    
    def editar_receita(self, receita_id: int, descricao: Optional[str] = None,
                       valor: Optional[float] = None, categoria: Optional[str] = None,
                       data_recebimento: Optional[str] = None) -> bool:
        """Edita uma receita existente"""
        updates = []
        params = []
        
        if descricao is not None:
            updates.append("descricao = %s")
            params.append(descricao)
        
        if valor is not None:
            updates.append("valor = %s")
            params.append(valor)
        
        if categoria is not None:
            updates.append("categoria = %s")
            params.append(categoria)
        
        if data_recebimento is not None:
            updates.append("data_recebimento = %s")
            params.append(data_recebimento)
        
        if not updates:
            return False
        
        params.append(receita_id)
        query = f"UPDATE receitas SET {', '.join(updates)} WHERE id = %s"
        
        try:
            self.db.execute_query(query, tuple(params))
            return True
        except Error:
            return False
    
    def remover_receita(self, receita_id: int) -> bool:
        """Remove uma receita"""
        query = "DELETE FROM receitas WHERE id = %s"
        try:
            # Executar DELETE com verificação detalhada
            with self.db.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                try:
                    # Desabilitar autocommit para controle manual da transação
                    conn.autocommit = False
                    
                    # Primeiro, verificar se a receita existe
                    check_query = "SELECT id, descricao FROM receitas WHERE id = %s"
                    cursor.execute(check_query, (receita_id,))
                    existe = cursor.fetchone()
                    
                    if not existe:
                        conn.rollback()
                        return False
                    
                    # Executar DELETE
                    cursor.execute(query, (receita_id,))
                    rows_affected = cursor.rowcount
                    
                    if rows_affected == 0:
                        conn.rollback()
                        return False
                    
                    # Commit da transação
                    conn.commit()
                    
                    # Verificar se realmente removeu
                    cursor.execute(check_query, (receita_id,))
                    ainda_existe = cursor.fetchone()
                    
                    if ainda_existe:
                        return False
                    else:
                        return True
                        
                except Exception as e:
                    conn.rollback()
                    return False
                finally:
                    # Reabilitar autocommit
                    conn.autocommit = True
                    cursor.close()
                    
        except Exception as e:
            return False
    
    # ==================== METAS DE GASTOS ====================
    
    def criar_meta_gasto(self, categoria: str, limite_mensal: float, mes: int, ano: int) -> Optional[int]:
        """Cria uma nova meta de gasto"""
        query = """
            INSERT INTO metas_gastos (categoria, limite_mensal, mes, ano)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE limite_mensal = %s
        """
        return self.db.execute_query(query, (categoria, limite_mensal, mes, ano, limite_mensal))
    
    def obter_metas_mes(self, mes: int, ano: int) -> List[Dict]:
        """Obtém todas as metas de um mês"""
        query = "SELECT * FROM metas_gastos WHERE mes = %s AND ano = %s"
        return self.db.execute_query(query, (mes, ano), fetch=True) or []
    
    def atualizar_gastos_metas(self, mes: int, ano: int) -> bool:
        """Atualiza os gastos atuais das metas (chama stored procedure)"""
        query = "CALL sp_atualizar_gastos_metas(%s, %s)"
        try:
            self.db.execute_query(query, (mes, ano))
            return True
        except Error:
            return False
    
    def editar_meta_gasto(self, meta_id: int, limite_mensal: Optional[float] = None) -> bool:
        """Edita uma meta de gasto"""
        if limite_mensal is None:
            return False
        
        query = "UPDATE metas_gastos SET limite_mensal = %s WHERE id = %s"
        try:
            self.db.execute_query(query, (limite_mensal, meta_id))
            return True
        except Error:
            return False
    
    def remover_meta_gasto(self, meta_id: int) -> bool:
        """Remove uma meta de gasto"""
        query = "DELETE FROM metas_gastos WHERE id = %s"
        try:
            self.db.execute_query(query, (meta_id,))
            return True
        except Error:
            return False
    
    # ==================== CONFIGURAÇÕES ====================
    
    def obter_configuracao(self, chave: str) -> Optional[str]:
        """Obtém uma configuração"""
        query = "SELECT valor FROM configuracoes WHERE chave = %s"
        result = self.db.execute_query(query, (chave,), fetch=True)
        return result[0]['valor'] if result else None
    
    def salvar_configuracao(self, chave: str, valor: str, descricao: Optional[str] = None) -> bool:
        """Salva uma configuração"""
        query = """
            INSERT INTO configuracoes (chave, valor, descricao)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE valor = %s, descricao = COALESCE(%s, descricao)
        """
        try:
            self.db.execute_query(query, (chave, valor, descricao, valor, descricao))
            return True
        except Error:
            return False


# Instância global do gerenciador
db_manager = DatabaseManager()

if __name__ == "__main__":
    # Teste de conexão
    print("🔍 Testando conexão com o banco de dados...")
    if DatabaseConnection.test_connection():
        print("✅ Conexão com MySQL funcionando!")
    else:
        print("❌ Falha na conexão com MySQL!")
        print("💡 Verifique as configurações em db_config.py ou arquivo .env")

