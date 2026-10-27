from hashlib import sha256
from pathlib import Path


RAW_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
REPORTS_DIR = Path('reports')
ENVIO_DIR = RAW_DIR.parent / 'intercambio' / 'envio'
REFERENCE_FILES = [
    ENVIO_DIR / 'referencia.txt',
    ENVIO_DIR / 'referemcia.txt',  # nombre antiguo que existe en esta copia
]
NAMES = ['partida_A.jsonl', 'partida_B.jsonl']


def checksum(path):
    return sha256(path.read_bytes()).hexdigest()


def read_reference(path):
    references = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[0] in NAMES and parts[1].isdigit():
            references[parts[0]] = {
                'size': int(parts[1]),
                'sha256': parts[2].lower(),
            }
    return references


references = {}
reference_used = None
for candidate in REFERENCE_FILES:
    if candidate.exists():
        candidate_references = read_reference(candidate)
        if set(candidate_references) == set(NAMES):
            references = candidate_references
            reference_used = candidate
            break
if not references:
    raise ValueError('No hay una referencia valida con nombre, tamano y SHA-256 para A y B')

print('Referencia utilizada:', reference_used)
print('RESULTADO DE LA VERIFICACION')
for name in NAMES:
    path = ENVIO_DIR / name
    expected = references[name]
    if not path.exists():
        print(f'{name}: NO RECIBIDO')
        continue
    current_hash = checksum(path)
    current_size = path.stat().st_size
    result = 'COINCIDE' if current_hash == expected['sha256'] else 'NO COINCIDE'
    print(f'\n{name}')
    print('Tamano esperado:', expected['size'])
    print('Tamano recibido:', current_size)
    print('SHA esperado:', expected['sha256'])
    print('SHA calculado:', current_hash)
    print('Resultado:', result)
