import json
import re
from pathlib import Path

BASE_PATH = Path('.')
CHAINS_PATH = BASE_PATH / 'blockchains'
EXPORT_DIR_PATH = BASE_PATH / 'export data'

CHAINS = ['ethereum', 'polygon', 'tron']

TRON_WALLET_FORMAT_RE = r'^(0x41[a-fA-F0-9]{40})|(T[a-km-zA-HJ-NP-Z1-9]{33})$'
ETH_WALLET_FORMAT_RE = r'^0x[a-fA-F0-9]{40}$'
ADDRESS_VALIDATORS = {
    'ethereum': ETH_WALLET_FORMAT_RE,
    'polygon': ETH_WALLET_FORMAT_RE,
    'tron': TRON_WALLET_FORMAT_RE,
}

def run():
    for chain in CHAINS:
        results = {}
        addrs_dir = CHAINS_PATH / chain / 'assets'
        for p in Path(addrs_dir).iterdir():
            if p.is_dir():
                if not re.match(ADDRESS_VALIDATORS[chain], p.name):
                    continue
                with open(p / 'info.json', 'r') as info:
                    try:
                        raw_data = info.read()
                        data = json.loads(raw_data)
                    except json.decoder.JSONDecodeError as err:
                        print(p.name, err, '\nFile content was:\n', raw_data)
                results[data['id']] = {
                    'name': data['name'],
                    'symbol': data['symbol'],
                    'website': data['website'] or None,
                    'status': data['status'],
                }

        print(chain, len(results))

        EXPORT_DIR_PATH.mkdir(parents=True, exist_ok=True)
        with open(EXPORT_DIR_PATH / f'{chain.upper()}_results.json', 'w') as f:
            f.write(json.dumps(results, indent=4))


if __name__ == '__main__':
    run()
