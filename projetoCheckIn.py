import pandas as pd
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import os
import qrcode
import re
from datetime import datetime, timedelta

# acesso à API do Google
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = ServiceAccountCredentials.from_json_keyfile_name('credenciais.json', scope)
gc = gspread.authorize(credentials)

PLANILHA = 'Respostas Check-in Pousada'
PASTA_PDF = 'fichas_checkin'

if not os.path.exists(PASTA_PDF):
    os.makedirs(PASTA_PDF)

def gerar_qrcode(form_url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(form_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save("checkin_qrcode.png")

    print(f"QR Code gerado com sucesso: checkin_qrcode.png")

def limpar_nome_para_arquivo(nome):
    nome_limpo = re.sub(r'[^\w\s-]', '', nome)  # remove caracteres especiais
    nome_limpo = re.sub(r'\s+', '_', nome_limpo.strip())  # substitui espaços por _
    return nome_limpo.lower()

def ajustar_timestamp_para_brasilia(timestamp_str):
    try:
        dt_utc = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")
        dt_brasilia = dt_utc - timedelta(hours=3)
        return dt_brasilia.strftime("%d/%m/%Y %H:%M:%S")
    except:
        return timestamp_str

def gerar_pdf(nome, documento, telefone, data_nascimento, email, timestamp):
    nome_arquivo = limpar_nome_para_arquivo(nome)
    filename = f"{PASTA_PDF}/checkin_{nome_arquivo}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("FICHA DE CHECK-IN", styles['Heading1']))
    elements.append(Paragraph("Pousada do Suíço", styles['Heading2']))
    elements.append(Spacer(1, 20))

    timestamp_corrigido = ajustar_timestamp_para_brasilia(timestamp)
    elements.append(Paragraph(f"Formulário preenchido em: {timestamp_corrigido}", styles['Normal']))
    elements.append(Spacer(1, 20))

    data = [
        ["Nome completo:", nome],
        ["Documento:", documento],
        ["Telefone:", telefone],
        ["Data de nascimento:", data_nascimento],
        ["Email:", email],
        ["Período de estadia:", "___/___/______ até ___/___/______"],
    ]

    t = Table(data, colWidths=[150, 350])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))

    elements.append(t)
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("_______________________________________________", styles['Normal']))
    elements.append(Paragraph("Assinatura do hóspede", styles['Normal']))
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("Declaro que as informações acima são verdadeiras.", styles['Normal']))

    doc.build(elements)

    print(f"PDF gerado: {filename}")
    return filename

def mapear_colunas(colunas):
    col_map = {
        "nome": next((col for col in colunas if 'nome' in col.lower()), None),
        "documento": next((col for col in colunas if any(x in col.lower() for x in ['cpf', 'rg', 'documento'])), None),
        "telefone": next((col for col in colunas if any(x in col.lower() for x in ['tel', 'fone'])), None),
        "data_nascimento": next((col for col in colunas if 'nasc' in col.lower()), None),
        "email": next((col for col in colunas if 'mail' in col.lower()), None),
        "timestamp": next((col for col in colunas if 'time' in col.lower() or 'hora' in col.lower()), "Timestamp")
    }
    return col_map

def processar_respostas():
    try:
        sheet = gc.open(PLANILHA).sheet1
        dados = sheet.get_all_values()
        if not dados:
            print("Planilha vazia. Aguardando respostas...")
            return

        colunas = dados[0]
        df = pd.DataFrame(dados[1:], columns=colunas)

        if 'Processado' not in colunas:
            sheet.update_cell(1, len(colunas) + 1, 'Processado')
            colunas.append('Processado')

        idx_processado = colunas.index('Processado')
        col_map = mapear_colunas(colunas)

        novas_entradas = 0

        for i, (idx, row) in enumerate(df.iterrows(), start=2):
            try:
                if i <= len(sheet.col_values(idx_processado + 1)) and sheet.cell(i, idx_processado + 1).value == 'Sim':
                    continue
            except:
                pass

            nome = row.get(col_map["nome"], '')
            documento = row.get(col_map["documento"], '')
            telefone = row.get(col_map["telefone"], '')
            data_nascimento = row.get(col_map["data_nascimento"], '')
            email = row.get(col_map["email"], '')
            timestamp = row.get(col_map["timestamp"], '')

            if not nome or not documento:
                continue

            pdf_path = gerar_pdf(nome, documento, telefone, data_nascimento, email, timestamp)
            sheet.update_cell(i, idx_processado + 1, 'Sim')
            novas_entradas += 1
            print(f"Processado: {nome} - PDF gerado: {pdf_path}")

        if novas_entradas == 0:
            print("Nenhuma nova entrada para processar.")
        else:
            print(f"{novas_entradas} novas entradas processadas.")

    except Exception as e:
        print(f"Erro ao processar respostas: {str(e)}")

def monitorar_planilha():
    print("Iniciando monitoramento da planilha de respostas...")
    print(f"PDFs serão salvos na pasta: {PASTA_PDF}")
    try:
        while True:
            processar_respostas()
            print("Esperando por novas respostas... (Ctrl+C para sair)")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nMonitoramento interrompido pelo usuário.")

if __name__ == "__main__":
    print("Sistema de Check-in - Pousada do Suíço")
    print("=============================================")

    opcao = input(
        "O que deseja fazer?\n1. Gerar QR Code para formulário\n2. Monitorar respostas e gerar PDFs\nEscolha (1 ou 2): ")

    if opcao == "1":
        url = input("Digite a URL do Google Forms: ")
        gerar_qrcode(url)
    elif opcao == "2":
        monitorar_planilha()
    else:
        print("Opção inválida!")
