# FastAPI
### Quem é o FastAPi?
Framework FastAPI, alta performance, fácil de aprender, fácil de codar, pronto para produção.
FastAPI é um moderno e rápido (alta performance) framework web para construção de APIs com Python 3.6 ou superior, baseado nos type hints padrões do Python.

### Async
Código assíncrono apenas significa que a linguagem tem um jeito de dizer para o computador / programa que em certo ponto, ele terá que esperar por algo para finalizar em outro lugar

# Projeto
## WorkoutAPI

Esta é uma API de competição de crossfit chamada WorkoutAPI. É uma API pequena, devido a ser um projeto mais hands-on e simplificado desenvolvi uma API de poucas tabelas, mas com o necessário para aprender a como utilizar o FastAPI, toda desenvolvida em ambiente windows.

## Modelagem de entidade e relacionamento - MER
![MER](/mer.jpg "Modelagem de entidade e relacionamento")

## Stack da API

A API foi desenvolvida utilizando o `fastapi` (async), junto das seguintes libs: `alembic`, `SQLAlchemy`, `pydantic`. Para salvar os dados está sendo utilizando o `postgres`, por meio do `docker`.

## Execução da API

Para executar o projeto, utilizei a [pyenv-win-venv](https://github.com/pyenv-win/pyenv-win-venv), versão utilizada para ambiente windows, com a versão 3.11.4 do `python` para o ambiente virtual.

Caso opte por usar pyenv, após instalar, execute:

```bash
pyenv-venv install 3.11.4 workoutapi
pyenv-venv activate workoutapi
pip install -r requirements.txt
```
Para subir o banco de dados, caso não tenha o [docker-compose](https://docs.docker.com/desktop/install/windows-install/) instalado, faça a instalação e logo em seguida, execute:

```bash
docker-compose up -d
```
Para criar uma migration nova, execute:

```bash
make create-migrations d="nome_da_migration"
```

Para criar o banco de dados, execute:

```bash
make run-migrations
```

## API

Para subir a API, execute:
```bash
make run
```
e acesse: http://127.0.0.1:8000/docs

# Referências

FastAPI: https://fastapi.tiangolo.com/

Pydantic: https://docs.pydantic.dev/latest/

SQLAlchemy: https://docs.sqlalchemy.org/en/20/

Alembic: https://alembic.sqlalchemy.org/en/latest/

Fastapi-pagination: https://uriyyo-fastapi-pagination.netlify.app/