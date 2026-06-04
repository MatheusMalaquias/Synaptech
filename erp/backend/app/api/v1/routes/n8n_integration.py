"""
Endpoint dedicado para integração com o fluxo n8n.

Fluxo do n8n:
  Google Sheets (Notas + Produtos)
    → Code JS (cruza valor bruto com produto candidato)
    → Loop
    → Final (Produto, Preco_Unit, Quantidade, Valor_Total, Forma_Pagamento)
    → POST /api/v1/n8n/registrar-venda  ← este endpoint

O endpoint faz tudo em uma única chamada:
  1. Autentica via header X-N8N-Secret (sem precisar de JWT)
  2. Encontra ou cria produto pelo nome
  3. Usa sessão de caixa aberta (ou cria uma automática se não existir)
  4. Cria a venda, adiciona o item e finaliza com pagamento
"""
import logging
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.integrations.n8n.webhook_worker import enfileirar_evento
from app.models.base import FormaPagamento, StatusPagamento, StatusVenda
from app.models.caixa import Caixa, SessaoCaixa
from app.models.estoque import Estoque
from app.models.produto import Produto
from app.models.usuario import Usuario
from app.models.venda import ItemVenda, PagamentoVenda, Venda
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.caixa_repo import CaixaRepository
from app.repositories.estoque_repo import EstoqueRepository
from app.repositories.venda_repo import VendaRepository

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

# Mapeamento de formas de pagamento do n8n → enum ERP
MAPA_FORMA_PAGAMENTO: dict[str, FormaPagamento] = {
    # Variações comuns vindas do Google Sheets / Fantastsoft
    "pix": FormaPagamento.pix,
    "pix dinâmico": FormaPagamento.pix,
    "pix dinamico": FormaPagamento.pix,
    "dinheiro": FormaPagamento.dinheiro,
    "espécie": FormaPagamento.dinheiro,
    "especie": FormaPagamento.dinheiro,
    "crédito": FormaPagamento.credito,
    "credito": FormaPagamento.credito,
    "cartão crédito": FormaPagamento.credito,
    "cartao credito": FormaPagamento.credito,
    "débito": FormaPagamento.debito,
    "debito": FormaPagamento.debito,
    "cartão débito": FormaPagamento.debito,
    "cartao debito": FormaPagamento.debito,
    "cheque": FormaPagamento.cheque,
    "voucher": FormaPagamento.voucher,
    "troca": FormaPagamento.troca,
    "caderneta": FormaPagamento.caderneta,
    "fiado": FormaPagamento.caderneta,
}


def _mapear_forma(forma_raw: str) -> FormaPagamento:
    """Converte a string de forma de pagamento do n8n para o enum do ERP."""
    chave = forma_raw.strip().lower()
    return MAPA_FORMA_PAGAMENTO.get(chave, FormaPagamento.pix)  # default: pix


class RegistrarVendaN8NRequest(BaseModel):
    """Payload enviado pelo nó 'Final' do workflow n8n."""
    Produto: str = Field(..., description="Nome do produto (exatamente como na planilha)")
    Preco_Unit: float = Field(..., gt=0, description="Preço unitário em reais")
    Quantidade: float = Field(..., gt=0, description="Quantidade (3 casas decimais para KG)")
    Valor_Total: float = Field(..., gt=0, description="Valor bruto da nota")
    Forma_Pagamento: str = Field(..., description="Forma de pagamento (Pix, Dinheiro, etc.)")


class RegistrarVendaN8NResponse(BaseModel):
    sucesso: bool
    venda_id: str
    numero: int
    produto: str
    quantidade: str
    preco_unitario: str
    subtotal: str
    total_final: str
    forma_pagamento: str
    mensagem: str


async def _autenticar_n8n(x_n8n_secret: Optional[str] = Header(None, alias="X-N8N-Secret")):
    """Valida o secret compartilhado entre n8n e ERP."""
    if not settings.N8N_WEBHOOK_SECRET:
        # Se não há secret configurado, aceita (modo dev)
        return
    if x_n8n_secret != settings.N8N_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Secret n8n inválido",
        )


