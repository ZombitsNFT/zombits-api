import subprocess
import glob

ADDRESS = 'addr1v8hzad0cqqxmklk9ckea0sxmfgzpul2anmypacycvh6l3hsstd0rs'
POLICY_ID = 'ad6290066292cfeef7376cd575e5d8367833ab3d8b2ac53d26ae4ecc'
INVALID_HEREAFTER = '28025039'

def get_address_balance(address):
    command = ['cardano-cli', 'query', 'utxo', '--address', address, '--mainnet', '--mary-era']
    print(f'======== Getting address balance ({address}) ========')
    print(command)
    try:
        output = subprocess.run(command, check=True, capture_output=True)
        print(f'> {output.stdout}')
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr)
    transactions = output.stdout.splitlines()
    for row in transactions:
        if len(row.split()) == 4:
            transaction = row
    tx_assets = transaction.split()
    tx_hash, tx_ix, balance = tx_assets[:3]
    tokens = b' '.join(tx_assets[5:])
    return tx_hash.decode('utf-8'), tx_ix.decode('utf-8'), balance.decode('utf-8'), tokens.decode('utf-8')

def build_draft_transaction(tokens, tx_hash, tx_ix, balance, address, policy_id, token_name, transaction_number, tokens_per_transaction, metadata_file, out_file):
    assets = []
    token_number = transaction_number*tokens_per_transaction+1
    for j in range(tokens_per_transaction):
        assets.append(f'1 {policy_id}.{token_name}{token_number}')
        token_number += 1

    #### TODO:
    #### UPDATE OUPUT NUMBER ON MIN FEE CALCULATION
    #### SAME UPDATES IN BUILD FINAL FUNCTION
    #### UPDATE LOOP NUMBER
    #### UPDATE GET BLANACE ROW NUMBER
    assets_string = '+'.join(assets)
    if not tokens:
        command = ['cardano-cli', 'transaction', 'build-raw', '--tx-in', f'{tx_hash}#{tx_ix}', '--tx-out', f'{address}+{balance} lovelace', '--tx-out', f'{address}+{balance} lovelace+{assets_string}', '--mint', assets_string, '--fee', '0', '--metadata-json-file', metadata_file, '--out-file', out_file, '--mary-era', '--invalid-hereafter', INVALID_HEREAFTER]
    else:
        command = ['cardano-cli', 'transaction', 'build-raw', '--tx-in', f'{tx_hash}#{tx_ix}', '--tx-out', f'{address}+{balance} lovelace+{tokens}', '--tx-out', f'{address}+{balance} lovelace+{assets_string}', '--mint', assets_string, '--fee', '0', '--metadata-json-file', metadata_file, '--out-file', out_file, '--mary-era', '--invalid-hereafter', INVALID_HEREAFTER]
    print(f'======== Building draft transaction {transaction_number} ========')
    print(command)
    try:
        output = subprocess.run(command, check=True, capture_output=True)
        print(f'> {output.stdout}')
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr)

def build_final_transaction(tokens, tx_hash, tx_ix, balance, min_fee, address, policy_id, token_name, transaction_number, tokens_per_transaction, metadata_file, out_file):
    assets = []
    token_number = transaction_number*tokens_per_transaction+1
    for j in range(tokens_per_transaction):
        assets.append(f'1 {policy_id}.{token_name}{token_number}')
        token_number += 1

    assets_string = '+'.join(assets)
    final_balance = int(balance)-int(min_fee)
    min_output_size = 6500000
    if not tokens:
        command = ['cardano-cli', 'transaction', 'build-raw', '--tx-in', f'{tx_hash}#{tx_ix}', '--tx-out', f'{address}+{final_balance-min_output_size} lovelace', '--tx-out', f'{address}+{min_output_size} lovelace+{assets_string}', '--mint', assets_string, '--fee', min_fee, '--metadata-json-file', metadata_file, '--out-file', out_file, '--mary-era', '--invalid-hereafter', INVALID_HEREAFTER]
    else:
        command = ['cardano-cli', 'transaction', 'build-raw', '--tx-in', f'{tx_hash}#{tx_ix}', '--tx-out', f'{address}+{final_balance-min_output_size} lovelace+{tokens}', '--tx-out', f'{address}+{min_output_size} lovelace+{assets_string}', '--mint', assets_string, '--fee', min_fee, '--metadata-json-file', metadata_file, '--out-file', out_file, '--mary-era', '--invalid-hereafter', INVALID_HEREAFTER]
    print(f'======== Building final transaction {transaction_number} ========')
    print(command)
    try:
        output = subprocess.run(command, check=True, capture_output=True)
        print(f'> {output.stdout}')
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr)

def calculate_minimum_fee(tokens, draft_file, protocol_file):
    command = ['cardano-cli', 'transaction', 'calculate-min-fee', '--tx-body-file', draft_file, '--tx-in-count', '1', '--tx-out-count', '2', '--witness-count', '2', '--protocol-params-file', protocol_file]
    print(f'======== Calculating minimum fee ========')
    print(command)
    try:
        output = subprocess.run(command, check=True, capture_output=True)
        print(f'> {output.stdout}')
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr)
    min_fee, _ = output.stdout.split()
    return min_fee.decode('utf-8')

def sign_transaction(payment_signing_key_file, policy_signing_key_file, policy_script_file, final_transaction_file, out_file):
    command = ['cardano-cli', 'transaction', 'sign', '--signing-key-file', payment_signing_key_file, '--signing-key-file', policy_signing_key_file, '--script-file', policy_script_file, '--tx-body-file', final_transaction_file, '--out-file', out_file]
    print(f'======== Signing final transaction ========')
    print(command)
    try:
        output = subprocess.run(command, check=True, capture_output=True)
        print(f'> {output.stdout}')
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr)

def submit_transaction(signed_file):
    command = ['cardano-cli', 'transaction', 'submit', '--tx-file', signed_file, '--mainnet']
    print(f'======== Submitting signed transaction ========')
    print(command)
    try:
        output = subprocess.run(command, check=True, capture_output=True)
        print(f'> {output.stdout}')
    except subprocess.CalledProcessError as e:
        raise Exception(e.stderr)

TRANSACTION_COUNT = 200

old_tx_hash, old_tx_ix, old_balance, old_tokens = '', '', '', ''

for i in range(69, TRANSACTION_COUNT):
    print(f'================ {i} ================')
    while True:
        tx_hash, tx_ix, balance, tokens = get_address_balance(ADDRESS)
        if tx_hash != old_tx_hash or tx_ix != old_tx_ix or balance != old_balance or tokens != old_tokens:
            old_tx_hash = tx_hash
            old_tx_ix = tx_ix
            old_balance = balance
            old_tokens = tokens
            break
    
    draft_file = f'DraftTransactions/matx{i}.draft'
    final_file = f'FinalTransactions/matx{i}.raw'
    metadata_file = f'Metadata/metadata{i}.json'
    build_draft_transaction(tokens, tx_hash, tx_ix, balance, ADDRESS, POLICY_ID, 'Zombit', i, 50, metadata_file, draft_file)
    min_fee = calculate_minimum_fee(tokens, draft_file, 'protocol.json')
    build_final_transaction(tokens, tx_hash, tx_ix, balance, min_fee, ADDRESS, POLICY_ID, 'Zombit', i, 50, metadata_file, final_file)

    ### TRY UNTIL HERE

    signed_file = f'SignedTransactions/matx{i}.signed'
    sign_transaction('zombits_payment.skey', 'policy.skey', 'policy.json', final_file, signed_file)
    submit_transaction(signed_file)
