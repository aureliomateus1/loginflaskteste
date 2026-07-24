let itens = [];
let idEmEdicao = null;

// ===== CARREGAR OPÇÕES (categorias e tipos) NOS SELECTS =====
async function carregarOpcoes() {
    const resposta = await fetch('/api/vencimentos/opcoes', { credentials: 'include' });
    if (!resposta.ok) return;
    const dados = await resposta.json();

    const selects = [
        document.getElementById('selectCategoria'),
        document.getElementById('selectCategoriaModal')
    ];
    selects.forEach(select => {
        dados.categorias.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat;
            opt.textContent = cat;
            select.appendChild(opt);
        });
    });

    const selectTipo = document.getElementById('selectTipo');
    dados.tipos.forEach(tipo => {
        const opt = document.createElement('option');
        opt.value = tipo;
        opt.textContent = tipo;
        selectTipo.appendChild(opt);
    });
}


// ===== CARREGAR E RENDERIZAR A LISTA =====
async function carregarLista() {
    const resposta = await fetch('/api/vencimentos/listar', { credentials: 'include' });
    if (!resposta.ok) return;
    itens = await resposta.json();
    renderizarTabela(itens);
    atualizarCards(itens);
    renderizarDestaques(itens);
    atualizarGrafico(itens);
}

function renderizarTabela(lista) {
    const corpo = document.getElementById('corpoTabela');
    corpo.innerHTML = '';

    lista.forEach(item => {
        const linha = document.createElement('tr');
        linha.innerHTML = `
            <td>${item.nome}</td>
            <td>${item.categoria}</td>
            <td>${item.tipo}</td>
            <td>${item.lote || ''}</td>
            <td>${item.quantidade}</td>
            <td>${item.data}</td>
            <td>${item.dias}</td>
            <td class="status-${item.status}">${item.status}</td>
            <td>
                <button class="v-acao-btn" title="Editar" onclick="editarItem(${item.id})">✏️</button>
                <button class="v-acao-btn" title="Imprimir etiqueta" onclick="imprimirEtiqueta(${item.id})">🏷️</button>
                <button class="v-acao-btn remover" title="Remover" onclick="removerItem(${item.id})">🗑️</button>
            </td>
        `;
        corpo.appendChild(linha);
    });
}

function atualizarCards(lista) {
    const vencidos = lista.filter(i => i.status === 'VENCIDO').length;
    const proximos = lista.filter(i => i.status === 'PROXIMO').length;

    animarNumero('cardVencidos', vencidos);
    animarNumero('cardProximos', proximos);
    animarNumero('cardTotal', lista.length);
}

// Anima a contagem de 0 até o valor final — reforça a sensação de painel "vivo"
function animarNumero(id, valorFinal) {
    const el = document.getElementById(id);
    const valorInicial = parseInt(el.textContent) || 0;
    if (valorInicial === valorFinal) return;

    const duracao = 500;
    const passos = 20;
    const incremento = (valorFinal - valorInicial) / passos;
    let atual = valorInicial;
    let passo = 0;

    const intervalo = setInterval(() => {
        passo++;
        atual += incremento;
        el.textContent = Math.round(atual);
        if (passo >= passos) {
            el.textContent = valorFinal;
            clearInterval(intervalo);
        }
    }, duracao / passos);
}


// ===== DESTAQUES: ÚLTIMOS ADICIONADOS E VENCENDO/PRÓXIMOS =====
function renderizarDestaques(lista) {
    const ultimos = [...lista].sort((a, b) => b.id - a.id).slice(0, 5);
    const vencendo = lista
        .filter(i => i.status === 'VENCIDO' || i.status === 'PROXIMO')
        .sort((a, b) => a.dias - b.dias)
        .slice(0, 6);

    const listaUltimos = document.getElementById('listaUltimos');
    const listaVencendo = document.getElementById('listaVencendo');

    listaUltimos.innerHTML = ultimos.length
        ? ultimos.map(item => `
            <div class="v-mini-item">
                <span class="v-mini-dot status-${item.status}"></span>
                <div class="v-mini-info">
                    <strong>${item.nome}</strong>
                    <span>${item.categoria} · lote ${item.lote || '—'}</span>
                </div>
                <span class="v-mini-data">${item.data}</span>
            </div>
        `).join('')
        : '<p class="v-mini-vazio">Nenhum item cadastrado ainda.</p>';

    listaVencendo.innerHTML = vencendo.length
        ? vencendo.map(item => `
            <div class="v-mini-item">
                <span class="v-mini-dot status-${item.status}"></span>
                <div class="v-mini-info">
                    <strong>${item.nome}</strong>
                    <span>${item.categoria} · lote ${item.lote || '—'}</span>
                </div>
                <span class="v-mini-dias status-${item.status}">${item.dias < 0 ? `${Math.abs(item.dias)}d vencido` : `${item.dias}d restantes`}</span>
            </div>
        `).join('')
        : '<p class="v-mini-vazio">Nada vencendo no momento. 🎉</p>';
}


