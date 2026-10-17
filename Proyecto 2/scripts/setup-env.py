"""Crea credenciales locales sin imprimirlas ni sobrescribir un .env existente."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parents[1]
text = (root / '.env.example').read_text()
for key in ('MSSQL_SA_PASSWORD', 'DB_PASSWORD', 'IMPORT_DB_PASSWORD', 'IMPORT_KEY'):
    lines = text.splitlines()
    text = '\n'.join(f'{key}=Bd1_{secrets.token_hex(24)}!' if line.startswith(key + '=') else line for line in lines) + '\n'
with (root / '.env').open('x') as stream:
    stream.write(text)
(root / '.env').chmod(0o600)
print('Credenciales creadas en .env (no versionar).')
