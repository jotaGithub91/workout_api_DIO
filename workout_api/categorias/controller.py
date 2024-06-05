from uuid import uuid4
from fastapi import APIRouter, HTTPException, Body, status
from fastapi_pagination import LimitOffsetPage, paginate
from pydantic import UUID4
from workout_api.categorias.schemas import CategoriaIn, CategoriaOut
from workout_api.contrib.dependencies import DatabaseDependency
from workout_api.categorias.models import CategoriaModel
from sqlalchemy.future import select

router = APIRouter()

@router.post(
        path='/',
        summary='Criar uma nova Categoria',
        status_code=status.HTTP_201_CREATED,
        response_model=CategoriaOut,
)

async def post(
    db_session: DatabaseDependency,
    categoria_in: CategoriaIn = Body(...)
) -> CategoriaOut:
    
    categoria_nome = categoria_in.nome
    categoria = (await db_session.execute(
        select(CategoriaModel).filter_by(nome=categoria_nome))
    ).scalars().first()
    
    if categoria:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f'Categoria com mesmo nome: {categoria_nome}'
        )

    categoria_out = CategoriaOut(id=uuid4(), **categoria_in.model_dump())
    categoria_model = CategoriaModel(**categoria_out.model_dump())

    db_session.add(categoria_model)
    await db_session.commit()
    
    return categoria_out

@router.get(
        path='/',
        summary='Consultar todas as Categorias',
        status_code=status.HTTP_200_OK,
        response_model=LimitOffsetPage[CategoriaOut],
)

async def query(db_session: DatabaseDependency) -> LimitOffsetPage[CategoriaOut]:
    categorias: list[CategoriaOut] = (await db_session.execute(select(CategoriaModel))).scalars().all()
    
    return paginate(categorias)

@router.get(
        path='/{id}',
        summary='Consulta uma Categoria pelo id',
        status_code=status.HTTP_200_OK,
        response_model=CategoriaOut,
)

async def get(id: UUID4, db_session: DatabaseDependency) -> CategoriaOut:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(id=id))
    ).scalars().first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Categoria não encontrada no id: {id}'
        )

    return categoria

@router.delete(
        path='/{id}',
        summary='Deletar uma categoria pelo id',
        status_code=status.HTTP_204_NO_CONTENT
)

async def delete(id: UUID4, db_session: DatabaseDependency) -> None:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(id=id))
    ).scalars().first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Categoria não encontrada no id: {id}'
        )
    
    await db_session.delete(categoria)
    await db_session.commit()