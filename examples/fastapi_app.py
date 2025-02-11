import logging
from abc import abstractmethod
from typing import Annotated, Protocol

import uvicorn
from fastapi import APIRouter, FastAPI

from dishka import (
    Provider, Scope, provide,
)
from dishka.integrations.fastapi import (
    Depends, inject, DishkaApp,
)


# app core
class DbGateway(Protocol):
    @abstractmethod
    def get(self) -> str:
        raise NotImplementedError


class FakeDbGateway(DbGateway):
    def get(self) -> str:
        return "Hello"


class Interactor:
    def __init__(self, db: DbGateway):
        self.db = db

    def __call__(self) -> str:
        return self.db.get()


# app dependency logic
class AdaptersProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_db(self) -> DbGateway:
        return FakeDbGateway()


class InteractorProvider(Provider):
    i1 = provide(Interactor, scope=Scope.REQUEST)


# presentation layer
router = APIRouter()


@router.get("/")
@inject
async def index(
        *,
        interactor: Annotated[Interactor, Depends()],
) -> str:
    result = interactor()
    return result


def create_app():
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s  %(process)-7s %(module)-20s %(message)s',
    )

    app = FastAPI()
    app.include_router(router)
    return DishkaApp(
        providers=[AdaptersProvider(), InteractorProvider()],
        app=app,
    )


if __name__ == "__main__":
    uvicorn.run(create_app(), host="0.0.0.0", port=8000, lifespan="on")
