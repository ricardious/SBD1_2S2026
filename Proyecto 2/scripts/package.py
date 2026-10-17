"""Empaqueta una entrega reproducible y excluye secretos y artefactos locales."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
out = root / 'entrega' / '[BD1]_ProyectoFase2_202300476.zip'
out.parent.mkdir(exist_ok=True)
excluded = {'node_modules', 'dist', 'entrega', '.git', '__pycache__', 'coverage'}
with ZipFile(out, 'w', ZIP_DEFLATED) as archive:
    for file in sorted(root.rglob('*')):
        relative = file.relative_to(root)
        if not file.is_file() or any(part in excluded for part in relative.parts):
            continue
        if (file.name.startswith('.env') and file.name != '.env.example') or file.suffix == '.log':
            continue
        archive.write(file, relative.as_posix())
with ZipFile(out) as archive:
    assert archive.testzip() is None
    assert 'init.sql' in archive.namelist() and 'docker-compose.yml' in archive.namelist()
    assert '.env' not in archive.namelist()
print(f'Entrega creada y verificada: {out.name}')
