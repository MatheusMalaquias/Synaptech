"""
Importa todos os modelos para que o Alembic os descubra via Base.metadata.
"""
from app.models.auditoria import AuditoriaLog  # noqa
from app.models.caixa import Caixa, SessaoCaixa  # noqa
from app.models.cliente import Cliente  # noqa
from app.models.configuracao import Configuracao  # noqa
from app.models.estoque import Estoque, MovimentacaoEstoque  # noqa
from app.models.produto import Categoria, Produto  # noqa
from app.models.usuario import Usuario  # noqa
from app.models.venda import ItemVenda, PagamentoVenda, Venda  # noqa
from app.models.webhook import Webhook, WebhookEntrega  # noqa
