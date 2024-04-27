import numpy as np
import nmslib
import os


fname = os.path.join('data', 'scenes.idx')
index = nmslib.init(method='hnsw', space='cosinesimil')
index.loadIndex(fname)

data = np.random.random(512)
ids, distances = index.knnQuery(data, k=10)

print(ids)
print(distances)