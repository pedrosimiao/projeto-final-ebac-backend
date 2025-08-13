[English version](/README-en.md)

# Projeto Final EBAC - Backend

[![Status de Construção](https://img.shields.io/badge/Status-Concluído-brightgreen.svg)](https://github.com/SEU_USUARIO/projeto-final-ebac-backend)
[![Licença](https://img.shields.io/badge/Licença-MIT-blue.svg)](https://github.com/SEU_USUARIO/projeto-final-ebac-backend/blob/main/LICENSE)

Este é o repositório do backend para o projeto final do curso **EBAC - Desenvolvedor Web Python**. A aplicação é uma API RESTful de uma rede social, desenvolvida com Django REST Framework e otimizada para ambientes de desenvolvimento e produção usando Docker.

A arquitetura do projeto foi desenhada para ser escalável, segura e fácil de manter, utilizando um sistema de `multi-stage build` no Docker e separando as configurações de ambiente.

## Funcionalidades da API

* **Autenticação**: Registro e login de usuários com JSON Web Tokens (JWT).
* **Perfis**: Gerenciamento de perfis de usuário, incluindo bio, foto de perfil e imagem de capa.
* **Posts**: Criação, edição e exclusão de posts com suporte a texto e imagens.
* **Interações**: Sistema de likes, comentários e retweets.
* **Social**: Funcionalidade de seguir e deixar de seguir outros usuários.
* **Notificações**: Notificações em tempo real para interações (likes, comentários, etc.) e novas menções ou seguidores.

## Tecnologias Principais

* **Backend**: Python, Django, Django REST Framework
* **Banco de Dados**: PostgreSQL
* **Contêinerização**: Docker, Docker Compose
* **Gerenciamento de Dependências**: Poetry

## Como Executar (Desenvolvimento Local)

### Pré-requisitos

Certifique-se de ter **Docker** e **Docker Compose** instalados.

### Passos

1.  Clone o repositório e navegue até a pasta:
    ```bash
    git clone [https://github.com/SEU_USUARIO/projeto-final-ebac-backend.git](https://github.com/SEU_USUARIO/projeto-final-ebac-backend.git)
    cd projeto-final-ebac-backend
    ```

2.  Crie um arquivo `.env` na raiz do projeto, usando o `.env.example` como modelo, e preencha as variáveis de ambiente necessárias.

3.  Inicie os contêineres (`web` e `db`) com Docker Compose:
    ```bash
    docker-compose up --build
    ```
    Na primeira execução, o comando irá construir as imagens, rodar as migrações do banco e semear os dados de mock.

4.  A API estará acessível em `http://localhost:8000`.

## Endpoints da API

A documentação interativa da API está disponível em `http://localhost:8000/docs/`.

| Funcionalidade         | Método | Endpoint                        |
|------------------------|--------|---------------------------------|
| Registro de Usuário    | `POST` | `/api/v1/accounts/register/`    |
| Login                  | `POST` | `/api/v1/accounts/login/`       |
| Posts                  | `GET`  | `/api/v1/posts/`                |
| Detalhe do Post        | `GET`  | `/api/v1/posts/{id}/`           |
| Curtir Post            | `POST` | `/api/v1/posts/{id}/like/`      |
| Seguir Usuário         | `POST` | `/api/v1/accounts/{id}/follow/` |
| Notificações           | `GET`  | `/api/v1/notifications/`        |
