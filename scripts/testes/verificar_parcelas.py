import json

data = json.load(open('transacoes_itau_3meses.json', encoding='utf-8'))

parceladas = [t for t in data['transacoes'] 
              if t.get('creditCardMetadata') and t['creditCardMetadata'].get('totalInstallments')]

print(f'Transações parceladas: {len(parceladas)}\n')
print('Exemplos de parcelas:')

for i, t in enumerate(parceladas[:10]):
    meta = t['creditCardMetadata']
    print(f"\n{i+1}. {t['description'][:50]}")
    print(f"   Valor: R$ {t['amount']:.2f}")
    print(f"   Data: {t['date'][:10]}")
    print(f"   Parcela: {meta.get('installmentNumber')}/{meta.get('totalInstallments')}")
    print(f"   Compra: {meta.get('purchaseDate', 'N/A')[:10]}")
    print(f"   BillId: {meta.get('billId', 'N/A')}")
    print(f"   Cartão: {meta.get('cardNumber')}")
