---
date: 2023-03-05
description: An example of Django PostgreSQL Database Connection Pooling with PgBouncer
hide:
- navigation
tags:
- python
- django
- postgresql
- docker
- pgbouncer
- tutorial
title: Django Database Connection Pooling with PgBouncer
type: post
ignore_macros: true
---

# Django PostgreSQL Database Connection Pooling with PgBouncer <br><small>March 5, 2023</small>

## Introduction

In this post, we will learn how to use PostgreSQL database connection pooling with PgBouncer for Django applications.

#### What is database connection pooling?

Database connection pooling is a technique that allows an application to reuse database connections instead of creating a new connection for each request.
This reduces the cost of opening and closing connections to the database server by maintaining a **pool** of connections that can be reused.
This improves the performance of the database and reduces the number of connections to the database server.

#### What is PgBouncer?

**PgBouncer** is a lightweight **connection pooler** for **PostgreSQL**.
It can sit between the application and the database server and manage the connections to the database server.

#### Why use PgBouncer?

- Low memory requirements (2 kB per connection by default).
- This is because PgBouncer does not need to see full packets at once.
- It is not tied to one backend server.
- The destination databases can reside on different hosts.

**Note:** This is copied from the [PgBouncer Features](https://www.pgbouncer.org/features.html) Page.

## Prerequisites

To follow this tutorial, you need to have the following installed:

- Docker
- Docker Compose

We are going to use Docker and Docker Compose to run Django, PostgreSQL and PgBouncer.

## Create a New Django Project

First, we need to create a project directory. We will call it `try-dj-pgbouncer`.

```bash
mkdir try-dj-pgbouncer
cd try-dj-pgbouncer
```

Then, we need to create a `requirements.txt` file inside the project directory that will contain the dependencies for our Django project.

```bash
touch requirements.txt
```

Add the following dependencies to the `requirements.txt` file:

```bash title="requirements.txt"
Django==4.1  # (1)!
psycopg2==2.9.5  # (2)!
dj-database-url==1.2.0 # (3)!
```

1. Specify the version of `Django` that we want to use.
2. Specify the version of `psycopg2` that we want to use. This is the PostgreSQL database adapter for Python.
3. Specify the version of `dj-database-url` that we want to use. This is a Django utility that allows us to configure the database using a URL.

Now we can add the `Dockerfile` for our Django project.

```bash
touch Dockerfile
```

Add the following content to the `Dockerfile`:

```dockerfile title="Dockerfile"
FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

RUN apt-get update \
    && apt-get install \
       -y \
       --no-install-recommends \
       --no-install-suggests \
       # Required for psycopg2
       gcc \
       g++ \
       libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy requirements.txt to the container
COPY ./requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy application code to the container
COPY . .
```

Let's build the Docker image.

```bash
docker build -t try-dj-pgbouncer .
```

Now, we can create a Django project using Docker.

```bash
docker run --rm -v $(pwd):/app try-dj-pgbouncer django-admin startproject try_dj_pgbouncer .
```

This command will create a Django project inside the current directory.

We can also create a Django app called `core` using Docker.

```bash
docker run --rm -v $(pwd):/app try-dj-pgbouncer python manage.py startapp core
```

This command will create a Django app called `core` inside the `try-dj-pgbouncer` directory.
We need to add the `core` app to the `INSTALLED_APPS` list in the `try_dj_pgbouncer/settings.py` file.

```python title="try_dj_pgbouncer/settings.py"
INSTALLED_APPS = [
    # ...
    'core',
]
```

## Setup Docker Compose for Django and PostgreSQL

We need to create a `docker-compose.yaml` file at the root of the project (`try-dj-pgbouncer/`) that will contain the `docker-compose` configuration
for our Django, PostgreSQL and PgBouncer services.

```bash
touch docker-compose.yaml
```

Add the following content to the `docker-compose.yaml` file:

```yaml title="docker-compose.yaml"
version: '3.9'

services:
  web:  # (1)!
    build:
      context: .  # (2)!
    volumes:
      - .:/app  # (3)!
    env_file:
      - ./.env  # (4)!
    ports:
      - 8000:8000  # (5)!
    depends_on:
      - db  # (6)!
    command: >  # (7)!
      bash -c "while !</dev/tcp/db/5432; do sleep 1; done;
               python manage.py runserver 0.0.0.0:8000"

  db:
    image: postgres:13.10-alpine  # (8)!
    environment:
      - POSTGRES_PASSWORD=postgres  # (9)!
    volumes:
      - postgres_data:/var/lib/postgresql/data/  # (10)!
    healthcheck:  # (11)!
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:  # (12)!
```

1. The `web` service is the Django Application.
2. The `build` context is the current directory where the `Dockerfile` is located.
3. This will mount the current directory to the `/app` directory inside the container.
4. This will load the environment variables from the `.env` file.
5. This will expose the port `8000` of the container to the host machine's port `8000`.
6. This will make sure that the `db` service is started before the `web` service.
7. This `command` will wait for the `db` service to be ready before starting the Django server.
8. The `db` service will use the `postgres:13.10-alpine` image.
9. The `POSTGRES_PASSWORD` environment variable will set the Database password to `postgres`.
10. The `volumes` will mount the `postgres_data` volume to the `/var/lib/postgresql/data/` directory inside the container. This will ensure that the database data is persisted between container restarts.
11. This will check if the database is ready to accept connections.
12. This will create a volume called `postgres_data` that will be used to persist the database data.

We also need to create a `.env` file at the root of the project (`try-dj-pgbouncer/`) that will contain the environment variables for the `docker-compose` configuration.

```bash
touch .env
```

Add the following content to the `.env` file:

```bash
DATABASE_URL=postgres://postgres:postgres@db:5432/postgres
```

??? question "How to get `DATABASE_URL` ?"

    The format of the `DATABASE_URL` is as follows:
    
    **`DATABASE_URL=<ENGINE>://<USER>:<PASSWORD>@<HOST>:<PORT>/<NAME>`**
        
    **Where:**

    - **`ENGINE`**  : The database engine. For PostgreSQL, it is `postgres`.
    - **`USER`**    : The database user.
    - **`PASSWORD`**: Password for the database user.
    - **`HOST`**    : The database host. As we are using docker-compose, we can use the service name (e.g: `db`) as the host.
    - **`PORT`**    : The port on which the database is accepting connections. For PostgreSQL, it is `5432`.
    - **`NAME`**    : Name of the database.

## Configure Django Settings to use PostgreSQL

We need to configure the Django settings to use PostgreSQL as the database engine.
We will use the `dj-database-url` package to configure the database using a `DATABASE_URL` we defined in the `.env` file.

Add the following content to the `try_dj_pgbouncer/settings.py` file:

```python title="try_dj_pgbouncer/settings.py"
# ...
import dj_database_url  # (1)!
# ...

DATABASES = {
    'default': dj_database_url.config()  # (2)!
}
```

1. This will import the `dj_database_url` package.
2. Here we are using the `dj_database_url.config()` function to configure the `deafult` `DATABASES` setting for Django.
   This function will read the `DATABASE_URL` environment variable and configure the `DATABASES` setting accordingly.

This will configure the `DATABASES` setting to use PostgreSQL as the database engine.

## Add Django Model and View

We need to add Django models and views to test the database connection pooling.

First, we need to update `core/models.py` file to add the `Post` model:

```python title="core/models.py"
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
```

Next, we need to update `core/admin.py` file to register the `Post` model:

```python title="core/admin.py"
from django.contrib import admin

from .models import Post


admin.site.register(Post)
```

Then, we need to update `core/views.py` file to add the `PostistView` view:

```python title="core/views.py"
from django.views.generic import ListView

from .models import Post


class PostistView(ListView):
    model = Post
    template_name = 'core/post_list.html'
```

Now, we need to create `core/urls.py` file to add the `PostistView` view:

```bash
touch core/urls.py
```

Add the following content to the `core/urls.py` file:

```python title="core/urls.py"
from django.urls import path

from .views import PostistView

urlpatterns = [
    path('', PostistView.as_view(), name='post_list'),
]
```

We also need to update `try_dj_pgbouncer/urls.py` file to include the `core.urls`:

```python title="try_dj_pgbouncer/urls.py"
from django.contrib import admin
from django.urls import path, include  # (1)!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # (2)!
]
```

1. This will import the `include` function from the `django.urls` module.
2. This will include the `core.urls` module.

Finally, we need to create a template file `core/templates/core/post_list.html` to render the list of posts:

```bash
mkdir -p core/templates/core/ && touch core/templates/core/post_list.html
```

Add the following content to the `core/templates/core/post_list.html` file:

``` html title="core/templates/core/post_list.html"
<!DOCTYPE html>
<html lang="en">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Post List</title>
    <body>
        {% block content %}
            <h1>Post List</h1>
            <ul>
                {% for post in object_list %}
                    <li>{{ post.title }}</li>
                {% endfor %}
            </ul>
        {% endblock %}
    </body>
</html>
```

Now, we can run Django migrations to create the `Post` table in the database:

```bash
docker-compose run --rm web python manage.py makemigrations  # (1)!
docker-compose run --rm web python manage.py migrate  # (2)!
```

1. This will create the migration files for the `Post` model.
2. This will run the migrations to create the `Post` table in the database.

We also create an admin user to access the Django admin.

```bash
docker-compose run --rm web python manage.py createsuperuser 
```

Now, we can run the Django development server.

```bash
docker-compose up --build
```

The Django development server will be available at: <http://localhost:8000/>

We can also visit Django Admin at <http://localhost:8000/admin/> and login with the admin user we created.
Then we can [create some posts](http://localhost:8000/admin/core/post/add/) from the Django admin.

After creating some posts, we can visit the post list page at <http://localhost:8000/> and see the list of posts.

!!! note

    Here we are using PostgreSQL as the database engine for Django.
    In the next section, we will see how to use PgBouncer to provide database connection pooling for Django applications.

Final Project Structure Should Look Like This:

```bash
try-dj-pgbouncer
   ├── core
   │   ├── admin.py
   │   ├── apps.py
   │   ├── __init__.py
   │   ├── migrations
   │   │   ├── 0001_initial.py
   │   │   └── __init__.py
   │   ├── models.py
   │   ├── templates
   │   │   └── core
   │   │       └── post_list.html
   │   ├── tests.py
   │   ├── urls.py
   │   └── views.py
   ├── docker-compose.yaml
   ├── Dockerfile
   ├── manage.py
   ├── requirements.txt
   └── try_dj_pgbouncer
       ├── asgi.py
       ├── __init__.py
       ├── settings.py
       ├── urls.py
       └── wsgi.py
```

## Add and Configure PgBouncer

We need to add PgBouncer service to our `docker-compose.yaml` file to provide database connection pooling for Django applications.

Add the following content to the `docker-compose.yaml` file:

```yaml hl_lines="15 32-39" title="docker-compose.yaml"
version: '3.9'

services:
  web:
    build:
      context: . 
    volumes:
      - .:/app
    env_file:
      - ./.env
    ports:
      - 8000:8000
    depends_on:
      - db
      - pgbouncer
    command: >
      bash -c "while !</dev/tcp/db/5432; do sleep 1; done;
               python manage.py runserver 0.0.0.0:8000"

  db:
    image: postgres:13.10-alpine
    environment:
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgbouncer:  # (1)!
    image: edoburu/pgbouncer:1.18.0  # (2)!
    env_file:
      - ./.env  # (3)!
    environment:
      DATABASE_URL: "${POSTGRES_DATABASE_URL}"  # (4)!
    depends_on:
      - db  # (5)!

volumes:
  postgres_data:
```

1. This will add a new service named `pgbouncer`.
2. We will use the `edoburu/pgbouncer:1.18.0` Docker image.
3. This will load the environment variables from the `.env` file.
4. This will set the `DATABASE_URL` environment variable to the `POSTGRES_DATABASE_URL` environment variable which will be set in the `.env` file.
5. This will add a dependency on the `db` service. This will ensure that the `db` service will be started before the `pgbouncer` service.

!!! question "Why Use `edoburu/pgbouncer` Docker Image ?"

    The official `pgbouncer/pgbouncer` Docker image was last updated 2 years ago (November 2020).
    But `edoburu/pgbouncer` is updated regularly and is the most popular (over 10+ Million downloads) PgBouncer Docker image on Docker Hub.
    You can also use `bitnami/pgbouncer` Docker image as an alternative which is also updated regularly. (Some of the configuration options are a bit different)

Now, we need to update the `.env` file.

```bash title=".env"
DATABASE_URL=postgres://postgres:postgres@pgbouncer:5432/postgres  # (1)!
POSTGRES_DATABASE_URL=postgres://postgres:postgres@db:5432/postgres  # (2)!
POOL_MODE=transaction  # (3)!
MAX_DB_CONNECTIONS=100  # (4)!
DEFAULT_POOL_SIZE=40  # (5)!
```

1. This will set the `DATABASE_URL` environment variable to use the `pgbouncer` service instead of the `db` service.
2. This will set the `POSTGRES_DATABASE_URL` environment variable to use the `db` service. `pgbouncer` service will use this environment variable to connect to the `db` service.
3. This will set the `POOL_MODE` to `transaction`. You can also set this to `session` or `statement` pooling mode. You can find more information about the different pooling modes in the [official PgBouncer documentation](https://www.pgbouncer.org/config.html#pool_mode).
4. Do not allow more than this many server connections per database (regardless of user). This considers the PgBouncer database that the client has connected to, not the PostgreSQL database of the outgoing connection.
5. How many server connections to allow per user/database pair.

There are many other configuration options available in the [official PgBouncer documentation](https://www.pgbouncer.org/config.html). You can use environment variables to set these configuration options.
The name of the environment variable should be the same as the name of the configuration option but capitalized. (e.g: `pool_mode` -> `POOL_MODE`, `max_db_connections` -> `MAX_DB_CONNECTIONS`)

!!! note

    You can also use the `pgbouncer.ini` file to set the configuration options by attaching a volume (e.g: `pgbouncer.ini:/etc/pgbouncer/pgbouncer.ini:ro`).
    You can find more information about `pgbouncer.ini` in the [official PgBouncer documentation](https://www.pgbouncer.org/config.html).

We also need to update Django settings file.

```python hl_lines="7" title="try_dj_pgbouncer/settings.py"
# ...
import dj_database_url
# ...
DATABASES = {
    'default': dj_database_url.config()
}
DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True
```

??? question "Why are we setting `DISABLE_SERVER_SIDE_CURSORS` to `True` ?"

    Using a connection pooler in transaction pooling mode (e.g. PgBouncer) requires disabling server-side cursors for that connection.
    Server-side cursors are local to a connection and remain open at the end of a transaction when `AUTOCOMMIT` is `True`.
    A subsequent transaction may attempt to fetch more results from a server-side cursor. In transaction pooling mode,
    there’s no guarantee that subsequent transactions will use the same connection. If a different connection is used,
    an error is raised when the transaction references the server-side cursor,
    because server-side cursors are only accessible in the connection in which they were created.
    One solution is to disable server-side cursors for a connection in `DATABASES` by setting `DISABLE_SERVER_SIDE_CURSORS` to True.

    **Source:** [Django Transaction pooling and server-side cursors](https://docs.djangoproject.com/en/4.1/ref/databases/#transaction-pooling-and-server-side-cursors)

Now, we can run the development server again.

```bash
docker-compose down
docker-compose up --build
```

We can visit the post list page at <http://localhost:8000/> and see the list of posts. Now Django server is using the `pgbouncer` service to connect to the `db` service.

#### Top Level Architecture Diagram

``` mermaid
flowchart LR
    
    A[Browser] <--> B(Django)
    B <--> C(PgBouncer)
    C <--> id1[(PostgreSQL)]
```

## References

- [Django Transaction pooling and server-side cursors](https://docs.djangoproject.com/en/4.1/ref/databases/#transaction-pooling-and-server-side-cursors)
- [PgBouncer](https://www.pgbouncer.org/)
- [Edoburu PgBouncer Docker Hub](https://hub.docker.com/r/edoburu/pgbouncer/)
- [Bitnami PgBouncer Docker Hub](https://hub.docker.com/r/bitnami/pgbouncer)
- [Official PgBouncer Docker Hub](https://hub.docker.com/r/pgbouncer/pgbouncer)


## Conclusion

In this post, we learned how to use PostgreSQL database connection pooling with PgBouncer for Django applications.
In production environments, PgBouncer can be really useful to reduce the number of connections to the database server and provide significant performance improvements.
You can run PgBouncer as a separate service alongside you Django application and PostgreSQL database server. If your servers are hosted in AWS you can also check out 
[AWS RDS Proxy](https://aws.amazon.com/rds/proxy/) which is a managed service that provides connection pooling for RDS databases.
