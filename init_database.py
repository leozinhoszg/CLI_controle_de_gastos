"""
Script de inicialização do banco de dados MySQL
Cria o schema e executa as migrações
"""
import mysql.connector
from mysql.connector import Error
from src.db.db_config import DB_CONFIG
import os

def criar_schema():
    """Cria o schema se não existir"""
    try:
        # Conectar sem especificar database
        config_sem_db = DB_CONFIG.copy()
        database_name = config_sem_db.pop('database')
        
        print(f"🔄 Conectando ao MySQL em {config_sem_db['host']}...")
        connection = mysql.connector.connect(**config_sem_db)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Criar schema
            print(f"🔄 Criando schema '{database_name}'...")
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS `{database_name}` "
                          f"DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Schema '{database_name}' criado/verificado!")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ Erro ao criar schema: {e}")
        return False

def executar_migrations():
    """Executa o arquivo de migrações SQL"""
    try:
        print("🔄 Conectando ao banco de dados...")
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Ler arquivo de migrações
            if not os.path.exists('migrations.sql'):
                print("❌ Arquivo migrations.sql não encontrado!")
                return False
            
            print("📖 Lendo arquivo migrations.sql...")
            with open('migrations.sql', 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            # Dividir em comandos individuais
            # Precisa de tratamento especial para DELIMITER
            print("🔄 Executando migrações...")
            
            current_delimiter = ';'
            commands = []
            current_command = []
            
            for line in sql_content.split('\n'):
                line = line.strip()
                
                # Ignorar comentários
                if line.startswith('--') or not line:
                    continue
                
                # Verificar mudança de delimitador
                if line.upper().startswith('DELIMITER'):
                    new_delimiter = line.split()[1]
                    if new_delimiter != ';':
                        current_delimiter = new_delimiter
                    else:
                        current_delimiter = ';'
                    continue
                
                current_command.append(line)
                
                # Verificar fim do comando
                if line.endswith(current_delimiter):
                    full_command = ' '.join(current_command)
                    if current_delimiter != ';':
                        full_command = full_command[:-len(current_delimiter)].strip()
                    else:
                        full_command = full_command[:-1].strip()
                    
                    if full_command:
                        commands.append(full_command)
                    current_command = []
            
            # Executar comandos
            total_executados = 0
            for command in commands:
                if command.strip():
                    try:
                        cursor.execute(command)
                        total_executados += 1
                    except Error as e:
                        # Ignorar erros de "já existe" que são esperados
                        if 'already exists' not in str(e).lower():
                            print(f"⚠️  Aviso ao executar comando: {e}")
            
            connection.commit()
            print(f"✅ {total_executados} comandos SQL executados com sucesso!")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ Erro ao executar migrações: {e}")
        return False

def verificar_tabelas():
    """Verifica se as tabelas foram criadas"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("\n📊 Verificando tabelas criadas...")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print(f"\n✅ {len(tables)} tabelas encontradas:")
            for table in tables:
                print(f"   • {table[0]}")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        return False

def inserir_dados_iniciais():
    """Insere dados iniciais necessários"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("\n🔄 Inserindo dados iniciais...")
            
            # Verificar se já existem contas
            cursor.execute("SELECT COUNT(*) FROM contas_bancarias")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Inserir conta Carteira
                cursor.execute("""
                    INSERT INTO contas_bancarias (nome, banco, saldo_atual)
                    VALUES ('Carteira', 'Dinheiro em Espécie', 0.00)
                """)
                print("   ✅ Conta 'Carteira' criada")
                
                # Inserir conta principal
                cursor.execute("""
                    INSERT INTO contas_bancarias (nome, banco, saldo_atual)
                    VALUES ('Conta Principal', 'Banco Principal', 0.00)
                """)
                print("   ✅ Conta 'Conta Principal' criada")
                
                # Configurar conta padrão
                cursor.execute("""
                    INSERT INTO configuracoes (chave, valor, descricao)
                    VALUES ('conta_padrao', 'Carteira', 'Conta bancária padrão do sistema')
                    ON DUPLICATE KEY UPDATE valor = 'Carteira'
                """)
                print("   ✅ Configuração 'conta_padrao' definida")
                
                connection.commit()
                print("✅ Dados iniciais inseridos com sucesso!")
            else:
                print("ℹ️  Dados iniciais já existem no banco")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ Erro ao inserir dados iniciais: {e}")
        return False

def main():
    """Função principal de inicialização"""
    print("="*60)
    print("  INICIALIZAÇÃO DO BANCO DE DADOS - SISTEMA DE GASTOS")
    print("="*60)
    print()
    
    # Passo 1: Criar schema
    print("📋 PASSO 1: Criando Schema")
    print("-"*60)
    if not criar_schema():
        print("\n❌ Falha ao criar schema. Abortando...")
        return False
    
    print()
    
    # Passo 2: Executar migrações
    print("📋 PASSO 2: Executando Migrações")
    print("-"*60)
    if not executar_migrations():
        print("\n❌ Falha ao executar migrações. Abortando...")
        return False
    
    print()
    
    # Passo 3: Verificar tabelas
    print("📋 PASSO 3: Verificando Estrutura")
    print("-"*60)
    if not verificar_tabelas():
        print("\n⚠️  Não foi possível verificar as tabelas")
    
    print()
    
    # Passo 4: Inserir dados iniciais
    print("📋 PASSO 4: Inserindo Dados Iniciais")
    print("-"*60)
    if not inserir_dados_iniciais():
        print("\n⚠️  Não foi possível inserir dados iniciais")
    
    print()
    print("="*60)
    print("  🎉 INICIALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print()
    print("💡 Dicas:")
    print("   • O banco de dados está pronto para uso")
    print("   • Execute 'python main_avancado.py' para iniciar o sistema")
    print("   • Suas credenciais MySQL estão em db_config.py")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Inicialização falhou. Verifique as configurações e tente novamente.")
            print("💡 Certifique-se de que:")
            print("   1. O MySQL está rodando")
            print("   2. As credenciais em db_config.py estão corretas")
            print("   3. O usuário tem permissões para criar schemas")
            exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Inicialização cancelada pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        exit(1)

