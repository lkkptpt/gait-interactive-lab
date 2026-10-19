#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把上肢骨骼加進 anatomy.json，並把肩／肘／腕關節中心寫進 skeleton.json。

骨頭來源：BodyParts3D 4.x 的 STL（CC BY-SA 2.1 JP），
   取自 GitHub 鏡像 Kevin-Mattheus-Moerman/BodyParts3D（原站台從本機連不到）。
   與既有 126 塊骨頭是同一副標本，所以座標直接對得上。

座標轉換（由既有右股骨的包圍盒反推、三塊骨頭交叉驗證，誤差 < 0.1 mm）：
   模型 (x, y, z) = 原始 (−Y, Z, −X) / 1000      原始單位 mm、Z 向上

節段切法（與動作資料的關節角對應）：
   鎖骨、肩胛骨  → thorax（肩帶沒有動作資料，跟胸廓一起動）
   肱骨          → humerus_r / humerus_l（肩關節）
   橈骨、尺骨    → forearm_r / forearm_l（肘關節；前臂旋轉沒有拆出來）
   腕骨、掌骨、指骨 → hand_r / hand_l（腕關節）

關節中心（全部是從骨頭幾何推估，provenance = derived）：
   肩：肱骨頭最小平方球面擬合（肱骨最上端 40 mm 內、偏內側的點）
   肘：肱骨遠端 20 mm 切片的質心
   腕：橈骨＋尺骨遠端 15 mm 切片的質心

