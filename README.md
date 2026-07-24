# Sistema de Vencimentos

Painel de controle de validade de produtos, com login protegido, CRUD de itens,
exportação em CSV/PDF e alertas automáticos por WhatsApp para itens vencidos
ou próximos do vencimento.

## Estrutura do projeto

```
.
├── backend/
│   ├── app.py                     # ponto de entrada (application factory)
│   ├── config.py                  # configuração via variáveis de ambiente
│   ├── database.py                # conexão com o banco (SQLite local / PostgreSQL em produção)
│   ├── api/
│   │   ├── auth.py                # /api/auth/*      → cadastro, login, logout, sessão
│   │   ├── vencimentos.py         # /api/vencimentos/* → CRUD e exportação
│   │   └── notificacoes.py        # /api/notificacoes/* → dispara o alerta de WhatsApp
│   └── services/
│       ├── whatsapp_service.py    # envio de mensagens via Twilio
│       ├── notificacao_service.py # decide o que está crítico e monta a mensagem
│       └── scheduler.py           # agendador interno opcional (APScheduler)
├── frontend/
│   ├── auth.html / auth.js / style2.css       # tela de login/cadastro
│   └── vencimentos.html / vencimentos.js / vencimentos.css  # painel
├── requirements.txt
├── Procfile                       # comando de start pro Render
└── .env.example
```

## Rotas

**Páginas**
- `GET /` — login/cadastro
- `GET /painel` — painel de vencimentos (exige sessão)

**API de autenticação** (`/api/auth`)
- `POST /api/auth/cadastro`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/verificar-sessao` — sessão de uso único: some após a checagem

**API de vencimentos** (`/api/vencimentos`)
- `GET /api/vencimentos/opcoes`
- `GET /api/vencimentos/listar`
- `POST /api/vencimentos/adicionar`
- `PUT /api/vencimentos/editar/<id>`
- `DELETE /api/vencimentos/remover/<id>`
- `GET /api/vencimentos/exportar-csv`
- `GET /api/vencimentos/exportar-pdf`

**API de notificações** (`/api/notificacoes`)
- `POST /api/notificacoes/verificar` — checa itens críticos e envia WhatsApp se houver algo.
  Protegida por header `X-Notificacoes-Token` (não por login de usuário), pensada
  pra ser chamada por um serviço de cron externo.

## Rodando localmente

```bash
pip install -r requirements.txt
cp .env.example .env   # preencha os valores, especialmente os do Twilio
cd backend
python app.py
```

Acesse `http://localhost:5000`.

## Configurando o WhatsApp (Twilio Sandbox)

O Sandbox do Twilio é grátis pra testar e não exige aprovação de conta comercial.

1. Crie uma conta em https://www.twilio.com/try-twilio.
2. No Console, vá em **Messaging → Try it out → Send a WhatsApp message** e ative o Sandbox.
3. Do celular que vai **receber** os alertas, mande a mensagem `join <código>` para o
   número do Sandbox (`+1 415 523 8886`). O Twilio confirma quando o número entrar.
   Repita esse passo em cada número extra que também deva receber os alertas —
   cada um precisa dar join individualmente.
4. Copie **Account SID** e **Auth Token** (na página inicial do Console) para
   `TWILIO_ACCOUNT_SID` e `TWILIO_AUTH_TOKEN`.
5. Preencha `WHATSAPP_DESTINO` com o(s) número(s) que deram join, no formato
   `whatsapp:+55DDDNUMERO`. Para mais de um número, separe por vírgula:
   `whatsapp:+55DDDNUMERO1,whatsapp:+55DDDNUMERO2`.

**Lembrete de 72h:** a conexão de cada número ao Sandbox expira sozinha depois
de 72 horas — é preciso reenviar o `join <código>` periodicamente enquanto o
projeto não migra para um número WhatsApp Business definitivo (sem essa
expiração).

**Limitação importante:** o Sandbox só envia mensagens pra números que deram join,
e mensagens iniciadas pela aplicação (fora de uma janela de 24h de conversa)
podem exigir um template pré-aprovado, mesmo em modo de teste. Pra uso pessoal
isso costuma funcionar bem; pra um produto real usado por terceiros, o passo
seguinte é migrar para um número WhatsApp Business aprovado pela Meta.

## Agendamento do alerta diário

Existem duas formas de disparar a checagem diária — escolha uma:

**Opção A — Cron externo (recomendado no Render free)**
O plano gratuito do Render "dorme" a aplicação depois de um tempo sem acesso,
então um agendador *dentro* do app pode simplesmente não rodar no horário
certo. A alternativa confiável é um serviço externo batendo na rota protegida
todo dia:

```bash
curl -X POST https://SEU-APP.onrender.com/api/notificacoes/verificar \
  -H "X-Notificacoes-Token: SEU_TOKEN_AQUI"
```

Serviços gratuitos pra isso: **Render Cron Jobs** (um segundo serviço no mesmo
projeto), **cron-job.org**, ou um **GitHub Actions** com `schedule`. Configure
pra rodar todo dia no horário desejado.

**Opção B — Agendador interno (APScheduler)**
Se a aplicação roda num serviço sempre ativo (plano pago do Render, VPS, etc.),
defina `SCHEDULER_ATIVO=true` e `NOTIFICACOES_HORA=08:00` (ou o horário que
preferir) nas variáveis de ambiente. O app dispara a checagem sozinho todo dia,
sem precisar de nada externo.

## Deploy no Render

O `Procfile` já aponta pro app dentro de `backend/`, então o comando de start
não precisa ser alterado manualmente — o Render detecta o `Procfile`
automaticamente. Só é preciso adicionar as novas variáveis de ambiente no
painel do Render (Settings → Environment): todas as listadas em `.env.example`.

Como a URL de produção e o `DATABASE_URL` não mudam, o restante do deploy
segue igual ao que já estava configurado.
