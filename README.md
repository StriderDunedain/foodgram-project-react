# Foodgram

A recipe-sharing web app built with Django, PostgreSQL, React, and Docker.

Users can publish recipes, save favorites, follow authors, and generate a shopping list from the ingredients in saved recipes.

## Stack

* **Backend:** Python, Django, Django REST Framework
* **Database:** PostgreSQL
* **Frontend:** React
* **Web server:** Nginx
* **Deployment:** Docker Compose
* **CI/CD:** GitHub Actions

The backend is split into separate Django apps for users, recipes, and API logic, with PostgreSQL used for persistent data.


## Deployment & Running locally

The project is containerized with Docker Compose.

The production setup runs the backend, database, frontend, and Nginx as separate services. GitHub Actions is used to deploy updates to the server over SSH after changes are pushed.

```bash
git clone https://github.com/StriderDunedain/foodgram-project-react.git
cd foodgram-project-react
```

Create the required `.env` file, then start the containers:

```bash
docker compose -f infra/docker-compose.yml up -d --build
```

Apply migrations:

```bash
docker compose -f infra/docker-compose.yml exec backend python manage.py migrate
```

## About

This was my larger backend project from the Yandex Practicum Python Developer course.

Most of the work was on the Django backend and API, with the project also covering PostgreSQL, containerization, Nginx, and automated deployment.
