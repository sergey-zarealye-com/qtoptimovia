import numpy as np
from glob import glob
from matplotlib import pyplot as plt
import re
from findpeaks import findpeaks
import os
import pandas as pd

f = re.compile("___\S+___")

# for fn in sorted(glob(r"D:\Sergey\qtoptimovia\data\tmp*.npy")):
#     im = np.load(fn)
#     plt.figure()
#     plt.imshow(im)
#     title = f.findall(fn)
#     plt.title(title[0])
# plt.show()

if 0:
    X, Y = [], []
    with open("data/tmp.txt") as inp:
        for row in inp:
            data = row.split()
            if len(data) == 2:
                x, y = float(data[0]), float(data[1])
                X.append(x)
                Y.append(y)
if 0:
    fp = findpeaks(method='peakdetect', lookahead=5, interpolate=4)
    results = fp.fit(Y)
    df = results['df']
    print(df[df['peak']])
    results['df'].to_excel('data/peaks.xlsx')
    # print(results['persistence'])
    peaks = df[df['peak']]
    # Plot the results
    # fp.plot_persistence()
    plt.figure()
    plt.plot(Y)
    plt.plot(peaks['x'], peaks['y'], 'ro')
    plt.show()

if 0:
    STEP_MSEC = 320//2
    step_frames = 8 // 2
    SCENE_THR = 0.02
    POOLING_SIZE = 10
    DIST_THRE = 0.01
    POOL_IDX_BY_N_FV = POOLING_SIZE
    RELEASE = STEP_MSEC * 4
    # FILTR = np.array([-0.01428036, -0.46054231, 0., 0.46054231, 0.01428036])  # sigma 0.6.1
    FILTR = np.array([-2./12, -6./12, 0., 6./12, 2./12])  # Barron
    # FILTR = np.array([-2./12, -8./12, 0., 8./12, 2./12])
    NFILTR = len(FILTR)
    last_detected = 0
    lastsofar = 0
    online_scene_dists = [0.]
    online_scene_scene_keys = [0.]
    scene_fvectors = []
    dist_thresh_coef = 1.25 - 0.0625 * step_frames
    dist_thresh_window = int(20 * 8 / step_frames)
    dist_thresh_default = SCENE_THR
    fv_dists = []
    yy_shit = [0]
    tresps, resps = [], []

    for pos_sec, scene_distance in zip(X, Y):
        if scene_distance < DIST_THRE:
            scene_distance = 0.
        online_scene_dists.append(scene_distance)
        if len(fv_dists) > dist_thresh_window:
            SCENE_THR = max(dist_thresh_default, np.array(fv_dists[-dist_thresh_window:]).std() * dist_thresh_coef)
        fv_dists.append(scene_distance)
        if len(online_scene_dists) > NFILTR:
            online_scene_dists.pop(0)
            buff = np.array(online_scene_dists)
            resp = np.dot(buff, FILTR)
            resps.append(resp)
            tresps.append(pos_sec)

            # TODO the following is a crap:
            if STEP_MSEC < 160:
                pos_msec = pos_sec * 1000
            else:
                pos_msec = pos_sec * 1000 - (NFILTR / 2 - 1) * STEP_MSEC
            if resp >= SCENE_THR and pos_msec > last_detected + RELEASE:
                online_scene_scene_keys.append(pos_msec)
                yy_shit.append(scene_distance)
                last_detected = pos_msec
                scene_fvectors = [scene_distance]
    if len(scene_fvectors):
        online_scene_scene_keys.append(lastsofar)
        yy_shit.append(scene_distance)

    K = NFILTR-1
    # stds = [np.std(resps[i-K:i])*2 for i, y in enumerate(resps[K:])]

    stds = np.std(np.lib.stride_tricks.sliding_window_view(resps, K), axis=-1) * 2

    plt.figure()
    plt.plot(X, Y)
    plt.plot(tresps, np.abs(np.array(resps)))
    plt.plot(tresps[K-1:], stds)
    # plt.scatter(
    #     [t/1000 for t in online_scene_scene_keys],
    #     yy_shit
    # )
    plt.show()

if 1:
    for fn in glob("data/*.txt"):
        df = pd.read_table(fn, sep=" ")
        data = df.values
        T = data[:, 2].copy()
        for i in range(10, T.shape[0]):
            T[i] = data[0:i, 2].std() * 3

        print(data[:, 2].std())

        #(pos_list[idx]['pos_sec'], delta, abs(resp), scene_threshold, int(now_triggered))
        plt.figure()
        plt.plot(data[:,0], data[:,1], label='delta')
        plt.plot(data[:, 0], data[:, 2], label='resp')
        plt.plot(data[:, 0], data[:, 3], label='T')
        plt.plot(data[:, 0], data[:, 4]*.2, 'r.')
        plt.plot(data[:, 0], T)
        plt.legend()
        plt.title(os.path.basename(fn))
        plt.ylim(0, 2)
    plt.show()

if 0:
    import pandas as pd

    FILTR = np.array([-2. / 12, -6. / 12, 0., 6. / 12, 2. / 12])
    FILTR = np.array([-25/12,	4,	-3,	4/3,	-1/4]) #forward data[3:-1, 0
    FILTR = np.array([35 / 12,    -26 / 3,    19 / 2,    -14 / 3,   11 / 12])

    df = pd.read_table("data/tmp.txt", sep=" ")
    data = df.values
    deltas = np.convolve(data[:,1], FILTR, 'valid')
    thr = np.std(np.lib.stride_tricks.sliding_window_view(deltas, 5), axis=-1)*2
    # thr = np.mean(np.lib.stride_tricks.sliding_window_view(deltas, 4), axis=-1)
    plt.figure()
    plt.plot(data[:, 0], data[:, 1])
    plt.plot(data[3:-1, 0], np.abs(deltas))
    # plt.plot(data[5:-3, 0], thr)
    plt.show()