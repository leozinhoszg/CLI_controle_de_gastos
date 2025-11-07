from datetime import datetime, date
import os
from typing import List, Dict
from controle_avancado import ControleFinanceiroAvancado

try:
    import pandas as pd
    PANDAS_DISPONIVEL = True
except ImportError:
    PANDAS_DISPONIVEL = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_DISPONIVEL = True
except ImportError:
    REPORTLAB_DISPONIVEL = False

class ExportadorRelatorios:
    """Classe para exportar relatórios em diferentes formatos"""
    
    def __init__(self, controle: ControleFinanceiroAvancado):
        self.controle = controle
    
    def obter_mes_nome(self, mes: int) -> str:
        """Retorna o nome do mês"""
        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        return meses.get(mes, "Mês Inválido")
    
    def exportar_relatorio_mensal_excel(self, mes: int, ano: int, nome_arquivo: str = None) -> bool:
        """Exporta relatório mensal para Excel"""
        if not PANDAS_DISPONIVEL:
            print("❌ Pandas não está instalado. Execute: pip install pandas openpyxl")
            return False
        
        try:
            if nome_arquivo is None:
                nome_arquivo = f"relatorio_mensal_{mes:02d}_{ano}.xlsx"
            
            # Criar dados das despesas
            despesas = self.controle.obter_despesas_mes(mes, ano)
            dados_despesas = []
            
            for despesa in despesas:
                dados_despesas.append({
                    'Descrição': despesa.descricao,
                    'Valor': despesa.valor,
                    'Categoria': despesa.categoria,
                    'Vencimento': despesa.data_vencimento.strftime('%d/%m/%Y'),
                    'Status': 'Pago' if despesa.pago else 'Pendente',
                    'Data Pagamento': despesa.data_pagamento.strftime('%d/%m/%Y') if despesa.data_pagamento else ''
                })
            
            # Criar dados das receitas
            receitas = self.controle.obter_receitas_mes(mes, ano)
            dados_receitas = []
            
            for receita in receitas:
                dados_receitas.append({
                    'Descrição': receita.descricao,
                    'Valor': receita.valor,
                    'Categoria': receita.categoria,
                    'Data Recebimento': receita.data_recebimento.strftime('%d/%m/%Y')
                })
            
            # Criar dados das contas
            dados_contas = []
            for nome_conta in self.controle.obter_contas_bancarias():
                conta = self.controle.contas_bancarias[nome_conta]
                dados_contas.append({
                    'Conta': nome_conta,
                    'Banco': conta.banco,
                    'Saldo Atual': conta.saldo_atual
                })
            
            # Criar resumo
            total_receitas = self.controle.calcular_total_receitas(mes, ano)
            total_despesas = self.controle.calcular_total_despesas(mes, ano)
            total_despesas_pagas = self.controle.calcular_total_despesas_pagas(mes, ano)
            saldo_total = sum(self.controle.obter_saldo_conta(conta) for conta in self.controle.obter_contas_bancarias())
            
            dados_resumo = [{
                'Métrica': 'Total de Receitas',
                'Valor': total_receitas
            }, {
                'Métrica': 'Total de Despesas',
                'Valor': total_despesas
            }, {
                'Métrica': 'Despesas Pagas',
                'Valor': total_despesas_pagas
            }, {
                'Métrica': 'Despesas Pendentes',
                'Valor': total_despesas - total_despesas_pagas
            }, {
                'Métrica': 'Saldo Total das Contas',
                'Valor': saldo_total
            }]
            
            # Criar arquivo Excel
            with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
                # Aba de resumo
                pd.DataFrame(dados_resumo).to_excel(writer, sheet_name='Resumo', index=False)
                
                # Aba de despesas
                if dados_despesas:
                    pd.DataFrame(dados_despesas).to_excel(writer, sheet_name='Despesas', index=False)
                
                # Aba de receitas
                if dados_receitas:
                    pd.DataFrame(dados_receitas).to_excel(writer, sheet_name='Receitas', index=False)
                
                # Aba de contas
                if dados_contas:
                    pd.DataFrame(dados_contas).to_excel(writer, sheet_name='Contas', index=False)
            
            print(f"✅ Relatório exportado para: {nome_arquivo}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao exportar para Excel: {e}")
            return False
    
    def exportar_relatorio_mensal_pdf(self, mes: int, ano: int, nome_arquivo: str = None) -> bool:
        """Exporta relatório mensal para PDF"""
        if not REPORTLAB_DISPONIVEL:
            print("❌ ReportLab não está instalado. Execute: pip install reportlab")
            return False
        
        try:
            if nome_arquivo is None:
                nome_arquivo = f"relatorio_mensal_{mes:02d}_{ano}.pdf"
            
            doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Título
            titulo = Paragraph(f"<b>Relatório Financeiro - {self.obter_mes_nome(mes)}/{ano}</b>", 
                             styles['Title'])
            story.append(titulo)
            story.append(Spacer(1, 12))
            
            # Data de geração
            data_geracao = Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                   styles['Normal'])
            story.append(data_geracao)
            story.append(Spacer(1, 20))
            
            # Resumo Financeiro
            story.append(Paragraph("<b>Resumo Financeiro</b>", styles['Heading2']))
            
            total_receitas = self.controle.calcular_total_receitas(mes, ano)
            total_despesas = self.controle.calcular_total_despesas(mes, ano)
            total_despesas_pagas = self.controle.calcular_total_despesas_pagas(mes, ano)
            saldo_total = sum(self.controle.obter_saldo_conta(conta) for conta in self.controle.obter_contas_bancarias())
            
            dados_resumo = [
                ['Métrica', 'Valor (R$)'],
                ['Total de Receitas', f'{total_receitas:.2f}'],
                ['Total de Despesas', f'{total_despesas:.2f}'],
                ['Despesas Pagas', f'{total_despesas_pagas:.2f}'],
                ['Despesas Pendentes', f'{total_despesas - total_despesas_pagas:.2f}'],
                ['Saldo Total das Contas', f'{saldo_total:.2f}']
            ]
            
            tabela_resumo = Table(dados_resumo)
            tabela_resumo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(tabela_resumo)
            story.append(Spacer(1, 20))
            
            # Contas Bancárias
            story.append(Paragraph("<b>Contas Bancárias</b>", styles['Heading2']))
            
            dados_contas = [['Conta', 'Banco', 'Saldo (R$)']]
            for nome_conta in self.controle.obter_contas_bancarias():
                conta = self.controle.contas_bancarias[nome_conta]
                dados_contas.append([nome_conta, conta.banco, f'{conta.saldo_atual:.2f}'])
            
            if len(dados_contas) > 1:
                tabela_contas = Table(dados_contas)
                tabela_contas.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(tabela_contas)
            else:
                story.append(Paragraph("Nenhuma conta bancária encontrada.", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # Despesas
            story.append(Paragraph("<b>Despesas</b>", styles['Heading2']))
            
            despesas = self.controle.obter_despesas_mes(mes, ano)
            if despesas:
                dados_despesas = [['Descrição', 'Valor (R$)', 'Categoria', 'Vencimento', 'Status']]
                
                for despesa in despesas:
                    status = 'Pago' if despesa.pago else 'Pendente'
                    dados_despesas.append([
                        despesa.descricao[:30] + '...' if len(despesa.descricao) > 30 else despesa.descricao,
                        f'{despesa.valor:.2f}',
                        despesa.categoria,
                        despesa.data_vencimento.strftime('%d/%m/%Y'),
                        status
                    ])
                
                tabela_despesas = Table(dados_despesas)
                tabela_despesas.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(tabela_despesas)
            else:
                story.append(Paragraph("Nenhuma despesa encontrada.", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # Receitas
            story.append(Paragraph("<b>Receitas</b>", styles['Heading2']))
            
            receitas = self.controle.obter_receitas_mes(mes, ano)
            if receitas:
                dados_receitas = [['Descrição', 'Valor (R$)', 'Categoria', 'Data Recebimento']]
                
                for receita in receitas:
                    dados_receitas.append([
                        receita.descricao[:30] + '...' if len(receita.descricao) > 30 else receita.descricao,
                        f'{receita.valor:.2f}',
                        receita.categoria,
                        receita.data_recebimento.strftime('%d/%m/%Y')
                    ])
                
                tabela_receitas = Table(dados_receitas)
                tabela_receitas.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(tabela_receitas)
            else:
                story.append(Paragraph("Nenhuma receita encontrada.", styles['Normal']))
            
            # Gerar PDF
            doc.build(story)
            
            print(f"✅ Relatório PDF exportado para: {nome_arquivo}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao exportar para PDF: {e}")
            return False
    
    def exportar_historico_conta_excel(self, nome_conta: str, nome_arquivo: str = None) -> bool:
        """Exporta histórico de uma conta para Excel"""
        if not PANDAS_DISPONIVEL:
            print("❌ Pandas não está instalado. Execute: pip install pandas openpyxl")
            return False
        
        if nome_conta not in self.controle.contas_bancarias:
            print(f"❌ Conta '{nome_conta}' não encontrada.")
            return False
        
        try:
            if nome_arquivo is None:
                nome_arquivo = f"historico_{nome_conta.replace(' ', '_')}.xlsx"
            
            conta = self.controle.contas_bancarias[nome_conta]
            
            dados_historico = []
            for movimento in conta.historico_saldo:
                data = datetime.fromisoformat(movimento['data'])
                dados_historico.append({
                    'Data': data.strftime('%d/%m/%Y %H:%M'),
                    'Operação': movimento['operacao'],
                    'Saldo Anterior': movimento['saldo_anterior'],
                    'Saldo Novo': movimento['saldo_novo'],
                    'Variação': movimento['valor']
                })
            
            # Criar DataFrame e exportar
            df = pd.DataFrame(dados_historico)
            df.to_excel(nome_arquivo, index=False, sheet_name=f'Histórico {nome_conta}')
            
            print(f"✅ Histórico da conta exportado para: {nome_arquivo}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao exportar histórico: {e}")
            return False
    
    def exportar_relatorio_anual_excel(self, ano: int, nome_arquivo: str = None) -> bool:
        """Exporta relatório anual para Excel"""
        if not PANDAS_DISPONIVEL:
            print("❌ Pandas não está instalado. Execute: pip install pandas openpyxl")
            return False
        
        try:
            if nome_arquivo is None:
                nome_arquivo = f"relatorio_anual_{ano}.xlsx"
            
            # Dados mensais
            dados_mensais = []
            for mes in range(1, 13):
                receitas = self.controle.calcular_total_receitas(mes, ano)
                despesas = self.controle.calcular_total_despesas(mes, ano)
                despesas_pagas = self.controle.calcular_total_despesas_pagas(mes, ano)
                
                if receitas > 0 or despesas > 0:
                    dados_mensais.append({
                        'Mês': self.obter_mes_nome(mes),
                        'Receitas': receitas,
                        'Despesas': despesas,
                        'Despesas Pagas': despesas_pagas,
                        'Despesas Pendentes': despesas - despesas_pagas,
                        'Saldo Líquido': receitas - despesas_pagas
                    })
            
            # Dados por categoria (despesas)
            categorias_despesas = {}
            for mes in range(1, 13):
                despesas = self.controle.obter_despesas_mes(mes, ano)
                for despesa in despesas:
                    if despesa.pago:
                        if despesa.categoria not in categorias_despesas:
                            categorias_despesas[despesa.categoria] = 0
                        categorias_despesas[despesa.categoria] += despesa.valor
            
            dados_categorias_despesas = []
            for categoria, valor in categorias_despesas.items():
                dados_categorias_despesas.append({
                    'Categoria': categoria,
                    'Total Gasto': valor
                })
            
            # Dados por categoria (receitas)
            categorias_receitas = {}
            for mes in range(1, 13):
                receitas = self.controle.obter_receitas_mes(mes, ano)
                for receita in receitas:
                    if receita.categoria not in categorias_receitas:
                        categorias_receitas[receita.categoria] = 0
                    categorias_receitas[receita.categoria] += receita.valor
            
            dados_categorias_receitas = []
            for categoria, valor in categorias_receitas.items():
                dados_categorias_receitas.append({
                    'Categoria': categoria,
                    'Total Recebido': valor
                })
            
            # Criar arquivo Excel
            with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
                # Aba mensal
                if dados_mensais:
                    pd.DataFrame(dados_mensais).to_excel(writer, sheet_name='Resumo Mensal', index=False)
                
                # Aba categorias despesas
                if dados_categorias_despesas:
                    pd.DataFrame(dados_categorias_despesas).to_excel(writer, sheet_name='Despesas por Categoria', index=False)
                
                # Aba categorias receitas
                if dados_categorias_receitas:
                    pd.DataFrame(dados_categorias_receitas).to_excel(writer, sheet_name='Receitas por Categoria', index=False)
            
            print(f"✅ Relatório anual exportado para: {nome_arquivo}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao exportar relatório anual: {e}")
            return False
    
    def exportar_backup_completo(self, nome_arquivo: str = None) -> bool:
        """Exporta backup completo dos dados em Excel"""
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
                for mes_ano, despesas in self.controle.despesas.items():
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
                for mes_ano, receitas in self.controle.receitas.items():
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
                for nome_conta, conta in self.controle.contas_bancarias.items():
                    dados_contas.append({
                        'Nome': nome_conta,
                        'Banco': conta.banco,
                        'Saldo Atual': conta.saldo_atual,
                        'Movimentações': len(conta.historico_saldo)
                    })
                
                if dados_contas:
                    pd.DataFrame(dados_contas).to_excel(writer, sheet_name='Contas Bancárias', index=False)
            
            print(f"✅ Backup completo exportado para: {nome_arquivo}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao exportar backup: {e}")
            return False

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    print("🔍 Verificando dependências para exportação...")
    
    if PANDAS_DISPONIVEL:
        print("✅ Pandas: Disponível")
    else:
        print("❌ Pandas: Não instalado")
    
    if REPORTLAB_DISPONIVEL:
        print("✅ ReportLab: Disponível")
    else:
        print("❌ ReportLab: Não instalado")
    
    try:
        import openpyxl
        print("✅ OpenPyXL: Disponível")
    except ImportError:
        print("❌ OpenPyXL: Não instalado")
    
    if not (PANDAS_DISPONIVEL and REPORTLAB_DISPONIVEL):
        print("\n📦 Para instalar todas as dependências, execute:")
        print("pip install pandas openpyxl reportlab")

if __name__ == "__main__":
    verificar_dependencias()