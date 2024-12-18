import pandas as pd
import numpy as np
import requests

zombits_ipfs = np.array(pd.read_csv('zombits_ipfs.csv', header=None))

with open('zombits_arweave.csv', 'a') as outfile:
    for row in zombits_ipfs:
        zombit_id, ipfs_hash = row

        response = requests.post(f'https://ipfs2arweave.com/permapin/{ipfs_hash}')
        print(f"{zombit_id},{response.text}\n")
        outfile.write(f"{zombit_id},{response.text}\n")
