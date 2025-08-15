# Abordagem de multi-stage build 
# separação entre etapas, "stages" (base, desenvolvimento e produção) 

# A imagem base instala apenas as dependências essenciais do sistema (compiladores e bibliotecas C) 

# O estágio development instala o Poetry, configura a virtualenv fora do projeto (/opt/venv) 
# e instala apenas as dependências de produção, 
# respeitando o cache de build ao copiar apenas os arquivos de lock antes do código-fonte. 

# O estágio production herda o ambiente Python já preparado, 
# mas não executa instalações adicionais nem compilações
# apenas copia os binários e arquivos do estágio anterior, 
# Imagem final mais leve e segura. Pronta pra rodar com o Gunicorn. 

# -----------------------------------------------------------
# STAGE BASE: config da imagem base python & install system dependencies 
# -----------------------------------------------------------

# imagem base do Python 
# Debian Bookworm (Debian 12)
# slim version --> install libs necessárias manualmente
FROM python:3.12.11-slim-bookworm AS base

# env variables para o container

# PYTHONDONTWRITEBYTECODE 1: desabilita writting de bytecode compilado (.pyc) 
# PYTHONUNBUFFERED 1: saída de log em tempo real sem armazenamendo em buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# update do sistema (apt-get update) e comando de instalação das libs necessárias (apt-get -y install)
RUN apt-get update && apt-get -y install \
    # libpq-dev: conexão com PostgreSQL
    # gcc: compilador C p/ deps
    # curl: downloader de dependencies (instalação do Poetry)
    libpq-dev gcc curl \
    # libs low-level em C para processamento de imagem (usadas pelo Pillow)
    # compila os bindings nativos pra JPEG, PNG...
    # libjpeg-dev: support read/write JPEG files 
    # zlib1g-dev: support read/write PNG files (compressão zlib)
    libjpeg-dev zlib1g-dev \
    # ferramentas client PostgreSQL, incluindo pg_isready
    postgresql-client \
    # remoção de lista de packages (cache) baixados pelo apt-get update
    && rm -rf /var/lib/apt/lists/*


# -----------------------------------------------------------
# STAGE DEVELOPMENT: config ambiente de desenvolvimento com Poetry e dependências
# -----------------------------------------------------------

# herda da imagem base (python:3.12.11-slim-bookworm)
FROM base AS development

# argumentos de build
ARG SECRET_KEY_ARG
ARG DEBUG_ARG
ARG DATABASE_URL_ARG
# variáveis de ambiente no ambiente de build = argumentos de build
ENV SECRET_KEY=${SECRET_KEY_ARG}
ENV DEBUG=${DEBUG_ARG}
ENV DATABASE_URL=${DATABASE_URL_ARG}

# env variables Poetry e virtual env
# "/opt/venv": endereço do venv (armazena binários, libs python e o virtual env)
ENV VIRTUAL_ENV="/opt/venv" \
    # criação automática de venv poetry = false
    POETRY_VIRTUALENVS_CREATE=false \
    # precaução (criação de venv dentro do projeto = false)
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    # impedir prompts de entrada
    POETRY_NO_INTERACTION=1 \
    # versão do poetry
    POETRY_VERSION=1.8.5 \
    # allow cache p/ acelerar reinstalações no dev
    PIP_NO_CACHE_DIR=off \
    # desabilitar avisos de update do pip
    PIP_DISABLE_PIP_VERSION_CHECK=on


# install global do Poetry via curl (script oficial) 
# -sSL --> s: silent (promptless), S: Show error, L: seguir redirecionamento HTTP; 
RUN curl -sSL https://install.python-poetry.org | python3 -

# add Poetry (~/.local/bin) & "/opt/venv" ($VIRTUAL_ENV/bin) to PATH
ENV PATH="/root/.local/bin:$PATH"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

# copiando config files do Poetry para o container
# ./ reinstalar deps apenas se esses arquivos mudarem
COPY poetry.lock pyproject.toml ./ 

# criar o venv e install deps do projeto (default: produção)
# --no-root: não instalar o próprio projeto como pacote
# --no-dev: ignore deps de desenvolvimento
RUN python -m venv $VIRTUAL_ENV \
    && . $VIRTUAL_ENV/bin/activate \
    && poetry install --no-root --no-dev

# copy código-fonte da aplicação para o container
# copy * from twitter-clone-backend paste in /app (WORKDIR) 
COPY . .


# copy script entrypoint & torna executável (stage development)
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# define ENTRYPOINT & CMD padrão para entrypoint.sh
# ENTRYPOINT --> exec script sempre
# CMD --> comando pardrão: argumento para o ENTRYPOINT
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]


# -----------------------------------------------------------
# STAGE "PRODUCTION": Cria a imagem final para produção.
# -----------------------------------------------------------
FROM base AS production

WORKDIR /app

# env variables: 
# diretório da venv instalada 
ENV VIRTUAL_ENV="/opt/venv"
# caminho do PATH da venv 
ENV PATH="$VIRTUAL_ENV/bin:/root/.local/bin:$PATH"

# from config.settings import *
ENV DJANGO_SETTINGS_MODULE=config.settings

# copia o Poetry & venv do stage development pra a imagem final.
COPY --from=development /root/.local /root/.local
COPY --from=development /opt/venv /opt/venv

# copia o código-fonte da aplicação (estáticos coletados) para a imagem final.
COPY --from=development /app /app

# Copia media direto para /app/media
COPY ./media /app/media

# define porta 8000 para acesso externo
EXPOSE 8000

# copy script entrypoint.sh & torna executável (stage prodution)
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# define ENTRYPOINT & CMD padrão para o entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["poetry", "run", "gunicorn", "--workers=4", "--bind=0.0.0.0:8000", "config.wsgi:application"]