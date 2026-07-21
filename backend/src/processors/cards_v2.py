"""
Processador para o novo layout de fatura Itaú/Latam (colunas estruturadas)
===========================================================================

Formato novo, distinto do antigo (colunas A/B com marcador "FINAL"): a planilha
já vem com colunas nomeadas — Data, Lançamento, Parcelamento, Valor, Cotação,
Titularidade, Nome, Tipo do cartão, Número do cartão.

Este processor é isolado do `cards.py` (formato antigo) de propósito: a
seleção de qual processor trata um arquivo é feita por DETECÇÃO DE CABEÇALHO
(procura por "Titularidade"/"Parcelamento" nas primeiras linhas), não só pelo
nome do arquivo — isso evita que um arquivo no formato novo seja processado
por engano pelo parser antigo (que não tem como reconhecer a diferença só
pelo nome "Itau"/"Latam.xls(x)").
"""

import re
import logging
from typing import List, Optional, Tuple
from pathlib import Path

import pandas as pd

from .base import BaseProcessor
from models import Transaction, TransactionCategory, TransactionSource, get_card_source

logger = logging.getLogger(__name__)

# Países observados nos dados reais até agora. Ampliar esta lista conforme
# novos destinos apareçam nas faturas (mantida pequena de propósito: uma
# lista grande demais aumenta risco de falso-positivo ao "adivinhar" o país
# em descrições sem localização, ex.: uma palavra em português terminando
# coincidentemente em 2 letras que batam com um código de país obscuro).
PAISES_CONHECIDOS = {"BR", "US", "ES"}

_PARCELA_RE = re.compile(r"Parcela\s+(\d+)\s+de\s+(\d+)", re.IGNORECASE)
_COTACAO_RE = re.compile(
    r"([A-Za-z]{3})\s*([\d\.,]+).*?cota[çc][ãa]o\s*R\$\s*([\d\.,]+)",
    re.IGNORECASE | re.DOTALL,
)


def _parse_valor_br(texto: str) -> Optional[float]:
    """Converte '1.190,10' -> 1190.10"""
    if not texto:
        return None
    limpo = texto.strip().replace(".", "").replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        return None


