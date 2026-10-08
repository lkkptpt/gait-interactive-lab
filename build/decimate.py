#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 anatomy.json 的骨骼網格減面。

為什麼不是所有骨頭用同一個比例：
    胸廓（39 塊肋骨胸骨）佔了 38% 的面數，但步態教學不會看肋骨細節；
    下肢與骨盆才是要看的。所以依節段分配不同的保留比例，
    把預算花在會被放大檢視的地方。

輸入輸出格式與原檔完全相同（Uint16 量化頂點 ＋ Uint16 索引，
緊鄰打包成一塊 base64 二進位），瀏覽器端不必改任何程式。

用法：
    python3 decimate.py 原檔.json 輸出.json [等級]
    等級：soft / medium / hard，預設 medium
"""
import sys, json, base64, struct
import numpy as np
import fast_simplification

# 每個節段「保留」的面數比例。數字越小刪越多。
LEVELS = {
    'soft':   {'下肢': 0.75, '骨盆腰椎': 0.75, '頸椎': 0.55, '胸廓': 0.45, '頭顱': 0.45},
    'medium': {'下肢': 0.55, '骨盆腰椎': 0.55, '頸椎': 0.35, '胸廓': 0.25, '頭顱': 0.25},
    'hard':   {'下肢': 0.40, '骨盆腰椎': 0.40, '頸椎': 0.22, '胸廓': 0.15, '頭顱': 0.15},
    # 實際採用的等級：把面數預算集中在會被放大檢視的下肢與骨盆，
    # 胸廓與頭顱在步態教學裡只是背景，砍得比較兇。
    'balanced': {'下肢': 0.75, '骨盆腰椎': 0.65, '頸椎': 0.25, '胸廓': 0.18, '頭顱': 0.18},
}

REGION = {}
for s in ('femur_r', 'femur_l', 'tibia_r', 'tibia_l', 'talus_r', 'talus_l',
          'foot_r', 'foot_l', 'toes_r', 'toes_l'):
    REGION[s] = '下肢'
for s in ('pelvis', 'lumbar'):
    REGION[s] = '骨盆腰椎'
REGION['cervical'] = '頸椎'
REGION['thorax'] = '胸廓'
REGION['head'] = '頭顱'

# 低於這個面數就不再減——小骨頭（趾骨、頸椎椎體）再減會塌掉
FLOOR_FACES = 220


def unpack(part, buf):
    """取出某塊骨頭的實際座標與面索引。"""
    nv, nf = part['nv'], part['nf']
    q = np.frombuffer(buf, dtype='<u2', count=nv * 3,
                      offset=part['vo']).reshape(nv, 3).astype(np.float64)
    lo = np.array(part['lo'], dtype=np.float64)
    sp = np.array(part['sp'], dtype=np.float64)
    pts = lo + q / 65535.0 * sp
    idx = np.frombuffer(buf, dtype='<u2', count=nf * 3,
                        offset=part['io']).reshape(nf, 3).astype(np.int64)
    return pts, idx


def quantize(pts, idx):
    """重新量化。包圍盒重算，因為減面後範圍可能縮小，盒子越緊精度越好。"""
    lo = pts.min(axis=0)
    hi = pts.max(axis=0)
    sp = hi - lo
    sp[sp < 1e-9] = 1e-9          # 避免平面物件除以零
    q = np.rint((pts - lo) / sp * 65535.0).clip(0, 65535).astype('<u2')
    return lo, sp, q, idx.astype('<u2')


def compact(pts, idx):
    """丟掉沒有被任何面引用的頂點，並重編索引。"""
    used = np.unique(idx)
    remap = np.full(pts.shape[0], -1, dtype=np.int64)
    remap[used] = np.arange(used.size)
    return pts[used], remap[idx]


def drop_degenerate(idx):
    """移除三個頂點有重複的面（減面後偶爾會出現）。"""
    ok = (idx[:, 0] != idx[:, 1]) & (idx[:, 1] != idx[:, 2]) & (idx[:, 0] != idx[:, 2])
    return idx[ok]


def decimate_part(part, buf, keep):
    pts, idx = unpack(part, buf)
    target_faces = max(FLOOR_FACES, int(round(part['nf'] * keep)))
    if target_faces < part['nf']:
        reduction = 1.0 - target_faces / float(part['nf'])
        try:
            pts, idx = fast_simplification.simplify(
                pts.astype(np.float32), idx.astype(np.int32), reduction)
            pts = pts.astype(np.float64)
            idx = idx.astype(np.int64)
        except Exception as e:                      # 個別骨頭失敗就保留原樣，不要整批掛掉
            sys.stderr.write('  ! %s 減面失敗，保留原網格：%s\n' % (part['n'], e))
            pts, idx = unpack(part, buf)
    idx = drop_degenerate(idx)
    pts, idx = compact(pts, idx)
    assert pts.shape[0] < 65536, '%s 頂點數 %d 超出 Uint16' % (part['n'], pts.shape[0])
    return pts, idx


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/repo/build/anatomy.json'
    dst = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/repo/build/anatomy.json'
    level = sys.argv[3] if len(sys.argv) > 3 else 'medium'
    keeps = LEVELS[level]

    a = json.load(open(src, encoding='utf-8'))
    buf = base64.b64decode(a['buf'])

    out_parts, chunks, off = [], [], 0
    f0 = v0 = f1 = v1 = 0

    for part in a['parts']:
        region = REGION.get(part['s'], '胸廓')
        pts, idx = decimate_part(part, buf, keeps[region])
        lo, sp, q, i16 = quantize(pts, idx)

        vbytes = q.tobytes()
        ibytes = i16.tobytes()
        p = dict(part)
        p['lo'] = [round(float(x), 6) for x in lo]
        p['sp'] = [round(float(x), 6) for x in sp]
        p['nv'] = int(q.shape[0])
        p['nf'] = int(i16.shape[0])
        p['vo'] = off
        p['io'] = off + len(vbytes)
        off += len(vbytes) + len(ibytes)
        assert off % 2 == 0, 'Uint16 需要 2 位元組對齊'
        chunks.append(vbytes)
        chunks.append(ibytes)
        out_parts.append(p)

        v0 += part['nv']; f0 += part['nf']
        v1 += p['nv'];    f1 += p['nf']

    newbuf = b''.join(chunks)
    a['parts'] = out_parts
    a['buf'] = base64.b64encode(newbuf).decode('ascii')
    a['mesh_note'] = ('網格經 quadric decimation 減面（等級 %s）；'
                      '下肢與骨盆保留較多面數，胸廓與頭顱減量較多。'
                      '原始面數 %d，現為 %d。' % (level, f0, f1))

    with open(dst, 'w', encoding='utf-8') as fh:
        json.dump(a, fh, ensure_ascii=False, separators=(',', ':'))

    print('等級 %s' % level)
    print('  頂點 %7d → %7d  (%.1f%%)' % (v0, v1, 100.0 * v1 / v0))
    print('  面   %7d → %7d  (%.1f%%)' % (f0, f1, 100.0 * f1 / f0))
    print('  二進位 %.2f MB → %.2f MB' % (len(buf) / 1048576, len(newbuf) / 1048576))
    import os
    print('  輸出 %s（%.2f MB）' % (dst, os.path.getsize(dst) / 1048576))


if __name__ == '__main__':
    main()
