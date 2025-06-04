from flask import Flask, render_template, request, redirect, flash
import openpyxl
import os
import sys
import adicionarCartao
import webbrowser
import threading

app = Flask(__name__)
app.secret_key = 'segredo123'  # Necessário para usar flash messages

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # Usado pelo PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        deck_name = request.form.get('deck_name', '').strip()
        dados = []

        # Coletar os dados das frases
        for i in range(1, 11):
            front = request.form.get(f'front{i}', '').strip()
            back = request.form.get(f'back{i}', '').strip()
            if front and back:
                dados.append((front, back))

        # Validações
        if not deck_name:
            flash("⚠️ Por favor, informe o nome do baralho.")
            return render_template('index.html', deck_name=deck_name, dados=dados)

        if not dados:
            flash("⚠️ Por favor, preencha ao menos uma frase na frente e no verso.")
            return render_template('index.html', deck_name=deck_name, dados=dados)

        excel_path = resource_path("cartoes.xlsx")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Front", "Back"])
        for linha in dados:
            ws.append(linha)
        wb.save(excel_path)

        resultado = adicionarCartao.processar_planilha(excel_path, deck_name)

        if resultado == "baralho_nao_encontrado":
            flash(f"❌ Baralho '{deck_name}' não encontrado no Anki. Verifique o nome.")
            # Voltar com dados preenchidos
            return render_template('index.html', deck_name=deck_name, dados=dados)
        else:
            flash("✅ Cartões adicionados com sucesso!")
            return redirect('/')

    # GET request
    return render_template('index.html')

if __name__ == '__main__':
    threading.Timer(1.5, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(debug=False)