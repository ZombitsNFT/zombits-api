import numpy as np
import pandas as pd
import json


zombits_arweave = np.array(pd.read_csv('zombits_arweave.csv', header=None))

with open('zombits.json') as f:
  zombits_features = json.load(f)

zombit_index = 0

zombit_metadata = []
with open(f'metadata.json', 'w') as f:
    for i in range(10000):
        zombit_id, arweave_id, ipfs_hash = zombits_arweave[zombit_index]
        zombit_features = zombits_features[f'{zombit_id}']
        zombit_metadata.append({'id': zombit_id, 'name': f'Zombit #{zombit_id}', 'features': zombit_features, 'image': f'ipfs://{ipfs_hash}', 'arweaveId': arweave_id})

        zombit_index += 1
    json.dump(zombit_metadata, f)

# import numpy as np
# import pandas as pd
# import json


# zombits_arweave = np.array(pd.read_csv('zombits_arweave.csv', header=None))

# with open('zombits.json') as f:
#   zombits_features = json.load(f)

# zombit_index = 0

# for i in range(200):
#     zombit_metadata = {'721': {'ad6290066292cfeef7376cd575e5d8367833ab3d8b2ac53d26ae4ecc': {}}}
#     with open(f'Metadata/metadata{i}.json', 'w') as f:
#         for i in range(50):
#             zombit_id, arweave_id, ipfs_hash = zombits_arweave[zombit_index]
#             zombit_features = zombits_features[f'{zombit_id}']
#             zombit_metadata['721']['ad6290066292cfeef7376cd575e5d8367833ab3d8b2ac53d26ae4ecc'][f'Zombit{zombit_id}'] = {'arweaveId': arweave_id, 'image': f'ipfs://{ipfs_hash}', 'name': f'Zombit #{zombit_id}', 'features': zombit_features}

#             zombit_index += 1
#         json.dump(zombit_metadata, f, separators=(',',':'))
