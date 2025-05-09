from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import date

class LivroBase(BaseModel):
    titulo: str
    autor: str
    ano_publicacao: int

class Livro(LivroBase):
    id: UUID = Field(default_factory=uuid4)
    disponivel: bool = True

class UsuarioBase(BaseModel):
    nome: str

class Usuario(UsuarioBase):
    id: UUID = Field(default_factory=uuid4)
    livros_emprestados: List[UUID] = []

class Emprestimo(BaseModel):
    id_usuario: UUID
    id_livro: UUID
    data_emprestimo: date
    data_devolucao: Optional[date] = None
