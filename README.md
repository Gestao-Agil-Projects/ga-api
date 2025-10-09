# ga_api

This project was generated using fastapi_template.

---

## Setup
Para iniciar o projeto, você deve ter as ferramentas instaladas:
- [Python 3.13.7+](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Docker](https://docs.docker.com/get-docker/)

Recomenda-se utilizar o Postman para testar os endpoints da API:
- [Postman](https://www.postman.com/downloads/)

Para checar o banco de dados, utilize o pgAdmin:
- [pgAdmin 4](https://www.pgadmin.org/download/)


Inicie os pre-commit-hooks com:
```bash
pre-commit install
```

---

## Rodando o projeto

Para iniciar o projeto:
1. Copie e cole o arquivo `.env-example` e o renomeie para `.env`
2. execute:
    ```bash
    poetry install
    docker-compose -f docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build
    ```
   
    Caso queira evitar o build, remova a flag --build no final do comando.

Feito o processo acima, no terminal deve indicar algo semelhante a:
```
db-1  | 2025-09-11 16:50:55.799 UTC [1] LOG:  database system is ready to accept connections
api-1  | INFO:     Will watch for changes in these directories: ['/app/src']
api-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
api-1  | INFO:     Started reloader process [1] using WatchFiles
api-1  | INFO:     Started server process [8]
api-1  | INFO:     Waiting for application startup.
api-1  | INFO:     Application startup complete.
```
E agora a API vai estar rodando na porta 8000.

Acesse a [Documentação do Swagger](http://localhost:8000/api/docs)

---

## Configurações manuais

Configurações feitas após o projeto gerado com o `fastapi-template`:

- adicionado no `[tool.mypy]` do arquivo `pyproject.toml` a regra:
```
  exclude = [
    "^ga_api/db/models/users.py$",
    "^tests/$"
]
```
- adicionado no `[tool.ruff]` do arquivo `pyproject.toml` a regra:
```
exclude = [
    "ga_api/db/migrations",
    "tests/*",
    ".venv/"
]
```
- remoção da regra `D` (docstring) do `[tool.ruff.select]` no arquivo `pyproject.toml`
- criação do `.env-example`
- adicionada etapa de rodar testes no pre-commit
- removido `# type: ignore` do `users.py` e do `users/views.py`

---

## Poetry

This project uses poetry. It's a modern dependency management
tool.

To run the project use this set of commands:

```bash
poetry install
poetry run python -m ga_api
```

This will start the server on the configured host.

You can find swagger documentation at `/api/docs`.

You can read more about poetry here: https://python-poetry.org/

## Docker

You can start the project with docker using this command:

```bash
docker-compose up --build
```

If you want to develop in docker with autoreload and exposed ports add `-f deploy/docker-compose.dev.yml` to your docker command.
Like this:

```bash
docker-compose -f docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build
```

This command exposes the web application on port 8000, mounts current directory and enables autoreload.

But you have to rebuild image every time you modify `poetry.lock` or `pyproject.toml` with this command:

```bash
docker-compose build
```

## Project structure

```bash
$ tree "ga_api"
ga_api
├── conftest.py  # Fixtures for all tests.
├── db  # module contains db configurations
│   ├── dao  # Data Access Objects. Contains different classes to interact with database.
│   └── models  # Package contains different models for ORMs.
├── __main__.py  # Startup script. Starts uvicorn.
├── services  # Package for different external services such as rabbit or redis etc.
├── settings.py  # Main configuration settings for project.
├── static  # Static content.
├── tests  # Tests for project.
└── web  # Package contains web server. Handlers, startup config.
    ├── api  # Package with all handlers.
    │   └── router.py  # Main router.
    ├── application.py  # FastAPI application configuration.
    └── lifespan.py  # Contains actions to perform on startup and shutdown.
```

## Configuration

This application can be configured with environment variables.

You can create `.env` file in the root directory and place all
environment variables here. 

All environment variables should start with "GA_API_" prefix.

For example if you see in your "ga_api/settings.py" a variable named like
`random_parameter`, you should provide the "GA_API_RANDOM_PARAMETER" 
variable to configure the value. This behaviour can be changed by overriding `env_prefix` property
in `ga_api.settings.Settings.Config`.

An example of .env file:
```bash
GA_API_RELOAD="True"
GA_API_PORT="8000"
GA_API_ENVIRONMENT="dev"
```

You can read more about BaseSettings class here: https://pydantic-docs.helpmanual.io/usage/settings/

## Pre-commit

To install pre-commit simply run inside the shell:
```bash
pre-commit install
```

pre-commit is very useful to check your code before publishing it.
It's configured using .pre-commit-config.yaml file.

By default it runs:
* black (formats your code);
* mypy (validates types);
* ruff (spots possible bugs);


You can read more about pre-commit here: https://pre-commit.com/


## Running tests

If you want to run it in docker, simply run:

```bash
docker-compose run --build --rm api pytest -vv .
docker-compose down
```

For running tests on your local machine.
1. you need to start a database.

I prefer doing it with docker:
```bash
docker run -p "5432:5432" -e "POSTGRES_PASSWORD=ga_api" -e "POSTGRES_USER=ga_api" -e "POSTGRES_DB=ga_api" postgres:16.3-bullseye
```


2. Run the pytest.
```bash
pytest -vv .
```
