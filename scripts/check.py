import numpy as np
import glob
import random
from PIL import Image

TOTAL_ZOMBITS = 10_000

finals = []
for i in range(TOTAL_ZOMBITS):
    finals.append(np.array(Image.open(f'Final/Zombit{i+1}.png')))

print(f'Checking {len(finals)} Zombits')

for i in range(TOTAL_ZOMBITS - 1):
    for j in range(i+1, TOTAL_ZOMBITS):
        zombit_id_i = i+1
        zombit_id_j = j+1

        zombit_image_i = finals[i]
        zombit_image_j = finals[j]

        if np.array_equal(zombit_image_i, zombit_image_j):
            print(f'Identicals found, i: {zombit_id_i}, j: {zombit_id_j}')
