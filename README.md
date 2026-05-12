# 🍬 PCP Vó Nena — Sistema de Planejamento e Controle da Produção

## Protótipo v1.0

Sistema digital que substitui a folha de produção em papel da fábrica Doces Vó Nena.

---

## Instalação (uma única vez)

### 1. Pré-requisitos
- Python 3.9 ou superior instalado no computador

### 2. Instalar dependências
Abra o terminal (Prompt de Comando no Windows) dentro desta pasta e rode:

```bash
pip install -r requirements.txt
```

### 3. Rodar o sistema
```bash
streamlit run painel.py
```

O sistema vai abrir automaticamente no navegador em:
**http://localhost:8501**

---

## Estrutura dos arquivos

```
pcp_vo_nena/
├── painel.py          ← Tela principal (Streamlit)
├── database.py        ← Banco de dados SQLite + dados iniciais
├── pcp_vo_nena.db     ← Banco de dados (criado automaticamente)
├── requirements.txt   ← Dependências Python
└── README.md          ← Este arquivo
```

---

## Abas do sistema

| Aba | Persona | O que mostra |
|-----|---------|-------------|
| 📋 Eraldo — Planejamento | Gestor | Embalados, Cortados, Viradas, P/Virar, PM/Balas, Parâmetros |
| 👨‍🍳 Sr. Joel — Produção | Cozinha | Quadro de produção (bandejas, potes, lembretes) |
| 🔪 Gil — Corte | Corte | Corte cocada (45g, Mini, Pet) e corte palha |
| 📦 Leonice — Embalagem | Embalagem | Pendentes de embalagem (cocada e palha) |
| 📊 Estoque Geral | Gestor | Estoque completo com alertas |

---

## Próximas versões planejadas

- [ ] Tela de preenchimento diário (Eraldo preenche pelo computador)
- [ ] Histórico de produções por data
- [ ] Cada funcionário preenche sua própria aba
- [ ] Acesso por Wi-Fi da fábrica (sem instalar nada nos outros computadores)
- [ ] Relatórios mensais de produção

---

## Observações técnicas

- O banco `pcp_vo_nena.db` é criado automaticamente na primeira execução com dados fictícios de exemplo.
- Stack: Python + Streamlit + SQLite (sem dependência do Google Sheets).
- Funciona offline — só precisa de rede local para acesso de múltiplos computadores.
