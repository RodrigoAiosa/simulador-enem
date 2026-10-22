# 🎓 Simulador ENEM

Simulador gratuito do ENEM: **20 questões por área**, explicação depois de cada
resposta, nota por área (escala 0–1000), radar de competências e relatório em
Excel. Site estático hospedado na **Vercel**, com o código no **GitHub**.

---

## 📚 Funcionalidades

- 🎯 Feedback imediato com explicação após cada resposta
- 🔀 Questões embaralhadas a cada simulado, evitando repetir as já vistas
- 📊 Nota por área (0–1000, estilo TRI) e gráfico de barras
- 📡 Radar de competências e sugestões de onde estudar
- 🔍 Revisão completa das questões ao final
- 📈 Histórico dos simulados da sessão
- 📥 Relatório completo em Excel (3 abas), gerado no navegador
- 👥 Cadastro de alunos, link de convite e telemetria de acesso

---

## 🏗️ Arquitetura

```
Navegador ──► index.html (site estático) ──► /api/aluno (função Vercel) ──► Supabase
                  └─ perguntas_400.json (banco de questões)
```

| Parte | Onde roda | Função |
|---|---|---|
| `index.html` | Vercel (estático) | Telas, simulado, gráficos e relatório em Excel |
| `perguntas_400.json` | Vercel (estático) | Banco de questões (180 questões em 4 áreas) |
| `api/aluno.js` | Vercel (função Node) | Cadastro, convites e telemetria |
| Supabase | Nuvem (banco de dados) | Tabelas `tbl_cadastro`, `tbl_telemetria_acesso` e `tbl_compartilhamento` |

A chave do Supabase **nunca vai para o navegador**: só a função `api/aluno.js`
a lê, das variáveis de ambiente da Vercel.

---

## 🗂️ Estrutura do projeto

```
simulador-enem/
├── index.html            # Interface completa (HTML + CSS + JS)
├── perguntas_400.json    # Banco de questões usado pelo site
├── perguntas.json        # Banco antigo (40 questões), não é publicado
├── api/
│   └── aluno.js          # Função serverless: cadastro, convite e telemetria
├── vercel.json           # Região (gru1) e limite de tempo da função
├── .vercelignore         # O que não vai no deploy
├── .gitignore
└── README.md
```

---

## ☁️ Deploy (GitHub + Vercel)

1. Importe o repositório na Vercel (ou, se já estiver ligado, basta dar `git push`
   na branch `main`: cada push publica automaticamente).
2. Em **Settings → Environment Variables**, crie para **Production**:
   - `SUPABASE_URL`: endereço do projeto Supabase
   - `SUPABASE_KEY`: chave de **servidor** do projeto (marque como **Sensitive**)
3. Faça um **Redeploy** para a função enxergar as variáveis.

Não há build nem dependências para instalar.

> ⚠️ Nunca coloque a chave no código nem em arquivos do repositório.
> Se uma chave for exposta, gere outra no painel do Supabase e atualize a
> variável na Vercel.

### Rodar localmente

```bash
npm i -g vercel
vercel link            # liga a pasta ao projeto da Vercel
vercel env pull .env   # baixa as variáveis (o .env não é versionado)
vercel dev             # abre em http://localhost:3000
```

Sem a API, o simulado continua funcionando em `index.html`; só o cadastro e a
telemetria dependem do banco.

---

## 📝 Como adicionar novas questões

Edite `perguntas_400.json` seguindo o formato:

```json
{
  "id": 181,
  "area": "Matemática",
  "competencia": "Geometria Analítica",
  "dificuldade": "Médio",
  "enunciado": "Enunciado da questão aqui...",
  "alternativas": ["A", "B", "C", "D", "E"],
  "correta": 2,
  "explicacao": "Explicação detalhada da resposta correta."
}
```

`correta` é o índice (0–4) da alternativa certa. Áreas aceitas:
`Linguagens`, `Ciências Humanas`, `Ciências da Natureza` e `Matemática`.
Use um `id` novo (o maior hoje é 180). Dificuldades: `Fácil`, `Médio` e `Difícil`.

---

## 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| [Vercel](https://vercel.com/) | Hospedagem do site e da função |
| [Supabase](https://supabase.com/) | Banco de dados (cadastro e telemetria) |
| HTML + CSS + JavaScript | Interface, sem framework e sem build |
| [SheetJS](https://sheetjs.com/) | Relatório em Excel, gerado no navegador |

---

## 📄 Licença

MIT License — fique à vontade para usar, modificar e distribuir.

Feito com ❤️ para estudantes brasileiros 🇧🇷
