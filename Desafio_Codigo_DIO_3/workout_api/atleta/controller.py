from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Body, status, HTTPException
from fastapi_pagination import LimitOffsetPage, paginate
from pydantic import UUID4
from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate, AtletaOne, AtletaAll
from workout_api.atleta.models import AtletaModel
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

router = APIRouter()

@router.post(
        path='/',
        summary='Criar um novo atleta',
        status_code=status.HTTP_201_CREATED,
        response_model=AtletaOut
)

async def post(
    db_session: DatabaseDependency,
    atleta_in: AtletaIn = Body(...)
):

    categoria_nome = atleta_in.categoria.nome
    categoria = (await db_session.execute(
        select(CategoriaModel).filter_by(nome=categoria_nome))
    ).scalars().first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'A categoria {categoria_nome} não foi encontrada.'
        )
    
    centro_treinamento_nome = atleta_in.centro_treinamento.nome
    centro_treinamento = (await db_session.execute(
        select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome))
    ).scalars().first()

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'O centro de treinamento {centro_treinamento_nome} não foi encontrado.'
        )
    
    atleta_cpf = atleta_in.cpf
    atleta = (await db_session.execute(
        select(AtletaModel).filter_by(cpf=atleta_cpf))
    ).scalars().first()

    if atleta:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f'Já existe um atleta cadastrado com o cpf: {atleta_cpf}'
        )
    
    try:
        atleta_out = AtletaOut(id=uuid4(), create_at=datetime.utcnow(), **atleta_in.model_dump())
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id

        db_session.add(atleta_model)
        await db_session.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Ocorreu um erro ao inserir os dados no banco'
        )

    return atleta_out

@router.get(
        path='/',
        summary='Consultar todos os Atletas',
        status_code=status.HTTP_200_OK,
        response_model=LimitOffsetPage[AtletaAll]
)

async def query(
    db_session: DatabaseDependency
) -> LimitOffsetPage[AtletaAll]:
    atletas: list[AtletaAll] = (await db_session.execute(select(AtletaModel))).scalars().all()

    atletas2 = [AtletaAll.model_validate(atleta) for atleta in atletas]

    return paginate(atletas2)

@router.get(
        path='/{nome}',
        summary='Consulta um atleta pelo nome',
        status_code=status.HTTP_200_OK,
        response_model=AtletaOne,
)

async def get(nome: str, db_session: DatabaseDependency) -> AtletaOne:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(nome=nome))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Atleta não encontrado com nome: {nome}'
        )
    
    atleta_model = AtletaOne(nome=atleta.nome, cpf=atleta.cpf)

    return atleta_model
    
@router.patch(
        path='/{nome}',
        summary='Editar um atleta pelo nome',
        status_code=status.HTTP_200_OK,
        response_model=AtletaOut,
)

async def patch(nome: str, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)) -> AtletaOut:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(nome=nome))
    ).scalars().first()
    
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Atleta não encontrado com nome: {nome}'
        )
    
    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)
    
    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta

@router.delete(
        path='/{nome}',
        summary='Deletar um atleta pelo nome',
        status_code=status.HTTP_204_NO_CONTENT
)

async def delete(nome: str, db_session: DatabaseDependency) -> None:
    atleta: AtletaOut = (
        await db_session.execute(select(AtletaModel).filter_by(nome=nome))
    ).scalars().first()
    
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Atleta não encontrado com nome: {nome}'
        )
    
    await db_session.delete(atleta)
    await db_session.commit()