// ===== GRÁFICO DE DISTRIBUIÇÃO POR STATUS =====
let graficoStatusInstancia = null;

function atualizarGrafico(lista) {
    const vencidos = lista.filter(i => i.status === 'VENCIDO').length;
    const proximos = lista.filter(i => i.status === 'PROXIMO').length;
    const ok = lista.filter(i => i.status === 'OK').length;

    const canvas = document.getElementById('graficoStatus');
    if (!canvas || typeof Chart === 'undefined') return;

    if (graficoStatusInstancia) {
        graficoStatusInstancia.data.datasets[0].data = [vencidos, proximos, ok];
        graficoStatusInstancia.update();
        return;
    }

    graficoStatusInstancia = new Chart(canvas.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: ['Vencidos', 'Próximos', 'OK'],
            datasets: [{
                data: [vencidos, proximos, ok],
                backgroundColor: ['#DC2626', '#D97706', '#16A34A'],
                borderWidth: 0,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '68%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { font: { family: 'Inter', size: 12 }, padding: 14, boxWidth: 10 }
                }
            }
        }
    });
}


// ===== PESQUISA POR TEXTO =====
document.getElementById('inputPesquisa').addEventListener('keyup', function () {
    const texto = this.value.toLowerCase();
    const filtrados = itens.filter(item =>
        item.nome.toLowerCase().includes(texto) ||
        item.categoria.toLowerCase().includes(texto) ||
        item.tipo.toLowerCase().includes(texto) ||
        (item.lote || '').toLowerCase().includes(texto)
    );
    renderizarTabela(filtrados);
});


// ===== ADICIONAR =====
document.getElementById('btnAdicionar').addEventListener('click', async function () {
    const erro = document.getElementById('erroForm');
    erro.textContent = '';

    const corpo = {
        nome: document.getElementById('inputNome').value.trim(),
        categoria: document.getElementById('selectCategoria').value,
        tipo: document.getElementById('selectTipo').value,
        lote: document.getElementById('inputLote').value.trim(),
        quantidade: document.getElementById('inputQuantidade').value,
        data: document.getElementById('inputData').value
    };

    const resposta = await fetch('/api/vencimentos/adicionar', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(corpo)
    });

    const dados = await resposta.json();

    if (resposta.ok) {
        limparFormulario();
        carregarLista();
    } else {
        erro.textContent = dados.mensagem;
    }
});

function limparFormulario() {
    document.getElementById('inputNome').value = '';
    document.getElementById('selectCategoria').value = '';
    document.getElementById('selectTipo').value = '';
    document.getElementById('inputLote').value = '';
    document.getElementById('inputQuantidade').value = '';
    document.getElementById('inputData').value = '';
}


// ===== EDITAR =====
function editarItem(id) {
    const item = itens.find(i => i.id === id);
    if (!item) return;

    idEmEdicao = id;

    document.getElementById('inputNome').value = item.nome;
    document.getElementById('selectCategoria').value = item.categoria;
    document.getElementById('selectTipo').value = item.tipo;
    document.getElementById('inputLote').value = item.lote || '';
    document.getElementById('inputQuantidade').value = item.quantidade;
    document.getElementById('inputData').value = item.data_iso;

    document.getElementById('btnAdicionar').style.display = 'none';
    document.getElementById('btnSalvarEdicao').style.display = 'block';
    document.getElementById('btnCancelarEdicao').style.display = 'block';
}

