#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推估跗蹠（Lisfranc）關節中心，作法與既有的中跗關節一致：
取近端骨（三個楔狀骨＋骰骨）的遠端面、與遠端骨（五根蹠骨）的近端面，
兩群點質心的中點。

新關節會把目前的中足再切一刀：
    舟狀骨＋骰骨＋三楔  ──跗蹠── 五根蹠骨
"""
import json, base64, sys
import numpy as np

SRC = '/home/claude/repo/build/anatomy.json'
SKEL = '/home/claude/repo/build/skeleton.json'

A = json.load(open(SRC, encoding='utf-8'))
BUF = base64.b64decode(A['buf'])
BY_NAME = {p['n']: p for p in A['parts']}
S = json.load(open(SKEL, encoding='utf-8'))

PROX = ['內側楔狀骨', '中間楔狀骨', '外側楔狀骨', '骰骨']
DIST = ['第1蹠骨', '第2蹠骨', '第3蹠骨', '第4蹠骨', '第5蹠骨']


def verts(part):
    """取出某塊骨頭的座標（公尺），相對該節段自己的關節中心。"""
    nv = part['nv']
    q = np.frombuffer(BUF, dtype='<u2', count=nv * 3,
                      offset=part['vo']).reshape(nv, 3).astype(np.float64)
    return np.array(part['lo']) + q / 65535.0 * np.array(part['sp'])


def extreme_face(pts, axis, sign, frac=0.15):
    v = pts[:, axis] * sign
    return pts[v >= np.quantile(v, 1.0 - frac)]


def tmt(side):
    P = '右' if side == 'r' else '左'
    prox = np.vstack([extreme_face(verts(BY_NAME[P + n]), 0, +1) for n in PROX])
    dist = np.vstack([extreme_face(verts(BY_NAME[P + n]), 0, -1) for n in DIST])
    c = (prox.mean(axis=0) + dist.mean(axis=0)) / 2.0
    gap = float(np.linalg.norm(prox.mean(axis=0) - dist.mean(axis=0)))
    return c, gap


if __name__ == '__main__':
    out = {}
    for side in ('r', 'l'):
        # 這些座標是相對 midtarsal 關節中心的（midfoot 節段的區域座標）
        c, gap = tmt(side)
        mt = np.array(S['joints']['midtarsal_' + side]['p'])
        g = mt + c                      # 轉成世界座標
        out['tmt_' + side] = [round(float(x), 5) for x in g]
        print('tmt_%s  世界座標 %s   兩關節面質心間距 %.1f mm'
              % (side, [round(float(x), 4) for x in g], gap * 1000))

    print('\n沿著足部長軸的順序檢查（x 由後往前遞增）：')
    for k in ('ankle_r', 'sub_r', 'midtarsal_r'):
        print('  %-13s x = %.4f' % (k, S['joints'][k]['p'][0]))
    print('  %-13s x = %.4f   ← 新關節' % ('tmt_r', out['tmt_r'][0]))
    for k in ('mtp1_r', 'mtp_r'):
        print('  %-13s x = %.4f' % (k, S['joints'][k]['p'][0]))

    ok = (S['joints']['midtarsal_r']['p'][0] < out['tmt_r'][0]
          < S['joints']['mtp1_r']['p'][0])
    if not ok:
        sys.exit('新關節沒有落在中跗與第一蹠趾之間，中止')
    print('\n順序正確：中跗 < 跗蹠 < 第一蹠趾')

    d1 = (out['tmt_r'][0] - S['joints']['midtarsal_r']['p'][0]) * 1000
    d2 = (S['joints']['mtp1_r']['p'][0] - out['tmt_r'][0]) * 1000
    print('中跗→跗蹠 %.1f mm，跗蹠→第一蹠趾 %.1f mm' % (d1, d2))

    json.dump(out, open('/home/claude/arch/tmt_joints.json', 'w'), indent=1)
    print('已寫出 tmt_joints.json')
