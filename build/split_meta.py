#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把中足再切一刀：舟骰楔 一段、五根蹠骨 一段，中間放跗蹠（Lisfranc）關節。

拆之前：
    foot_r(跟骨) --midtarsal--> midfoot_r(舟+骰+3楔+5蹠) --mtp1--> hallux_r
                                                        --mtp --> toes_r

拆之後：
    foot_r(跟骨) --midtarsal--> midfoot_r(舟+骰+3楔)
                                  |--tmt--> meta_r(5蹠骨) --mtp1--> hallux_r
                                                          --mtp --> toes_r

為什麼要拆：
    舟狀骨（足弓頂點）原本跟蹠骨焊在同一塊剛體裡，中跗一轉，兩者一起上去，
    所以模型裡足弓永遠不會塌——前足會翹起來而已。切開之後舟狀骨才能相對蹠骨
    往下掉，前足留在地上。

向後相容的關鍵同上次：各節段的網格座標是相對「該節段自己的關節中心」，
搬動節段只要把 lo 平移掉新舊關節中心的差，量化值完全不用重算。
新關節角度為 0 時，所有骨頭的世界座標必須與改之前完全相同。
"""
import json, base64, sys
import numpy as np

REPO = '/home/claude/repo/build/'
META = ['第1蹠骨', '第2蹠骨', '第3蹠骨', '第4蹠骨', '第5蹠骨']


def load(fn):
    return json.load(open(REPO + fn, encoding='utf-8'))


def save(obj, fn):
    json.dump(obj, open(REPO + fn, 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))


def verts_of(part, buf):
    q = np.frombuffer(buf, dtype='<u2', count=part['nv'] * 3,
                      offset=part['vo']).reshape(part['nv'], 3).astype(float)
    return np.array(part['lo']) + q / 65535.0 * np.array(part['sp'])


def world_centroids(anat, skel, buf):
    """每塊腳部骨頭的世界座標質心（所有關節角度為 0 的參考姿勢）。"""
    J = {k: np.array(v['p']) for k, v in skel['joints'].items()}
    H = skel['hier']
    FOOT = ('foot_r', 'foot_l', 'midfoot_r', 'midfoot_l', 'meta_r', 'meta_l',
            'hallux_r', 'hallux_l', 'toes_r', 'toes_l')
    out = {}
    for p in anat['parts']:
        if p['s'] in FOOT:
            out[p['n']] = verts_of(p, buf).mean(axis=0) + J[H[p['s']][1]]
    return out


def main():
    S, A = load('skeleton.json'), load('anatomy.json')
    buf = base64.b64decode(A['buf'])
    NEW = json.load(open('/home/claude/arch/tmt_joints.json', encoding='utf-8'))

    if 'meta_r' in S['hier']:
        sys.exit('已經拆過了，請先還原再重跑')

    before = world_centroids(A, S, buf)

    # ---------- 1) skeleton.json ----------
    for side in ('r', 'l'):
        S['joints']['tmt_' + side] = {
            'p': NEW['tmt_' + side],
            'method': '三個楔狀骨與骰骨的遠端面、五根蹠骨的近端面，兩群點質心取中點',
            'note': '模型關節：資料集沒有這個關節的通道（Bruening 模型把舟骰楔與蹠骨視為同一剛體）',
        }
        S['hier']['meta_' + side] = ['midfoot_' + side, 'tmt_' + side]
        S['hier']['hallux_' + side] = ['meta_' + side, 'mtp1_' + side]
        S['hier']['toes_' + side] = ['meta_' + side, 'mtp_' + side]

    # ---------- 2) anatomy.json：蹠骨改掛到 meta，平移 lo ----------
    J = {k: np.array(v['p']) for k, v in S['joints'].items()}
    moved = 0
    for p in A['parts']:
        side = p['s'][-1]
        if side not in ('r', 'l') or not p['s'].startswith('midfoot_'):
            continue
        if p['n'][1:] in META:
            shift = J['tmt_' + side] - J['midtarsal_' + side]
            p['lo'] = [round(float(p['lo'][i] - shift[i]), 6) for i in range(3)]
            p['s'] = 'meta_' + side
            moved += 1

    # ---------- 3) 驗證：世界座標必須完全不變 ----------
    after = world_centroids(A, S, buf)
    assert set(before) == set(after), '骨頭數量對不上'
    worst, worst_n = 0.0, ''
    for n in before:
        d = float(np.linalg.norm(before[n] - after[n]))
        if d > worst:
            worst, worst_n = d, n
    print('搬動 %d 塊蹠骨（左右合計）' % moved)
    print('世界座標最大位移 %.4f mm（%s）' % (worst * 1000, worst_n))
    if worst > 1e-5:
        sys.exit('位移超過容許值，中止——骨頭會跑掉')

    save(S, 'skeleton.json')
    save(A, 'anatomy.json')

    import collections
    c = collections.Counter(p['s'] for p in A['parts'])
    print('\n新的節段骨頭數：')
    for k in ('foot_r', 'midfoot_r', 'meta_r', 'hallux_r', 'toes_r'):
        print('  %-11s %d' % (k, c[k]))
    print('\nskeleton.json 與 anatomy.json 已更新')


if __name__ == '__main__':
    main()
