#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de migração de dados JSON para MySQL
Converte dados do sistema antigo (JSON) para o novo formato (MySQL)
"""
import json
import os
from datetime import datetime
from src.db.db_connection import DatabaseManager

def migrar_json_para_mysql():
    """Migra dados do JSON para o MySQL"""
    
    arquivo_json = 'dados_financeiros_avancado.json'
    
    if not os.path.exists(arquivo_json):
        print("❌ Arquivo JSON não encontrado!")
        print(f"   Procurando: {arquivo_json}")
        return False
    
    print("="*70)
    print("  MIGRAÇÃO DE DADOS JSON → MySQL")
    print("="*70)
    print()
    
    print("📖 Lendo dados do JSON...")
    try:
        with open(arquivo_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        print(f"✅ Arquivo JSON lido com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao ler JSON: {e}")
        return False
    
    print()
    
    try:
        db = DatabaseManager()
        print("✅ Conexão com MySQL estabelecida!")
    except Exception as e:
        print(f"❌ Erro ao conectar ao MySQL: {e}")
        print("💡 Execute 'python init_database.py' primeiro!")
        return False
    
    print()
    
    # Migrar contas bancárias
    print("🏦 Migrando Contas Bancárias")
    print("-"*70)
    contas_map = {}  # mapa de nome -> id
    for nome_conta, dados_conta in dados.get('contas_bancarias', {}).items():
        try:
            # Verificar se já existe
            conta_existe = db.obter_conta_por_nome(nome_conta)
            if conta_existe:
                contas_map[nome_conta] = conta_existe['id']
                print(f"   ⚠️  Conta '{nome_conta}' já existe - pulando")
            else:
                conta_id = db.criar_conta_bancaria(
                    nome=nome_conta,
                    banco=dados_conta['banco'],
                    saldo_inicial=dados_conta['saldo_atual']
                )
                contas_map[nome_conta] = conta_id
                print(f"   ✅ Conta '{nome_conta}' criada (Saldo: R$ {dados_conta['saldo_atual']:.2f})")
        except Exception as e:
            print(f"   ❌ Erro ao migrar conta '{nome_conta}': {e}")
    
    print()
    
    # Migrar despesas
    print("💸 Migrando Despesas")
    print("-"*70)
    total_despesas = 0
    erros_despesas = 0
    for mes_ano, lista_despesas in dados.get('despesas', {}).items():
        try:
            mes, ano = mes_ano.split('/')
            mes, ano = int(mes), int(ano)
            
            for desp_dict in lista_despesas:
                try:
                    # Converter data de vencimento
                    data_venc = desp_dict['data_vencimento']
                    if '/' in data_venc:
                        # Formato DD/MM/AAAA
                        partes = data_venc.split('/')
                        data_venc = f"{partes[2]}-{partes[1]}-{partes[0]}"
                    
                    db.adicionar_despesa(
                        descricao=desp_dict['descricao'],
                        valor=desp_dict['valor'],
                        categoria=desp_dict['categoria'],
                        data_vencimento=data_venc,
                        mes=mes,
                        ano=ano
                    )
                    total_despesas += 1
                    
                    if total_despesas % 10 == 0:
                        print(f"   📊 {total_despesas} despesas migradas...")
                        
                except Exception as e:
                    erros_despesas += 1
                    if erros_despesas <= 5:  # Mostrar apenas primeiros 5 erros
                        print(f"   ⚠️  Erro ao migrar despesa '{desp_dict.get('descricao', 'N/A')}': {e}")
        except Exception as e:
            print(f"   ❌ Erro ao processar mês {mes_ano}: {e}")
    
    print(f"   ✅ Total: {total_despesas} despesas migradas")
    if erros_despesas > 0:
        print(f"   ⚠️  {erros_despesas} erros encontrados")
    
    print()
    
    # Migrar receitas
    print("💰 Migrando Receitas")
    print("-"*70)
    total_receitas = 0
    erros_receitas = 0
    for mes_ano, lista_receitas in dados.get('receitas', {}).items():
        try:
            mes, ano = mes_ano.split('/')
            mes, ano = int(mes), int(ano)
            
            for rec_dict in lista_receitas:
                try:
                    # Converter data de recebimento
                    data_rec = rec_dict['data_recebimento']
                    if '/' in data_rec:
                        # Formato DD/MM/AAAA
                        partes = data_rec.split('/')
                        data_rec = f"{partes[2]}-{partes[1]}-{partes[0]}"
                    
                    db.adicionar_receita(
                        descricao=rec_dict['descricao'],
                        valor=rec_dict['valor'],
                        categoria=rec_dict['categoria'],
                        data_recebimento=data_rec,
                        mes=mes,
                        ano=ano
                    )
                    total_receitas += 1
                    
                    if total_receitas % 10 == 0:
                        print(f"   📊 {total_receitas} receitas migradas...")
                        
                except Exception as e:
                    erros_receitas += 1
                    if erros_receitas <= 5:
                        print(f"   ⚠️  Erro ao migrar receita '{rec_dict.get('descricao', 'N/A')}': {e}")
        except Exception as e:
            print(f"   ❌ Erro ao processar mês {mes_ano}: {e}")
    
    print(f"   ✅ Total: {total_receitas} receitas migradas")
    if erros_receitas > 0:
        print(f"   ⚠️  {erros_receitas} erros encontrados")
    
    print()
    
    # Migrar metas
    print("🎯 Migrando Metas de Gastos")
    print("-"*70)
    total_metas = 0
    erros_metas = 0
    for mes_ano, lista_metas in dados.get('metas_gastos', {}).items():
        try:
            mes, ano = mes_ano.split('/')
            mes, ano = int(mes), int(ano)
            
            for meta_dict in lista_metas:
                try:
                    db.criar_meta_gasto(
                        categoria=meta_dict['categoria'],
                        limite_mensal=meta_dict['limite_mensal'],
                        mes=mes,
                        ano=ano
                    )
                    total_metas += 1
                except Exception as e:
                    erros_metas += 1
                    if erros_metas <= 5:
                        print(f"   ⚠️  Erro ao migrar meta '{meta_dict.get('categoria', 'N/A')}': {e}")
        except Exception as e:
            print(f"   ❌ Erro ao processar mês {mes_ano}: {e}")
    
    print(f"   ✅ Total: {total_metas} metas migradas")
    if erros_metas > 0:
        print(f"   ⚠️  {erros_metas} erros encontrados")
    
    print()
    
    # Salvar conta padrão
    print("⚙️  Configurando Sistema")
    print("-"*70)
    conta_padrao = dados.get('conta_padrao', 'Carteira')
    db.salvar_configuracao('conta_padrao', conta_padrao)
    print(f"   ✅ Conta padrão configurada: {conta_padrao}")
    
    print()
    print("="*70)
    print("  ✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*70)
    print()
    print(f"📊 Resumo da Migração:")
    print(f"   🏦 Contas bancárias: {len(contas_map)}")
    print(f"   💸 Despesas: {total_despesas}")
    print(f"   💰 Receitas: {total_receitas}")
    print(f"   🎯 Metas: {total_metas}")
    print()
    
    # Fazer backup do JSON original
    print("💾 Criando Backup do JSON Original")
    print("-"*70)
    backup_json = f'backup_json_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    try:
        os.rename(arquivo_json, backup_json)
        print(f"   ✅ JSON original renomeado para: {backup_json}")
        print(f"   💡 Mantenha este arquivo como backup de segurança!")
    except Exception as e:
        print(f"   ⚠️  Não foi possível renomear o arquivo: {e}")
        print(f"   💡 Recomendamos fazer backup manual de: {arquivo_json}")
    
    print()
    print("🎉 Migração finalizada! Seu sistema agora usa MySQL.")
    print("   Execute 'python main_avancado.py' para iniciar o sistema.")
    print()
    
    return True

if __name__ == "__main__":
    try:
        print()
        sucesso = migrar_json_para_mysql()
        
        if not sucesso:
            print("\n❌ Migração falhou!")
            print("💡 Verifique os erros acima e tente novamente.")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Migração cancelada pelo usuário!")
        exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado durante a migração: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

