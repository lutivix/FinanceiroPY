# Tratamento de Dados Bancários (Extração via Texto)

Esta pasta contém a documentação e mapeamento da nova estratégia de extração de dados bancários via texto (Copiar/Colar) da interface web do Itaú, em substituição às APIs pagas (Pluggy/Plaid) e exportações de Excel descontinuadas.

## Estrutura de Arquivos Planejada

Serão utilizados arquivos `.txt` (texto puro) divididos por cartão/portador.
Os arquivos precisam obrigatoriamente começar com o mês de compensação (formato `YYYYMM_`):

**Itaú Master (1 arquivo):**
- `202604_master_luciano.txt` (exemplo para Abril/2026)

**Latam Visa (3 arquivos):**
- `202604_visa_luciano.txt`
- `202604_visa_bia.txt`
- `202604_visa_mae.txt`

## Mapeamento do Formato (Input)

O texto copiado da tela da fatura em aberto possui o seguinte padrão base:
`[Data] [Descrição] [Sinal/Moeda] [Valor]`

### Variações e Casos Especiais

**1. Transação Simples**
```text
16 abr.	dl*uberrides virtual	R$ 15,99
```
- Data: `16 abr.`
- Descrição: `dl*uberrides`
- Tipo: `virtual` (implícito no fim da descrição)
- Valor: `15,99`

**2. Transação Parcelada (Multi-linha)**
```text
20 nov.	gatabakana 05/06 virtual	R$ 55,47
parcela 5 de 6
```
- A informação de parcelamento vem na linha seguinte (`parcela X de Y`).
- Será necessário criar lógica de banco de dados para suportar: `indicador_parcelado`, `qtd_parcelas`, `parcela_atual`.

**3. Compra Internacional (Multi-linha)**
```text
24 mar.	virtual racing school virtual	R$ 27,84 • US$ 4,99
valor da cotação (R$ 5,58)
```
- Traz o valor em Dólar ao lado direito (`• US$ 4,99`).
- A cotação vem na linha de baixo.

**4. Estornos / Pagamentos**
```text
25 mar.	pagamento efetuado	-R$ 10.169,38
24 fev.	be spa urban-ct	-R$ 0,02
```
- Valores negativos contêm o sinal `-` antes da moeda (`-R$`).

## Impactos Conhecidos
- **Perda de Dado:** A flag de compra `recorrente` não é mais informada pelo layout do banco.
- **Mudança de Layout:** Teremos que tratar a quebra de linha (`\n`) que ocorre em compras parceladas e compras internacionais, pois uma única transação pode ocupar 2 linhas de texto.