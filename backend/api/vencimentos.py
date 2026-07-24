from flask import Blueprint, request, jsonify, session, send_file
from database import conectar, PLACEHOLDER
from datetime import datetime
import csv
import io
from reportlab.pdfgen import canvas
from auth_utils import sessao_valida

vencimentos_bp = Blueprint('vencimentos', __name__, url_prefix='/api/vencimentos')

CATEGORIAS = ["Geladeira 1", "Geladeira 2", "Geladeira 3", "Geladeira 4",
              "Geladeira 5", "Geladeira 6", "Freezer 2", "Freezer 3",
              "Pista", "Estoque", "Mercearia"]

TIPOS = ["Congelado", "Resfriado", "Temperatura Ambiente", "Quente"]


def exige_login():
    return sessao_valida()


def calcular_status(data_iso):
    data = datetime.strptime(data_iso, "%Y-%m-%d").date()
    hoje = datetime.now().date()
    dias = (data - hoje).days
    if dias < 0:
        status = "VENCIDO"
    elif dias <= 7:
        status = "PROXIMO"
    else:
        status = "OK"
    return data, dias, status


@vencimentos_bp.route('/opcoes', methods=['GET'])
def opcoes_vencimentos():
    if not exige_login():
        return jsonify({'mensagem': 'Não autenticado'}), 401
    return jsonify({'categorias': CATEGORIAS, 'tipos': TIPOS}), 200


@vencimentos_bp.route('/listar', methods=['GET'])
def listar_vencimentos():
    if not exige_login():
        return jsonify({'mensagem': 'Não autenticado'}), 401

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('SELECT id, nome, categoria, lote, tipo, quantidade, data FROM vencimentos ORDER BY data ASC')
    linhas = cursor.fetchall()
    conexao.close()

    resultado = []
    for linha in linhas:
        item_id, nome, categoria, lote, tipo, quantidade, data_iso = linha
        data, dias, status = calcular_status(data_iso)

        resultado.append({
            'id': item_id,
            'nome': nome,
            'categoria': categoria,
            'lote': lote,
            'tipo': tipo,
            'quantidade': quantidade,
            'data': data.strftime('%d/%m/%Y'),
            'data_iso': data_iso,
            'dias': dias,
            'status': status
        })

    return jsonify(resultado), 200


@vencimentos_bp.route('/adicionar', methods=['POST'])
def adicionar_vencimento():
    if not exige_login():
        return jsonify({'mensagem': 'Não autenticado'}), 401

    dados = request.get_json()
    nome = dados.get('nome', '').strip()
    categoria = dados.get('categoria', '').strip()
    lote = dados.get('lote', '').strip()
    tipo = dados.get('tipo', '').strip()
    quantidade = dados.get('quantidade')
    data_iso = dados.get('data')

    if not nome or not categoria or not tipo or not data_iso:
        return jsonify({'mensagem': 'Preencha todos os campos obrigatórios.'}), 400

    try:
        quantidade = int(quantidade)
        if quantidade < 1:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'mensagem': 'Quantidade deve ser um número inteiro positivo.'}), 400

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        f'INSERT INTO vencimentos (nome, categoria, lote, tipo, quantidade, data) VALUES ({PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER})',
        (nome, categoria, lote, tipo, quantidade, data_iso)
    )
    conexao.commit()
    conexao.close()

    return jsonify({'mensagem': 'Item adicionado com sucesso!'}), 201


@vencimentos_bp.route('/editar/<int:item_id>', methods=['PUT'])
def editar_vencimento(item_id):
    if not exige_login():
        return jsonify({'mensagem': 'Não autenticado'}), 401

    dados = request.get_json()
    nome = dados.get('nome', '').strip()
    categoria = dados.get('categoria', '').strip()
    lote = dados.get('lote', '').strip()
    tipo = dados.get('tipo', '').strip()
    quantidade = dados.get('quantidade')
    data_iso = dados.get('data')

    if not nome or not categoria or not tipo or not data_iso:
        return jsonify({'mensagem': 'Preencha todos os campos obrigatórios.'}), 400

    try:
        quantidade = int(quantidade)
        if quantidade < 1:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'mensagem': 'Quantidade deve ser um número inteiro positivo.'}), 400

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        f'UPDATE vencimentos SET nome={PLACEHOLDER}, categoria={PLACEHOLDER}, lote={PLACEHOLDER}, tipo={PLACEHOLDER}, quantidade={PLACEHOLDER}, data={PLACEHOLDER} WHERE id={PLACEHOLDER}',
        (nome, categoria, lote, tipo, quantidade, data_iso, item_id)
    )
    conexao.commit()
    conexao.close()

    return jsonify({'mensagem': 'Item atualizado com sucesso!'}), 200


@vencimentos_bp.route('/remover/<int:item_id>', methods=['DELETE'])
def remover_vencimento(item_id):
    if not exige_login():
        return jsonify({'mensagem': 'Não autenticado'}), 401

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(f'DELETE FROM vencimentos WHERE id={PLACEHOLDER}', (item_id,))
    conexao.commit()
    conexao.close()

    return jsonify({'mensagem': 'Item removido com sucesso!'}), 200


@vencimentos_bp.route('/exportar-csv', methods=['GET'])
def exportar_csv():
    if not exige_login():
        return jsonify({'mensagem': 'Não autenticado'}), 401

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('SELECT nome, categoria, tipo, lote, quantidade, data FROM vencimentos ORDER BY data ASC')
    linhas = cursor.fetchall()
    conexao.close()

    saida = io.StringIO()
    writer = csv.writer(saida)
    writer.writerow(["Produto", "Categoria", "Tipo", "Lote", "Quantidade", "Validade", "Dias", "Status"])

    for nome, categoria, tipo, lote, quantidade, data_iso in linhas:
        data, dias, status = calcular_status(data_iso)
        writer.writerow([nome, categoria, tipo, lote, quantidade, data.strftime("%d/%m/%Y"), dias, status])

    memoria = io.BytesIO(saida.getvalue().encode('utf-8-sig'))
    memoria.seek(0)

    return send_file(
        memoria,
        mimetype='text/csv',
        as_attachment=True,
        download_name='relatorio_vencimentos.csv'
    )


@vencimentos_bp.route('/exportar-pdf', methods=['GET'])
def exportar_pdf():
    if not exige_login():
        return jsonify({'mensagem': 'Não autenticado'}), 401

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute('SELECT nome, categoria, tipo, lote, quantidade, data FROM vencimentos ORDER BY data ASC')
    linhas = cursor.fetchall()
    conexao.close()

    memoria = io.BytesIO()
    pdf = canvas.Canvas(memoria)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 800, "RELATÓRIO DE VENCIMENTOS")

    y = 760
    pdf.setFont("Helvetica", 10)

    for nome, categoria, tipo, lote, quantidade, data_iso in linhas:
        texto = f"Produto: {nome} | Categoria: {categoria} | Tipo: {tipo} | Lote: {lote} | Qtd: {quantidade} | Validade: {data_iso}"
        pdf.drawString(40, y, texto)
        y -= 25
        if y < 100:
            pdf.showPage()
            y = 800

    pdf.save()
    memoria.seek(0)

    return send_file(
        memoria,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='relatorio_vencimentos.pdf'
    )
