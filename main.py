import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import SessionLocal, engine

app = FastAPI()

# Cria as tabelas no PostgreSQL (caso não exista) — só falha se o banco não estiver rodando
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    logging.warning(
        "PostgreSQL indisponível: não foi possível criar as tabelas. "
        "Inicie o PostgreSQL em localhost:5432 e reinicie a aplicação. Erro: %s",
        e,
    )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/estudantes', response_model=schemas.EstudanteResponse)

def create_student(
    student: schemas.EstudanteCreate, 
    db:Session = Depends(get_db)):

    db_student = models.Estudante(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@app.get('/estudantes/', response_model=List[schemas.EstudanteResponse])
def read_students(db: Session = Depends(get_db)):
    students = db.query(models.Estudante).all()
    return students


@app.get('/estudantes/{estudante_id}', response_model=schemas.EstudanteResponse)
def read_student(estudante_id: int, db: Session = Depends(get_db)):
    """Retorna um estudante pelo id. 404 se não existir."""
    db_student = db.query(models.Estudante).filter(models.Estudante.id == estudante_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Estudante não encontrado")
    return db_student


@app.get('/estudantes/com-matriculas')
def read_students_with_matriculas(db: Session = Depends(get_db)):
    estudantes = db.query(models.Estudante).all()
    matriculas = db.query(models.Matricula).all()
    resultado = []
    for est in estudantes:
        matriculas_do_estudante = [
            m for m in matriculas
            if m.estudante_id == est.id
        ]
        resultado.append({
            "id": est.id,
            "nome": est.nome,
            "idade": est.idade,
            "matriculas": [
                {"id": m.id, "estudante_id": m.estudante_id, "nome_disciplina": m.nome_disciplina}
                for m in matriculas_do_estudante
            ],
        })
    return resultado


#Criacao de Matriculas referenciando os estudantes
@app.post('/matriculas', response_model=schemas.MatriculaResponse)
def create_matricula(
    matricula: schemas.MatriculaCreate,
    db: Session = Depends(get_db)):
    # Regra de negócio: só permite matrícula se o estudante existir
    estudante = db.query(models.Estudante).filter(models.Estudante.id == matricula.estudante_id).first()
    if estudante is None:
        raise HTTPException(
            status_code=404,
            detail=f"Estudante com id {matricula.estudante_id} não encontrado. Crie o estudante antes de matricular.",
        )
    db_matricula = models.Matricula(**matricula.model_dump())
    db.add(db_matricula)
    db.commit()
    db.refresh(db_matricula)
    return db_matricula


@app.delete('/estudantes/{estudante_id}', status_code=204)
def delete_student(estudante_id: int, db: Session = Depends(get_db)):
    db_student = db.query(models.Estudante).filter(models.Estudante.id == estudante_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Estudante não encontrado")
    # Remove as matrículas do estudante antes (evita violação de chave estrangeira)
    db.query(models.Matricula).filter(models.Matricula.estudante_id == estudante_id).delete()
    db.delete(db_student)
    db.commit()
    return None