減面：肱骨／橈骨／尺骨保留 35%，肩胛骨 6%，鎖骨 20%，手部小骨頭下限 220 面。
"""
import io, json, base64, struct, sys, os
import numpy as np
import fast_simplification

HERE = os.path.dirname(os.path.abspath(__file__))
BP = '/home/claude/kevin-mattheus-moerman/bodyparts3d/assets/BodyParts3D_data/stl/'
ANAT = os.path.join(HERE, 'anatomy.json')
SKEL = os.path.join(HERE, 'skeleton.json')

FLOOR_FACES = 220

# (FMA, 中文名, 節段, 保留比例)
def side_parts(S, s):
    L = '右' if S == 'r' else '左'
    f = lambda r, l: r if S == 'r' else l
    P = [
        (f('FMA13322', 'FMA13323'), L + '鎖骨',   'thorax',       0.20),
        (f('FMA13395', 'FMA13396'), L + '肩胛骨', 'thorax',       0.06),
        (f('FMA23130', 'FMA23131'), L + '肱骨',   'humerus_' + s, 0.35),
        (f('FMA23464', 'FMA23465'), L + '橈骨',   'forearm_' + s, 0.35),
        (f('FMA23467', 'FMA23468'), L + '尺骨',   'forearm_' + s, 0.35),
        (f('FMA24435', 'FMA24436'), L + '腕舟骨',   'hand_' + s, 0.30),
        (f('FMA24437', 'FMA24438'), L + '月骨',     'hand_' + s, 0.30),
        (f('FMA24439', 'FMA24440'), L + '三角骨',   'hand_' + s, 0.30),
        (f('FMA24441', 'FMA24442'), L + '豌豆骨',   'hand_' + s, 0.30),
        (f('FMA24443', 'FMA24444'), L + '大多角骨', 'hand_' + s, 0.30),
        (f('FMA23725', 'FMA24445'), L + '小多角骨', 'hand_' + s, 0.30),
        (f('FMA24446', 'FMA24447'), L + '頭狀骨',   'hand_' + s, 0.30),
        (f('FMA24448', 'FMA24449'), L + '鉤骨',     'hand_' + s, 0.30),
        (f('FMA24464', 'FMA24465'), L + '第1掌骨', 'hand_' + s, 0.30),
        (f('FMA24466', 'FMA24467'), L + '第2掌骨', 'hand_' + s, 0.30),
        (f('FMA24468', 'FMA24469'), L + '第3掌骨', 'hand_' + s, 0.30),
        (f('FMA24470', 'FMA24471'), L + '第4掌骨', 'hand_' + s, 0.30),
        (f('FMA24472', 'FMA24473'), L + '第5掌骨', 'hand_' + s, 0.30),
        (f('FMA24450', 'FMA65470'), L + '拇指近節', 'hand_' + s, 0.30),
        (f('FMA24459', 'FMA23951'), L + '拇指遠節', 'hand_' + s, 0.30),
        (f('FMA24451', 'FMA71915'), L + '第2指近節', 'hand_' + s, 0.30),
        (f('FMA24452', 'FMA71908'), L + '第3指近節', 'hand_' + s, 0.30),
        (f('FMA24453', 'FMA71916'), L + '第4指近節', 'hand_' + s, 0.30),
        (f('FMA24454', 'FMA66791'), L + '第5指近節', 'hand_' + s, 0.30),
        (f('FMA24455', 'FMA23938'), L + '第2指中節', 'hand_' + s, 0.30),
        (f('FMA24456', 'FMA23940'), L + '第3指中節', 'hand_' + s, 0.30),
        (f('FMA24457', 'FMA23942'), L + '第4指中節', 'hand_' + s, 0.30),
        (f('FMA24458', 'FMA23944'), L + '第5指中節', 'hand_' + s, 0.30),
        (f('FMA24460', 'FMA23953'), L + '第2指遠節', 'hand_' + s, 0.30),
        (f('FMA24461', 'FMA23955'), L + '第3指遠節', 'hand_' + s, 0.30),
        (f('FMA24462', 'FMA23957'), L + '第4指遠節', 'hand_' + s, 0.30),
        (f('FMA24463', 'FMA23959'), L + '第5指遠節', 'hand_' + s, 0.30),
    ]
    return P


def read_stl(fn):
    """二進位 STL → 焊接後的頂點與面（模型座標，公尺）。"""
    d = open(fn, 'rb').read()
    n = struct.unpack('<I', d[80:84])[0]
    rec = np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    tri = np.frombuffer(d, dtype=rec, count=n, offset=84)['v'].reshape(-1, 3).astype(np.float64)
    # 座標轉換：模型 (x,y,z) = 原始 (−Y, Z, −X)/1000
    pts = np.stack([-tri[:, 1], tri[:, 2], -tri[:, 0]], axis=1) / 1000.0
    # 焊接：同一個點在 STL 裡每個三角形各存一份，依 1 µm 格點合併
    key = np.round(pts * 1e6).astype(np.int64)
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    verts = np.zeros((uniq.shape[0], 3))
    np.add.at(verts, inv, pts)
    cnt = np.bincount(inv, minlength=uniq.shape[0])
    verts /= cnt[:, None]
    faces = inv.reshape(-1, 3)
    ok = (faces[:, 0] != faces[:, 1]) & (faces[:, 1] != faces[:, 2]) & (faces[:, 0] != faces[:, 2])
    return verts, faces[ok]


def decimate(verts, faces, keep):
    target = max(FLOOR_FACES, int(round(faces.shape[0] * keep)))
    if faces.shape[0] <= target:
        return verts, faces
    red = 1.0 - target / faces.shape[0]
    v2, f2 = fast_simplification.simplify(verts.astype(np.float32), faces.astype(np.int64), red)
    v2 = v2.astype(np.float64); f2 = f2.astype(np.int64)
    ok = (f2[:, 0] != f2[:, 1]) & (f2[:, 1] != f2[:, 2]) & (f2[:, 0] != f2[:, 2])
    f2 = f2[ok]
    used = np.unique(f2)
    remap = np.full(v2.shape[0], -1, dtype=np.int64); remap[used] = np.arange(used.size)
    return v2[used], remap[f2]


def quantize(pts):
    lo = pts.min(axis=0); hi = pts.max(axis=0); sp = hi - lo
    sp[sp < 1e-9] = 1e-9
    q = np.rint((pts - lo) / sp * 65535.0).clip(0, 65535).astype('<u2')
    return lo, sp, q


def sphere_fit(p):
    """最小平方球面擬合，回傳 (中心, 半徑)。"""
    A = np.hstack([2 * p, np.ones((p.shape[0], 1))])
    b = (p ** 2).sum(axis=1)
    x, *_ = np.linalg.lstsq(A, b, rcond=None)
    c = x[:3]; r = np.sqrt(x[3] + (c ** 2).sum())
    return c, r


def joint_centres(raw, s):
    """raw: {中文名: (verts, faces)}（模型座標、世界系）。"""
    L = '右' if s == 'r' else '左'
    hum = raw[L + '肱骨'][0]; rad = raw[L + '橈骨'][0]; uln = raw[L + '尺骨'][0]
    # 肩：肱骨頭。取最上端 40 mm、且在肱骨幹軸內側（朝身體中線）那一半的點做球面擬合
    top = hum[hum[:, 1] > hum[:, 1].max() - 0.040]
    zc = np.median(hum[:, 2])
    # +z 是身體右側：右臂的內側是 z 較小的一半，左臂相反
    medial = top[top[:, 2] < zc] if s == 'r' else top[top[:, 2] > zc]
    head = medial if medial.shape[0] > 200 else top
    c, r = sphere_fit(head)
    # 肘：肱骨遠端 20 mm 切片質心
    dist = hum[hum[:, 1] < hum[:, 1].min() + 0.020]
    e = dist.mean(axis=0)
    # 腕：橈骨＋尺骨遠端 15 mm 切片質心
    fa = np.vstack([rad, uln])
    w = fa[fa[:, 1] < fa[:, 1].min() + 0.015].mean(axis=0)
    return {
        'shoulder_' + s: {'p': [round(float(v), 5) for v in c], 'provenance': 'derived',
                          'method': '肱骨頭最小平方球面擬合（最上端 40 mm、內側半邊的頂點）',
                          'note': '擬合半徑 %.1f mm，n=%d' % (r * 1000, head.shape[0])},
        'elbow_' + s: {'p': [round(float(v), 5) for v in e], 'provenance': 'derived',
                       'method': '肱骨遠端 20 mm 切片質心', 'note': ''},
        'wrist_' + s: {'p': [round(float(v), 5) for v in w], 'provenance': 'derived',
                       'method': '橈骨與尺骨遠端 15 mm 切片質心', 'note': ''},
    }, r


def main():
    anat = json.load(open(ANAT, encoding='utf-8'))
    skel = json.load(open(SKEL, encoding='utf-8'))
    if any(p['s'].startswith('humerus') for p in anat['parts']):
        sys.exit('anatomy.json 已經含有上肢，不重複加')
    buf = bytearray(base64.b64decode(anat['buf']))
    parts = anat['parts']
    nf_before = sum(p['nf'] for p in parts)

    new_joints = {}
    added = 0; faces_raw = 0; faces_out = 0
    for s in ('r', 'l'):
        spec = side_parts(s, s)
        raw = {}
        for fma, name, seg, keep in spec:
            raw[name] = read_stl(BP + fma + '.stl')
        jc, rad = joint_centres(raw, s)
        assert 0.018 < rad < 0.030, '肱骨頭擬合半徑不合理：%.1f mm' % (rad * 1000)
        new_joints.update(jc)
        seg_origin = {'thorax': np.array(skel['joints']['thorax']['p']),
                      'humerus_' + s: np.array(jc['shoulder_' + s]['p']),
                      'forearm_' + s: np.array(jc['elbow_' + s]['p']),
                      'hand_' + s: np.array(jc['wrist_' + s]['p'])}
        for fma, name, seg, keep in spec:
            v, f = raw[name]
            faces_raw += f.shape[0]
            v, f = decimate(v, f, keep)
            faces_out += f.shape[0]
            assert f.max() < 65536 and v.shape[0] < 65536, name + ' 頂點數超過 Uint16'
            local = v - seg_origin[seg]            # 節段局部座標：相對該節段的關節中心
            lo, sp, q = quantize(local)
            vo = len(buf); buf += q.tobytes()
            io_ = len(buf); buf += f.astype('<u2').tobytes()
            parts.append({'n': name, 'fma': fma, 's': seg,
                          'lo': [round(float(x), 6) for x in lo],
                          'sp': [round(float(x), 6) for x in sp],
                          'nv': int(v.shape[0]), 'nf': int(f.shape[0]), 'vo': vo, 'io': io_})
            added += 1
        print('%s 側：%d 塊，肱骨頭半徑 %.1f mm，肩 %s 肘 %s 腕 %s' % (
            s, len(spec), rad * 1000, jc['shoulder_' + s]['p'], jc['elbow_' + s]['p'], jc['wrist_' + s]['p']))

    anat['buf'] = base64.b64encode(bytes(buf)).decode()
    anat['mesh_note'] = (anat['mesh_note'] +
        ' 上肢 64 塊（鎖骨、肩胛骨、肱骨、橈骨、尺骨、腕骨、掌骨、指骨）另行減面：'
        '肱骨／橈骨／尺骨保留 35%%、鎖骨 20%%、肩胛骨 6%%，手部小骨頭下限 220 面；'
        '上肢原始面數 %d，現為 %d。' % (faces_raw, faces_out))
    json.dump(anat, open(ANAT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

    skel['joints'].update(new_joints)
    for s in ('r', 'l'):
        skel['hier']['humerus_' + s] = ['thorax', 'shoulder_' + s]
        skel['hier']['forearm_' + s] = ['humerus_' + s, 'elbow_' + s]
        skel['hier']['hand_' + s] = ['forearm_' + s, 'wrist_' + s]
    json.dump(skel, open(SKEL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('加入 %d 塊骨頭；總面數 %d → %d；anatomy.json %.2f MB' % (
        added, nf_before, nf_before + faces_out, os.path.getsize(ANAT) / 1048576))


if __name__ == '__main__':
    main()
