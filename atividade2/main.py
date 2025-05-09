from fastapi import FastAPI, HTTPException
from typing import List, Optional
from uuid import UUID

from models import Livro, LivroBase, Usuario, UsuarioBase, Emprestimo

app = FastAPI(title="Biblioteca API")

livros: List[Livro] = []
usuarios: List[Usuario] = []
historico_emprestimos: List[Emprestimo] = []

@app.post("/livros", response_model=Livro)
def cadastrar_livro(livro: LivroBase):
    novo_livro = Livro(**livro.dict())
    livros.append(novo_livro)
    print(f"📚 Livro cadastrado: {novo_livro.titulo} ({novo_livro.id})")
    return novo_livro

@app.get("/livros", response_model=List[Livro])
def listar_livros(disponivel: Optional[bool] = None):
    if disponivel is None:
        return livros
    return [livro for livro in livros if livro.disponivel == disponivel]

@app.get("/livros/busca", response_model=List[Livro])
def buscar_livro_por_titulo(titulo: str):
    resultados = [livro for livro in livros if titulo.lower() in livro.titulo.lower()]
    if not resultados:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return resultados

@app.post("/usuarios", response_model=Usuario)
def cadastrar_usuario(usuario: UsuarioBase):
    novo_usuario = Usuario(**usuario.dict())
    usuarios.append(novo_usuario)
    print(f"👤 Usuário cadastrado: {novo_usuario.nome} ({novo_usuario.id})")
    return novo_usuario

@app.post("/emprestimos")
def emprestar_livro(emprestimo: Emprestimo):
    usuario = next((u for u in usuarios if u.id == emprestimo.id_usuario), None)
    livro = next((l for l in livros if l.id == emprestimo.id_livro), None)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    if not livro.disponivel:
        raise HTTPException(status_code=400, detail="Livro não está disponível")

    livro.disponivel = False
    usuario.livros_emprestados.append(livro.id)
    historico_emprestimos.append(emprestimo)
    print(f"📖 Livro emprestado: {livro.titulo} para {usuario.nome}")
    return {"mensagem": "Empréstimo realizado com sucesso"}

@app.post("/devolucoes")
def devolver_livro(emprestimo: Emprestimo):
    usuario = next((u for u in usuarios if u.id == emprestimo.id_usuario), None)
    livro = next((l for l in livros if l.id == emprestimo.id_livro), None)

    if not usuario or livro.id not in usuario.livros_emprestados:
        raise HTTPException(status_code=400, detail="Empréstimo não encontrado para o usuário")

    livro.disponivel = True
    usuario.livros_emprestados.remove(livro.id)

    for reg in historico_emprestimos:
        if reg.id_usuario == emprestimo.id_usuario and reg.id_livro == emprestimo.id_livro and reg.data_devolucao is None:
            reg.data_devolucao = emprestimo.data_devolucao
            break

    print(f"🔁 Livro devolvido: {livro.titulo} por {usuario.nome}")
    return {"mensagem": "Livro devolvido com sucesso"}

@app.get("/usuarios/{usuario_id}/emprestimos", response_model=List[Livro])
def listar_livros_emprestados_por_usuario(usuario_id: UUID):
    usuario = next((u for u in usuarios if u.id == usuario_id), None)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return [livro for livro in livros if livro.id in usuario.livros_emprestados]

@app.get("/historico", response_model=List[Emprestimo])
def listar_historico_emprestimos():
    return historico_emprestimos
