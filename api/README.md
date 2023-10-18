# Backend for blog

The backend for my blog website

## prerequirements

- poetry
- docker

## libralies

- fastapi
- sqlalchemy
- postgres DB (Database)

## set up db

1.  `cd db`
2.  `Docker-Compose up -d`

## how to raunch server

1.  `poetry install`
2.  `poetry shell`
3.  `uvicorn main:app --reload`
