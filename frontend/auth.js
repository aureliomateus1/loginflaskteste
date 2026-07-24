// ===== CADASTRO =====
document.getElementById('btnRegister').addEventListener('click', async function () {
    const user = document.getElementById('userReg').value;
    const pass = document.getElementById('passReg').value;
    const passConfirma = document.getElementById('passRegConfirma').value;
    const erroCadastro = document.getElementById('erroCadastro');

    erroCadastro.textContent = '';

    if (!user || !pass || !passConfirma) {
        erroCadastro.textContent = 'Preencha todos os campos.';
        return;
    }

    if (pass !== passConfirma) {
        erroCadastro.textContent = 'As senhas não coincidem.';
        return;
    }

    const resposta = await fetch('/api/auth/cadastro', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user: user, pass: pass })
    });

    const dados = await resposta.json();

    if (resposta.ok) {
        erroCadastro.style.color = '#6bff8f';
        erroCadastro.textContent = dados.mensagem;
    } else {
        erroCadastro.style.color = '#ff6b6b';
        erroCadastro.textContent = dados.mensagem;
    }
});

// ===== LOGIN =====
document.getElementById('btnLogin').addEventListener('click', async function () {
    const user = document.getElementById('userLogin').value;
    const pass = document.getElementById('passLogin').value;
    const erroLogin = document.getElementById('erroLogin');

    erroLogin.textContent = '';

    const resposta = await fetch('/api/auth/login', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user: user, pass: pass })
    });

    const dados = await resposta.json();

    if (resposta.ok) {
        window.location.href = "/painel";
    } else {
        erroLogin.textContent = dados.mensagem;
    }
});

// ===== SLIDER (troca entre Login e Cadastro) =====
const btnToggle = document.getElementById('btnToggle');
const slider = document.getElementById('slider-panel');
const title = document.getElementById('slider-title');
const text = document.getElementById('slider-text');

const loginSide = document.querySelector('.login-side');
const registerSide = document.querySelector('.register-side');

btnToggle.addEventListener('click', () => {
    slider.classList.toggle('slide-left');

    if (slider.classList.contains('slide-left')) {
        title.innerText = "Login";
        text.innerText = "Já tem uma conta?";
        btnToggle.innerText = "Fazer Login";

        loginSide.classList.add('hidden-fields');
        registerSide.classList.remove('hidden-fields');
    } else {
        title.innerText = "Cadastro";
        text.innerText = "Ainda não tem conta?";
        btnToggle.innerText = "Cadastrar";

        registerSide.classList.add('hidden-fields');
        loginSide.classList.remove('hidden-fields');
    }
});