class CardStatementV2Processor(BaseProcessor):
    """
    Processador para o novo layout estruturado de fatura (Itaú Master e Latam
    Visa compartilham o mesmo layout — o que muda é o nome do arquivo/banco).
    """

    def __init__(self, bank_name: str):
        super().__init__(f"Cartão {bank_name} (novo formato)")
        self.bank_name = bank_name.lower()

    # ------------------------------------------------------------------
    # Detecção de arquivo
    # ------------------------------------------------------------------
    def can_process(self, file_path: Path) -> bool:
        if file_path.suffix.lower() not in [".xls", ".xlsx"]:
            return False
        if self.bank_name.title() not in file_path.name:
            return False
        return self._find_header_row(file_path) is not None

    def _find_header_row(self, file_path: Path) -> Optional[int]:
        """Procura a linha de cabeçalho ('Titularidade' + 'Parcelamento')."""
        try:
            df = pd.read_excel(file_path, header=None, nrows=30)
        except Exception:
            return None

        for i in range(len(df)):
            valores = [str(v) for v in df.iloc[i].values if pd.notna(v)]
            if "Titularidade" in valores and "Parcelamento" in valores:
                return i
        return None

    # ------------------------------------------------------------------
    # Processamento
    # ------------------------------------------------------------------
    def process_file(self, file_path: Path) -> List[Transaction]:
        if not self.validate_file(file_path):
            return []

        self.log_processing_start(file_path)
        transactions: List[Transaction] = []
        month_ref = self.extract_month_reference(file_path)

        # Extrai mes_comp do nome do arquivo (formato: 202607_Latam_nova.xlsx -> 2026-07)
        mes_comp = ""
        apenas_numeros = "".join(filter(str.isdigit, file_path.stem))
        if len(apenas_numeros) >= 6:
            mes_comp = f"{apenas_numeros[:4]}-{apenas_numeros[4:6]}"

        try:
            df = pd.read_excel(file_path, header=None)
            header_row = self._find_header_row(file_path)
            if header_row is None:
                self.stats.add_error(f"Cabeçalho não encontrado em {file_path.name}")
                return []

            for i in range(header_row + 1, len(df)):
                row = df.iloc[i]

                data_raw = row[1]
                if pd.isna(data_raw):
                    # Linha em branco logo após o cabeçalho ou pós-lançamentos
                    # (ex.: linha "Subtotal") -> fim dos lançamentos.
                    break

                descricao_raw = row[2]
                parcelamento_raw = row[3]
                valor_raw = row[4]
                cotacao_raw = row[5]
                titularidade_raw = row[6]
                nome_raw = row[7]
                tipo_cartao_raw = row[8]
                numero_cartao_raw = row[9]

                descricao = str(descricao_raw).strip() if pd.notna(descricao_raw) else ""
                valor = pd.to_numeric(valor_raw, errors="coerce")

                if self.should_skip_transaction(descricao, valor if pd.notna(valor) else 0):
                    continue
                if pd.isna(valor) or valor == 0:
                    continue

                data = pd.to_datetime(data_raw, errors="coerce")
                if pd.isna(data):
                    continue
                data = data.date()

                parcela_atual, qtd_parcelas = self._parse_parcelamento(parcelamento_raw)
                moeda, valor_moeda, cotacao = self._parse_cotacao(cotacao_raw)
                descricao_limpa, pais, local_site = self._parse_local(descricao)

                numero_cartao = str(numero_cartao_raw).strip() if pd.notna(numero_cartao_raw) else ""
                card_final = "".join(filter(str.isdigit, numero_cartao))[-4:] if numero_cartao else None
                source = (
                    get_card_source(card_final, self.bank_name)
                    if card_final
                    else (
                        TransactionSource.ITAU_MASTER_VIRTUAL
                        if self.bank_name == "itau"
                        else TransactionSource.LATAM_VISA_VIRTUAL
                    )
                )

                titularidade = str(titularidade_raw).strip() if pd.notna(titularidade_raw) else None
                nome_titular = str(nome_raw).strip() if pd.notna(nome_raw) else None
                tipo_cartao_raw_texto = str(tipo_cartao_raw).strip() if pd.notna(tipo_cartao_raw) else None

                transaction = Transaction(
                    date=data,
                    description=descricao_limpa or descricao,
                    amount=float(valor),
                    source=source,
                    category=TransactionCategory.A_DEFINIR,
                    month_ref=month_ref,
                    mes_comp=mes_comp,
                    raw_data={
                        "original_description": descricao,
                        "file_source": str(file_path),
                        "bank": self.bank_name,
                        "card_final": card_final,
                        "parcela_atual": parcela_atual,
                        "qtd_parcelas": qtd_parcelas,
                        "titularidade": titularidade,
                        "nome_titular": nome_titular,
                        "tipo_cartao_raw": tipo_cartao_raw_texto,
                        "numero_cartao": numero_cartao or None,
                        "cotacao": cotacao,
                        "moeda_estrangeira": moeda,
                        "valor_moeda_estrangeira": valor_moeda,
                        "pais": pais,
                        "local_site": local_site,
                    },
                )
                transactions.append(transaction)

            self.stats.files_processed += 1
            self.stats.transactions_extracted += len(transactions)
            self.log_processing_end(len(transactions))

        except Exception as e:
            error_msg = f"Erro ao processar {file_path}: {e}"
            self.stats.add_error(error_msg)
            logger.error(f"❌ [{self.source_name}] {error_msg}")

        return transactions

    # ------------------------------------------------------------------
    # Parsers auxiliares
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_parcelamento(valor) -> Tuple[Optional[int], Optional[int]]:
        if pd.isna(valor):
            return None, None
        m = _PARCELA_RE.search(str(valor))
        if not m:
            return None, None
        return int(m.group(1)), int(m.group(2))

    @staticmethod
    def _parse_cotacao(valor) -> Tuple[Optional[str], Optional[float], Optional[float]]:
        """
        Extrai moeda/valor estrangeiro/cotação de textos como:
        'USD\xa04,99 \n(cotação R$\xa05,51)'
        """
        if pd.isna(valor):
            return None, None, None
        texto = str(valor)
        m = _COTACAO_RE.search(texto)
        if not m:
            return None, None, None
        moeda = m.group(1).upper()
        valor_moeda = _parse_valor_br(m.group(2))
        cotacao = _parse_valor_br(m.group(3))
        return moeda, valor_moeda, cotacao

    @staticmethod
    def _parse_local(descricao: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Separa país (e, quando possível, cidade/site) do final da descrição.

        Limitação conhecida: o banco não usa um delimitador confiável entre
        estabelecimento/cidade/país — em vários casos os campos ficam colados
        sem espaço (ex.: "netflix.comsao paulobr"). Nesses casos só o país é
        extraído com segurança; cidade fica None. Aceito por decisão do
        usuário (campo pode ser nulo).
        """
        if not descricao:
            return descricao, None, None

        texto = descricao.strip()
        partes = re.split(r"\s{2,}", texto)

        if len(partes) >= 2 and partes[-1].strip().upper() in PAISES_CONHECIDOS:
            pais = partes[-1].strip().upper()
            if len(partes) >= 3:
                local_site = partes[-2].strip()
                merchant = " ".join(partes[:-2]).strip()
            else:
                local_site = None
                merchant = " ".join(partes[:-1]).strip()
            return (merchant or texto), pais, local_site

        # Fallback: sem espaçamento separador (campos colados)
        if len(texto) >= 4 and texto[-2:].upper() in PAISES_CONHECIDOS:
            pais = texto[-2:].upper()
            merchant = texto[:-2].strip()
            return (merchant or texto), pais, None

        return texto, None, None
