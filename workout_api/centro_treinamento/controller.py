from uuid import uuid4
from fastapi import APIRouter, Body, status, HTTPException
from fastapi_pagination import LimitOffsetPage, paginate
from pydantic import UUID4
from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut, CentroTreinamentoUpdate
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

router = APIRouter()

@router.post(
        path='/',
        summary='Criar um novo Centro de treinamento',
        status_code=status.HTTP_201_CREATED,
        response_model=CentroTreinamentoOut,
)

async def post(
    db_session: DatabaseDependency,
    centro_treinamento_in: CentroTreinamentoIn = Body(...)
) -> CentroTreinamentoOut:
    
    centro_treinamento_nome = centro_treinamento_in.nome
    centro_treinamento = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome))
    ).scalars().first()
    
    if centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f'Categoria com mesmo nome: {centro_treinamento_nome}'
        )

    centro_treinamento_out = CentroTreinamentoOut(id=uuid4(), **centro_treinamento_in.model_dump())
    centro_treinamento_model = CentroTreinamentoModel(**centro_treinamento_out.model_dump())

    db_session.add(centro_treinamento_model)
    await db_session.commit()
    
    return centro_treinamento_out

@router.get(
        path='/',
        summary='Consultar todos os centros de treinamento',
        status_code=status.HTTP_200_OK,
        response_model=LimitOffsetPage[CentroTreinamentoOut],
)

async def query(db_session: DatabaseDependency) -> LimitOffsetPage[CentroTreinamentoOut]:
    centros_treinamento_out: list[CentroTreinamentoOut] = (
        await db_session.execute(select(CentroTreinamentoModel))
    ).scalars().all()
    
    return paginate(centros_treinamento_out)

@router.get(
        path='/{id}',
        summary='Consulta um centro de treinamento pelo id',
        status_code=status.HTTP_200_OK,
        response_model=CentroTreinamentoOut,
)

async def get(id: UUID4, db_session: DatabaseDependency) -> CentroTreinamentoOut:
    centro_treinamento: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
    ).scalars().first()
    
    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Centro de treinamento não encontrado no id: {id}'
        )

    return centro_treinamento

@router.patch(
        path='/{id}',
        summary='Editar um centro de treinamento pelo id',
        status_code=status.HTTP_200_OK,
        response_model=CentroTreinamentoOut,
)

async def patch(
    id: UUID4,
    db_session: DatabaseDependency,
    centro_treinamento_up: CentroTreinamentoUpdate = Body(...)
) -> CentroTreinamentoOut:
    
    centro_treinamento: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
    ).scalars().first()
    
    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Centro de Treinamento não encontrada no id: {id}'
        )
    
    centro_treinamento_update = centro_treinamento_up.model_dump(exclude_unset=True)
    for key, value in centro_treinamento_update.items():
        setattr(centro_treinamento, key, value)
    
    await db_session.commit()
    await db_session.refresh(centro_treinamento)

    return centro_treinamento

@router.delete(
        path='/{id}',
        summary='Deletar um centro de treinamento pelo id',
        status_code=status.HTTP_204_NO_CONTENT
)

async def delete(id: UUID4, db_session: DatabaseDependency) -> None:
    centro_treinamento: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
    ).scalars().first()
    
    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Centro de treinamento não encontrado no id: {id}'
        )
    
    await db_session.delete(centro_treinamento)
    await db_session.commit()