document.getElementById('btnCancelarEdicao').addEventListener('click', function () {
    idEmEdicao = null;
    limparFormulario();
    document.getElementById('btnAdicionar').style.display = 'block';
    document.getElementById('btnSalvarEdicao').style.display = 'none';
    document.getElementById('btnCancelarEdicao').style.display = 'none';
});

document.getElementById('btnSalvarEdicao').addEventListener('click', async function () {
    const erro = document.getElementById('erroForm');
    erro.textContent = '';

    const corpo = {
        nome: document.getElementById('inputNome').value.trim(),
        categoria: document.getElementById('selectCategoria').value,
        tipo: document.getElementById('selectTipo').value,
        lote: document.getElementById('inputLote').value.trim(),
        quantidade: document.getElementById('inputQuantidade').value,
        data: document.getElementById('inputData').value
    };

    const resposta = await fetch(`/api/vencimentos/editar/${idEmEdicao}`, {
        method: 'PUT',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(corpo)
    });

    const dados = await resposta.json();

    if (resposta.ok) {
        idEmEdicao = null;
        limparFormulario();
        document.getElementById('btnAdicionar').style.display = 'block';
        document.getElementById('btnSalvarEdicao').style.display = 'none';
        document.getElementById('btnCancelarEdicao').style.display = 'none';
        carregarLista();
    } else {
        erro.textContent = dados.mensagem;
    }
});


// ===== REMOVER =====
async function removerItem(id) {
    const confirmar = confirm('Deseja realmente remover este item?');
    if (!confirmar) return;

    await fetch(`/api/vencimentos/remover/${id}`, {
        method: 'DELETE',
        credentials: 'include'
    });

    carregarLista();
}


// ===== MODAL: PESQUISA POR CATEGORIA =====
document.getElementById('btnPesquisarCategoria').addEventListener('click', function () {
    document.getElementById('modalCategoria').style.display = 'flex';
});

document.getElementById('btnFecharModal').addEventListener('click', function () {
    document.getElementById('modalCategoria').style.display = 'none';
});

document.getElementById('selectCategoriaModal').addEventListener('change', function () {
    const categoria = this.value;
    const corpo = document.getElementById('corpoTabelaModal');
    corpo.innerHTML = '';

    if (!categoria) return;

    const filtrados = itens.filter(item => item.categoria === categoria);

    filtrados.forEach(item => {
        const linha = document.createElement('tr');
        linha.innerHTML = `
            <td>${item.nome}</td>
            <td>${item.tipo}</td>
            <td>${item.lote || ''}</td>
            <td>${item.quantidade}</td>
            <td>${item.data}</td>
            <td class="status-${item.status}">${item.status}</td>
        `;
        corpo.appendChild(linha);
    });
});


// ===== EXPORTAR CSV / PDF (o navegador baixa direto pela URL) =====
document.getElementById('btnExportarCSV').addEventListener('click', function () {
    window.location.href = '/api/vencimentos/exportar-csv';
});

document.getElementById('btnExportarPDF').addEventListener('click', function () {
    window.location.href = '/api/vencimentos/exportar-pdf';
});


// ===== IMPRIMIR ETIQUETA =====
function imprimirEtiqueta(id) {
    const item = itens.find(i => i.id === id);
    if (!item) return;

    const situacao = item.dias < 0 ? `VENCIDO HÁ ${Math.abs(item.dias)} DIA(S)` : `VALIDADE EM ${item.dias} DIA(S)`;

    const area = document.getElementById('areaEtiqueta');
    area.innerHTML = `
        <div class="v-etiqueta status-borda-${item.status}">
            <div class="v-etiqueta-topo">
                <span class="v-etiqueta-marca">❄ Vencimentos</span>
                <span class="v-etiqueta-situacao status-${item.status}">${situacao}</span>
            </div>
            <h2>${item.nome.toUpperCase()}</h2>
            <div class="v-etiqueta-grid">
                <div><span>Categoria</span><strong>${item.categoria} · ${item.tipo}</strong></div>
                <div><span>Lote</span><strong>${item.lote || '—'} · Qtd: ${item.quantidade}</strong></div>
            </div>
            <div class="v-etiqueta-validade">
                <span>VENCIMENTO</span>
                <strong>${item.data}</strong>
            </div>
        </div>
    `;

    window.print();
}


// ===== INICIALIZAÇÃO =====
carregarOpcoes();
carregarLista();