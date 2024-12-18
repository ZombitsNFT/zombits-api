import pandas as pd
import numpy as np
import requests
import json
import time

zombits_arweave = np.array(pd.read_csv('zombits_arweave.csv', header=None))

headers = {
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Sec-GPC': '1',
    'Origin': 'https://viewblock.io',
    'Referer': 'https://viewblock.io/',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'
}

for row in zombits_arweave:
    zombit_id, arweave_id, ipfs_hash = row

    if zombit_id > 621:
        data = f'{{"value":"{arweave_id}","network":"mainnet"}}'

        response = requests.post(f'https://api.viewblock.io/search', data=data, headers=headers)
        response_json = json.loads(response.text)

        try:
            number_of_results = len(response_json['results'])
            result_arweave_hash = response_json['results'][0]['hash']
            result_ipfs_id = response_json['results'][0]['extra']['tags'][0]['value']
            result_status = response_json['results'][0]['status']
        except:
            raise Exception(f'Error parsing response: {response.text}')

        if number_of_results != 1:
            with open('arweave_error.csv', 'a') as errfile:
                errfile.write(f'NUMBER OF RESULTS IS NOT 1,{zombit_id},{arweave_id},{ipfs_hash},{response.text}')

        if result_arweave_hash != arweave_id:
            with open('arweave_error.csv', 'a') as errfile:
                errfile.write(f'ARWEAVE HASH AND ID DO NOT MATCH,{zombit_id},{arweave_id},{ipfs_hash},{response.text}')

        if result_ipfs_id != ipfs_hash:
            with open('arweave_error.csv', 'a') as errfile:
                errfile.write(f'IPFS VALUES DO NOT MATCH,{zombit_id},{arweave_id},{ipfs_hash},{response.text}')

        if result_status != 'mined':
            with open('arweave_error.csv', 'a') as errfile:
                errfile.write(f'NOT MINED,{zombit_id},{arweave_id},{ipfs_hash},{response.text}')

        print(f'Zombit ID: {zombit_id}, Arweave ID: {arweave_id}, IPFS Hash: {ipfs_hash}, Status: {result_status}, Number of results: {number_of_results}')

        time.sleep(5)