async def _obter_ou_criar_usuario_n8n(db: AsyncSession) -> Usuario:
    """Retorna o usuário de serviço do n8n (ou cria na primeira execução)."""
    result = await db.execute(
        select(Usuario).where(Usuario.email == "n8n@sistema.interno")
    )
    usuario = result.scalar_one_or_none()
    if not usuario:
        from app.core.security import hash_senha
        import secrets
        usuario = Usuario(
            nome="Integração n8n",
            email="n8n@sistema.interno",
            senha_hash=hash_senha(secrets.token_hex(32)),
            perfil="admin",
        )
        db.add(usuario)
        await db.flush()
        logger.info("Usuário de serviço n8n criado: %s", usuario.id)
    return usuario


async def _obter_ou_criar_sessao(db: AsyncSession, usuario: Usuario) -> SessaoCaixa:
    """
    Retorna uma sessão de caixa aberta.
    Se não existir nenhuma, cria automaticamente um caixa padrão e abre a sessão.
    """
    caixa_repo = CaixaRepository(db)

    # Procura qualquer sessão aberta
    sessao = await caixa_repo.sessao_aberta_qualquer()
    if sessao:
        return sessao

    # Cria ou recupera o caixa padrão do n8n
    result = await db.execute(select(Caixa).where(Caixa.nome == "Caixa n8n"))
    caixa = result.scalar_one_or_none()
    if not caixa:
        caixa = Caixa(nome="Caixa n8n", serie_nfce="01")
        db.add(caixa)
        await db.flush()
        logger.info("Caixa padrão n8n criado: %s", caixa.id)

    sessao = SessaoCaixa(
        caixa_id=caixa.id,
        usuario_id=usuario.id,
        valor_abertura=Decimal("0.00"),
    )
    db.add(sessao)
    await db.flush()
    logger.info("Sessão automática n8n aberta: %s", sessao.id)
    return sessao


async def _obter_ou_criar_produto(db: AsyncSession, nome: str, preco: Decimal) -> Produto:
    """
    Busca produto pelo nome (case-insensitive).
    Se não encontrar, cria automaticamente com o preço recebido.
    """
    nome_upper = nome.strip().upper()
    result = await db.execute(
        select(Produto).where(
            Produto.descricao == nome_upper,
            Produto.ativo == True,
        )
    )
    produto = result.scalar_one_or_none()

    if not produto:
        # Tenta busca parcial (LIKE)
        result = await db.execute(
            select(Produto).where(
                Produto.descricao.ilike(f"%{nome_upper}%"),
                Produto.ativo == True,
            ).limit(1)
        )
        produto = result.scalar_one_or_none()

    if not produto:
        # Cria o produto automaticamente
        produto = Produto(
            descricao=nome_upper,
            unidade="UN",
            preco_venda=preco,
            tributado=True,
            perc_icms=Decimal("18.00"),
        )
        db.add(produto)
        await db.flush()

        # Cria registro de estoque zerado
        estoque = Estoque(produto_id=produto.id, quantidade=Decimal("0"))
        db.add(estoque)
        await db.flush()
        logger.info("Produto criado automaticamente pelo n8n: %s (id=%s)", nome_upper, produto.id)

    return produto


