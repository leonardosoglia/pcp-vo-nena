# ============================================================================
# Dockerfile - PCP Vo Nena para Hugging Face Spaces
#
# Receita que o HF Spaces executa para montar o ambiente onde o app vai rodar.
# Streamlit Community Cloud IGNORA este arquivo - so o HF Spaces usa.
#
# Estrategia:
#   - Python 3.13 slim (estavel + wheels prontas pra psycopg-binary, pandas, plotly)
#   - Usuario nao-root uid=1000 (exigencia do HF Spaces)
#   - Streamlit headless na porta 8501 (porta padrao do HF p/ Streamlit)
#   - Variaveis de ambiente do app (DATABASE_URL) injetadas via Settings > Secrets
#     do Space, NAO hardcoded aqui.
# ============================================================================

FROM python:3.13-slim

# HF Spaces exige usuario nao-root com uid 1000.
RUN useradd -m -u 1000 user
USER user

# PATH inclui ~/.local/bin para encontrar `streamlit` instalado via --user.
# STREAMLIT_SERVER_ADDRESS=0.0.0.0 e necessario pro container aceitar conexoes externas.
# STREAMLIT_SERVER_HEADLESS=true evita tentativa de abrir navegador (nao tem display).
ENV PATH="/home/user/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /home/user/app

# Copia requirements.txt primeiro para aproveitar cache de layer Docker:
# se so o codigo mudar (sem mexer em deps), o pip install nao re-executa.
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Agora copia o restante do projeto (lancamento.py, pages/, database.py, ...).
COPY --chown=user:user . .

# Streamlit escuta na 8501 - mesmo valor declarado em app_port: 8501 no README.md.
EXPOSE 8501

# Comando que liga o app quando o Space inicia.
# Entry novo: app.py — usa st.navigation pra montar sidebar organizada.
# O lancamento.py virou apenas uma das paginas (referenciada pelo app.py).
CMD ["streamlit", "run", "app.py"]
