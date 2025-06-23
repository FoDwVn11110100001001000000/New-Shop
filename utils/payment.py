import asyncio
from crypto_pay_api_sdk import cryptopay
from utils.logs import log
from env import Config as config


if int(config.testnet):
    testnet_var = True
else:
    testnet_var = False

Crypto = cryptopay.Crypto(token=config.crypto_pay_token, testnet=testnet_var)

async def check_payment(invoice_id, max_attempts=89, sleep_seconds=10):
    attempts = 0
    found_invoice = None

    while attempts <= max_attempts:
        invoices = Crypto.getInvoices().get('result', {}).get('items', [])

        for invoice in invoices:
            if invoice['invoice_id'] == int(invoice_id):
                found_invoice = invoice
                break

        if found_invoice['status'] == 'paid':
            #***Инвойс оплачен успешно***
            log.info(f'Invoice {invoice_id} was paid')
            return True
        elif found_invoice['status'] == 'expired':
            log.info(f'Invoice {invoice_id} was expired')
            #***Инвойс не был оплачен***
            return False
        elif found_invoice['status'] == 'active':
            await asyncio.sleep(sleep_seconds)
            log.info(f'Invoice {invoice_id} is active. Attempts: {attempts}')
            attempts += 1
    log.error(f'Invoice {invoice_id}. Time is over. Invoice wasn`t payed.')
    return False


def create_invoice(amount: float):
    invoice = Crypto.createInvoice(
        config.pay_currency,
        amount,
        params={
            "description": config.channel_name,
            "expires_in": config.invoice_counter
        }
    )
    log.info(f'Invoice was created. Invoice ID: {invoice["result"]["invoice_id"]}')
    return invoice.get('result')
