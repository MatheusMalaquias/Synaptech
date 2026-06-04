"""Enums compartilhados entre os modelos."""
import enum


class UnidadeEnum(str, enum.Enum):
    KG = "KG"
    UN = "UN"
    L = "L"
    CX = "CX"
    PC = "PC"
    DZ = "DZ"


class PerfilUsuario(str, enum.Enum):
    admin = "admin"
    gerente = "gerente"
    caixa = "caixa"


class StatusVenda(str, enum.Enum):
    aberta = "aberta"
    finalizada = "finalizada"
    cancelada = "cancelada"


class StatusNfce(str, enum.Enum):
    pendente = "pendente"
    emitida = "emitida"
    rejeitada = "rejeitada"
    cancelada = "cancelada"


class FormaPagamento(str, enum.Enum):
    dinheiro = "dinheiro"
    credito = "credito"
    debito = "debito"
    pix = "pix"
    cheque = "cheque"
    voucher = "voucher"
    troca = "troca"
    caderneta = "caderneta"


class StatusPagamento(str, enum.Enum):
    pendente = "pendente"
    confirmado = "confirmado"
    rejeitado = "rejeitado"
    estornado = "estornado"


class TipoMovimentacao(str, enum.Enum):
    entrada = "entrada"
    saida = "saida"
    ajuste_positivo = "ajuste_positivo"
    ajuste_negativo = "ajuste_negativo"
    cancelamento = "cancelamento"


class StatusSessaoCaixa(str, enum.Enum):
    aberta = "aberta"
    fechada = "fechada"


class WebhookStatus(str, enum.Enum):
    pendente = "pendente"
    enviando = "enviando"
    entregue = "entregue"
    falhou = "falhou"
