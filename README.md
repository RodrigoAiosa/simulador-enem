# 🎓 Simulador ENEM

Aplicação interativa para preparação para o ENEM com **40 questões**, análise de desempenho por competência e gráficos de evolução.

Construído com **Python + Streamlit**.

---

## 🚀 Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://seu-app.streamlit.app)

---

## 📚 Funcionalidades

- ✅ 40 questões organizadas em 4 áreas do ENEM
- 🎯 Feedback imediato com explicação detalhada após cada resposta
- 🔀 Questões embaralhadas a cada simulado
- 📊 Score por área (escala 0–1000, estilo TRI)
- 📡 Radar de competências
- 📌 Sugestões de onde focar os estudos
- 🔍 Revisão completa ao final com todas as questões
- 📈 Histórico de simulados na sessão

---

## 🗂️ Estrutura do projeto

```
simulador_enem/
├── app.py                  # Aplicação principal Streamlit
├── perguntas.json          # Banco de questões (40 questões)
├── requirements.txt        # Dependências Python
├── .streamlit/
│   └── config.toml         # Tema e configurações do Streamlit
├── .gitignore
└── README.md
```

---

## ⚙️ Como rodar localmente

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/simulador-enem.git
cd simulador-enem
```

### 2. Crie um ambiente virtual (recomendado)
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Execute o app
```bash
streamlit run app.py
```

O app abrirá automaticamente em `http://localhost:8501`

---

## ☁️ Deploy no Streamlit Community Cloud

1. Faça fork deste repositório no GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte sua conta GitHub
4. Selecione o repositório, branch `main` e o arquivo `app.py`
5. Clique em **Deploy!**

---

## 📝 Como adicionar novas questões

Edite o arquivo `perguntas.json` seguindo o formato:

```json
{
  "id": 41,
  "area": "Matemática",
  "competencia": "Geometria Analítica",
  "enunciado": "Enunciado da questão aqui...",
  "alternativas": [
    "Alternativa A",
    "Alternativa B",
    "Alternativa C",
    "Alternativa D",
    "Alternativa E"
  ],
  "correta": 2,
  "explicacao": "Explicação detalhada da resposta correta."
}
```

> **`correta`** é o índice (0–4) da alternativa correta.

As 4 áreas disponíveis são:
- `"Linguagens"`
- `"Ciências Humanas"`
- `"Ciências da Natureza"`
- `"Matemática"`

---

## 🛠️ Tecnologias

| Tecnologia | Uso |
|-----------|-----|
| [Streamlit](https://streamlit.io) | Interface web |
| [Plotly](https://plotly.com/python/) | Gráficos interativos |
| [Pandas](https://pandas.pydata.org) | Manipulação de dados |
| Python 3.9+ | Backend |

---

## 🗺️ Roadmap

- [ ] Sistema de login e histórico persistente (SQLite)
- [ ] Modo cronometrado (simulação real do ENEM)
- [ ] Filtro por ano da prova (questões oficiais INEP)
- [ ] Exportar resultado em PDF
- [ ] Integração com IA para explicações personalizadas
- [ ] Banco com 500+ questões

---

## 📄 Licença

MIT License — fique à vontade para usar, modificar e distribuir.

---

Feito com ❤️ para estudantes brasileiros 🇧🇷
