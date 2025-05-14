# **Check-In Online – Pousada do Suíço** 🇨🇭

Este projeto tem como objetivo automatizar o sistema de **check-in de hóspedes** de uma pousada localizada em Fortaleza.

## **Descrição**

O sistema automatiza todo o processo de check-in, desde a coleta de dados dos hóspedes até a geração da documentação necessária, eliminando a necessidade de preenchimento manual de fichas e agilizando o processo de recepção dos clientes.

### **Ferramentas e tecnologias utilizadas:**
- **Google Forms** para coleta das informações dos hóspedes;
- **API do Google Sheets** para armazenamento e monitoramento;
- **Python** para automatizar:
  - Geração de **QR Codes**;
  - Criação de fichas de **check-in em PDF**;
  - Monitoramento em tempo real para processar novos **check-ins automaticamente**.

---

## 🚀 **Como utilizar**

1. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```
   
2. **Gere seu próprio arquivo `credenciais.json`** com permissões de acesso ao Google Sheets (veja instruções abaixo).

3. **Insira o arquivo `credenciais.json`** na **raiz do projeto** (mesmo nível do script `.py`).

4. **Execute o script**

## **Dependências**

O projeto requer as seguintes bibliotecas Python:
```
gspread
oauth2client
qrcode
reportlab
pillow
```

Você pode instalar todas as dependências com:
```bash
pip install -r requirements.txt
```

## 🔐 **Como obter o arquivo credenciais.json**

Para o script funcionar corretamente, você precisa gerar suas credenciais da API do Google:

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2. Crie um novo projeto (ou use um existente).
3. Ative a Google Sheets API.
4. Vá em "APIs e serviços" > "Credenciais".
5. Clique em "Criar credencial" > "Conta de serviço".
6. Gere uma chave no formato JSON e faça o download.
7. Renomeie o arquivo para `credenciais.json` e coloque na pasta do projeto.
8. Compartilhe a planilha com o e-mail da conta de serviço (visível dentro do `credenciais.json`).

## 📝 **Licença**

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
