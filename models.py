from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base


class Estudante(Base):
    _tablename_ = "estudantes"
    id = Column(
        Integer,
        primary_key=True,
        index=True)
    nome = Column(
        String(100),
        nullable=False)
    idade = Column(
        Integer, nullable=False)


class Matricula(Base):
    __table_name__ = "matriculas"
    id = Column(
        Integer, 
        primary_key=True, 
        Index=True)
    estudante_id = Column(
        Integer,
        ForeignKey("estudante.id"))