@router.post(
    "/registrar-venda",
    response_model=RegistrarVendaN8NResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar venda vinda do n8n",
)
async def registrar_venda_n8n(
    body: RegistrarVendaN8NRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(_autenticar_n8n),
):
    """
    Endpoint dedicado para o workflow n8n registrar uma venda no ERP.

    Recebe o payload do nó **Final** do workflow n8n:
    - Produto, Preco_Unit, Quantidade, Valor_Total, Forma_Pagamento

    Executa automaticamente:
    1. Resolve usuário de serviço n8n
    2. Encontra/cria sessão de caixa
    3. Encontra/cria produto pelo nome
    4. Cria venda → adiciona item → finaliza com pagamento
    5. Dá baixa no estoque
    6. Dispara webhook venda_finalizada

    **Autenticação:** header `X-N8N-Secret: <seu_secret>`
    """
    try:
        preco = Decimal(str(round(body.Preco_Unit, 2)))
        quantidade = Decimal(str(round(body.Quantidade, 3)))
        valor_total = Decimal(str(round(body.Valor_Total, 2)))
    except InvalidOperation as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Valor numérico inválido: {e}")

    forma = _mapear_forma(body.Forma_Pagamento)

    # 1. Usuário de serviço n8n
    usuario = await _obter_ou_criar_usuario_n8n(db)

    # 2. Sessão de caixa (abre automaticamente se necessário)
    sessao = await _obter_ou_criar_sessao(db, usuario)

    # 3. Produto
    produto = await _obter_ou_criar_produto(db, body.Produto, preco)

    # 4. Cria venda
    venda_repo = VendaRepository(db)
    numero = await venda_repo.proximo_numero()
    venda = Venda(
        numero=numero,
        serie="01",
        sessao_caixa_id=sessao.id,
        usuario_id=usuario.id,
    )
    venda = await venda_repo.criar(venda)

    # 5. Adiciona item — subtotal = ROUND(quantidade × preco, 2)
    subtotal = round(quantidade * preco, 2)
    item = ItemVenda(
        venda_id=venda.id,
        produto_id=produto.id,
        sequencia=1,
        quantidade=quantidade,
        preco_unitario=preco,
        subtotal=subtotal,
        unidade=produto.unidade,
        tributado=produto.tributado,
        perc_icms=produto.perc_icms,
    )
    db.add(item)
    await db.flush()

    # Atualiza totais da venda
    venda.subtotal = subtotal
    venda.total_final = subtotal

    # 6. Finaliza a venda
    pagamento = PagamentoVenda(
        venda_id=venda.id,
        forma=forma,
        valor=valor_total,  # usa o valor bruto original da nota
        status=StatusPagamento.confirmado,
        confirmado_em=datetime.now(timezone.utc),
    )
    db.add(pagamento)

    venda.status = StatusVenda.finalizada
    venda.finalizado_em = datetime.now(timezone.utc)
    await db.flush()

    # 7. Baixa de estoque (pode ficar negativo — regra de negócio)
    estoque_repo = EstoqueRepository(db)
    try:
        await estoque_repo.registrar_movimentacao(
            produto_id=produto.id,
            tipo="saida",
            quantidade=quantidade,
            usuario_id=usuario.id,
            motivo=f"Importação n8n — venda #{numero}",
            referencia_id=venda.id,
            referencia_tipo="venda",
        )
    except ValueError as e:
        logger.warning("Erro ao baixar estoque (produto %s): %s", produto.id, e)

    # 8. Auditoria
    audit = AuditoriaRepository(db)
    await audit.registrar(
        acao="venda_n8n",
        usuario_id=usuario.id,
        tabela="vendas",
        registro_id=str(venda.id),
        dados_depois={
            "numero": numero,
            "produto": produto.descricao,
            "quantidade": str(quantidade),
            "total_final": str(subtotal),
            "forma_pagamento": forma.value,
        },
    )

    # 9. Webhook venda_finalizada
    await enfileirar_evento(db, "venda_finalizada", {
        "evento": "venda_finalizada",
        "origem": "n8n",
        "venda": {
            "id": str(venda.id),
            "numero": numero,
            "serie": "01",
            "itens": [{
                "sequencia": 1,
                "produto_id": produto.id,
                "descricao": produto.descricao,
                "unidade": str(produto.unidade.value if hasattr(produto.unidade, 'value') else produto.unidade),
                "quantidade": str(quantidade),
                "preco_unitario": str(preco),
                "subtotal": str(subtotal),
            }],
            "pagamentos": [{"forma": forma.value, "valor": str(valor_total)}],
            "subtotal": str(subtotal),
            "desconto": "0.00",
            "total_final": str(subtotal),
            "finalizado_em": venda.finalizado_em.isoformat(),
        },
    })

    logger.info(
        "Venda n8n registrada: #%d produto=%s qtd=%s total=%s forma=%s",
        numero, produto.descricao, quantidade, subtotal, forma.value,
    )

    return RegistrarVendaN8NResponse(
        sucesso=True,
        venda_id=str(venda.id),
        numero=numero,
        produto=produto.descricao,
        quantidade=str(quantidade),
        preco_unitario=str(preco),
        subtotal=str(subtotal),
        total_final=str(subtotal),
        forma_pagamento=forma.value,
        mensagem=f"Venda #{numero} registrada com sucesso",
    )
