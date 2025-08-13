# EBAC Final Project - Backend

[](https://www.google.com/search?q=https://github.com/SEU_USUARIO/projeto-final-ebac-backend)
[](https://www.google.com/search?q=https://github.com/SEU_USUARIO/projeto-final-ebac-backend/blob/main/LICENSE)

This is the backend repository for the final project of the **EBAC - Python Web Developer** course. The application is a RESTful API for a social network, built with Django REST Framework and optimized for both development and production environments using Docker.

The project architecture was designed to be scalable, secure, and easy to maintain, utilizing a multi-stage build system in Docker and separating environment configurations.

## API Features

  * **Authentication**: User registration and login with JSON Web Tokens (JWT).
  * **Profiles**: Management of user profiles, including bio, profile picture, and cover image.
  * **Posts**: Creation, editing, and deletion of posts with support for text and images.
  * **Interactions**: System for likes, comments, and retweets.
  * **Social**: Functionality to follow and unfollow other users.
  * **Notifications**: Real-time notifications for interactions (likes, comments, etc.) and new mentions or followers.

## Key Technologies

  * **Backend**: Python, Django, Django REST Framework
  * **Database**: PostgreSQL
  * **Containerization**: Docker, Docker Compose
  * **Dependency Management**: Poetry

## How to Run (Local Development)

### Prerequisites

Make sure you have **Docker** and **Docker Compose** installed.

### Steps

1.  Clone the repository and navigate to the folder:

    ```bash
    git clone https://github.com/SEU_USUARIO/projeto-final-ebac-backend.git
    cd projeto-final-ebac-backend
    ```

2.  Create a `.env` file in the project's root, using `.env.example` as a template, and fill in the necessary environment variables.

3.  Start the containers (`web` and `db`) with Docker Compose:

    ```bash
    docker-compose up --build
    ```

    On the first run, this command will build the images, perform database migrations, and seed mock data.

4.  The API will be available at `http://localhost:8000`.

## API Endpoints

The interactive API documentation is available at `http://localhost:8000/docs/`.

| Feature | Method | Endpoint |
|---|---|---|
| User Registration | `POST` | `/api/v1/accounts/register/` |
| Login | `POST` | `/api/v1/accounts/login/` |
| Posts | `GET` | `/api/v1/posts/` |
| Post Detail | `GET` | `/api/v1/posts/{id}/` |
| Like Post | `POST` | `/api/v1/posts/{id}/like/` |
| Follow User | `POST` | `/api/v1/accounts/{id}/follow/` |
| Notifications | `GET` | `/api/v1/notifications/` |
