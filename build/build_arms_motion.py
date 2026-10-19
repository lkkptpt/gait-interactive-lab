#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把手臂的動作通道接進 motion.json。

手臂資料從哪裡來（逐片段）：
   hoa_*          Bertaux 2022 髖關節炎資料集，該受試者自己的雙側肩肘腕（Plug-in Gait）
   hea_mean（新） Bertaux 2022 健康對照組 80 人平均，下肢與手臂同一批人同一次量
   pd_*           Shida 2023 帕金森資料集，雙側肩肘；平均片段取同一批 22／11 人
   vc_*、mean_*、arch_walk_*
                  這些資料集的公開版本沒有手臂 → 借用 hea_mean 的手臂，介面上標示「借用」
   stroke_*       無手臂資料，也不借（偏癱的手臂不該套健康人的擺動）→ 手臂靜止並標示
   arch_*、arch_push_*（只有腳）
                  不加

通道與正負號（全部以本工具的旋轉方向為準，與髖一致）：
   shoulder_flexion_{r,l}    屈曲 +（手往前）         絕對值
   shoulder_adduction_{r,l}  內收 +                   扣掉週期平均（PiG 的額狀面偏移受試者間達 ±8–20°，絕對值不可信）
   shoulder_rotation_{r,l}   內旋 +                   扣掉週期平均（同上，SD 16°）
   elbow_flexion_{r,l}       屈曲 +                   絕對值
   wrist_flexion_{r,l}       屈曲 +                   扣掉週期平均（擺幅只有 ±3°，偏移 SD 12°）

相位：
   Bertaux 的左右檔在同一時間軸上（右肩在右足著地後 5% 最伸展、左肩在 0% 最屈曲，
   與「對側手腳同步」一致），直接用。
   Shida 的每個檔以該側自己的著地為 0%，左側通道平移 50%（與該資料集下肢的做法相同）。
"""
import io, json, os, re, zipfile, sys
import numpy as np
import xlrd

HERE = os.path.dirname(os.path.abspath(__file__))
U = '/mnt/user-data/uploads/'
BERT = [U + 'Downloads/HOA-M0-M6_HEA DataSet/Angles/', U]
MOTION = os.path.join(HERE, 'motion.json')
SKEL = os.path.join(HERE, 'skeleton.json')

Z = [0.0] * 101
d2r = np.deg2rad


# ---------- 通用 ----------
def roll50(a):
    v = np.roll(np.asarray(a, float)[:100], -50); return np.append(v, v[0])


def cyclic(v):
    """首尾線性去趨勢：讓第 100 點等於第 0 點，播放時不跳。"""
    v = np.asarray(v, float).copy()
    dv = v[100] - v[0]
    return v - dv * np.arange(101) / 100.0


def dm(v):
    v = np.asarray(v, float); return v - v[:100].mean()


def r3(v):
    return [round(float(x), 3) for x in v]


# ---------- Bertaux ARFF ----------
def permean(fn):
    out = {}
    with io.open(fn, encoding='latin-1') as fh:
        data = False
        for l in fh:
            l = l.strip()
            if not data:
                if l.lower().startswith('@data'): data = True
                continue
            if not l: continue
            p = l.split(',')
            if len(p) != 105: continue
            try: v = np.array([float(x) for x in p[:101]])
            except ValueError: continue
            if np.isnan(v).any(): continue
            out.setdefault(p[101], []).append(v)
    return {k: np.mean(v, 0) for k, v in out.items()}


_BC = {}
def bert(pre, side, part, ax):
    key = (pre, side, part, ax)
    if key not in _BC:
        for base in BERT:
            fn = '%s%s_M0_%s%sAngles_%s.arff' % (base, pre, side, part, ax)
            if os.path.exists(fn):
                _BC[key] = permean(fn); break
        else:
            raise FileNotFoundError(str(key))
    return _BC[key]


def bert_arms(pre, subj=None):
    """回傳手臂通道 dict。subj=None → 全組平均（每人先平均，再跨人平均）。"""
    def ch(side, part, ax):
        D = bert(pre, side, part, ax)
        if subj is not None: return np.asarray(D[subj], float)
        return np.mean(np.array(list(D.values())), 0)
    out = {}
    for S, s in (('R', 'r'), ('L', 'l')):
        out['shoulder_flexion_' + s] = r3(cyclic(ch(S, 'Shoulder', 'X')))
        # PiG 的肩 Y：雙側平均都是 +14～+16°，垂著的手臂不可能內收 16°，
        # 只可能是外展——所以這裡正值是外展，取負號轉成本工具的「內收 +」。
        out['shoulder_adduction_' + s] = r3(cyclic(-dm(ch(S, 'Shoulder', 'Y'))))
        out['shoulder_rotation_' + s] = r3(cyclic(dm(ch(S, 'Shoulder', 'Z'))))
        out['elbow_flexion_' + s] = r3(cyclic(ch(S, 'Elbow', 'X')))
        out['wrist_flexion_' + s] = r3(cyclic(dm(ch(S, 'Wrist', 'X'))))
    n = len(bert(pre, 'R', 'Shoulder', 'X'))
    return out, n


# ---------- Shida（帕金森）----------
_Z = zipfile.ZipFile(U + 'Gait_cycles.zip')
_ZN = {n.split('/')[-1]: n for n in _Z.namelist() if not n.startswith('__MACOSX') and n.endswith('.csv')}


def pd_file(subj, state, side, part):
    """回傳 (101, 3) 的逐週期平均：[內收外展, 旋轉, 屈伸]。"""
    name = '%s_%s_walk_%s_%s_Ang.csv' % (subj, state, side, part)
    wb = xlrd.open_workbook(file_contents=_Z.read(_ZN[name])); sh = wb.sheet_by_index(0)
    hdr = [str(sh.cell_value(0, c)) for c in range(sh.ncols)]
    assert 'Flx' in hdr[3] or 'Flex' in hdr[3], hdr[:4]
    M = np.array([[sh.cell_value(r, c) if sh.cell_value(r, c) != '' else np.nan
                   for c in range(1, sh.ncols)] for r in range(2, sh.nrows)], float)
    assert M.shape[0] == 101, M.shape
    return np.stack([np.nanmean(M[:, j::3], 1) for j in range(3)], 1)


def pd_arms(subjs, state):
    acc = {}
    for subj in subjs:
        one = {}
        for S, s in (('Right', 'r'), ('Left', 'l')):
            sh = pd_file(subj, state, S, 'Shoulder'); el = pd_file(subj, state, S, 'Elbow')
            f = (lambda v: roll50(v)) if s == 'l' else (lambda v: np.asarray(v, float))
            # Shida 的內收外展：ABD(−)/ADD(+)，與本工具同號
            one['shoulder_flexion_' + s] = f(sh[:, 2])
            one['shoulder_adduction_' + s] = dm(f(sh[:, 0]))
            one['shoulder_rotation_' + s] = dm(f(sh[:, 1]))
            one['elbow_flexion_' + s] = f(el[:, 2])
            one['wrist_flexion_' + s] = np.zeros(101)
        for k, v in one.items(): acc.setdefault(k, []).append(v)
    return {k: r3(cyclic(np.mean(np.array(v), 0))) for k, v in acc.items()}


PD_PAIRED = ['SUB01', 'SUB02', 'SUB03', 'SUB05', 'SUB06', 'SUB07', 'SUB08', 'SUB09', 'SUB10', 'SUB11',
             'SUB12', 'SUB13', 'SUB14', 'SUB15', 'SUB16', 'SUB17', 'SUB18', 'SUB19', 'SUB20', 'SUB21',
             'SUB22', 'SUB24']
PD_FZ = ['SUB01', 'SUB05', 'SUB07', 'SUB09', 'SUB10', 'SUB11', 'SUB12', 'SUB15', 'SUB17', 'SUB21', 'SUB22']
PD_NF = [s for s in PD_PAIRED if s not in PD_FZ]
assert len(PD_FZ) == 11 and len(PD_NF) == 11


# ---------- hea_mean 下肢（與 build_hoa.py 同一套做法）----------
J = {k: np.array(v['p']) for k, v in json.load(open(SKEL, encoding='utf-8'))['joints'].items()}


def Rz(a):
    c, s = np.cos(a), np.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def sole(g, i, side, ho):
    hip, knee, ank, sub, mtp = [J[k + '_' + side] for k in ('hip', 'knee', 'ankle', 'sub', 'mtp')]
    Rh = Rz(d2r(g['hip_flexion_' + side][i] + ho)); Rk = Rh @ Rz(d2r(g['knee_angle_' + side][i]))
    Pk = hip + Rh @ (knee - hip); Pa = Pk + Rk @ (ank - knee); Ra = Rk @ Rz(d2r(g['ankle_angle_' + side][i]))
    return min((Pa + Ra @ (sub - ank))[1] - 0.030, (Pa + Ra @ (mtp - ank))[1] - 0.020)


def best_hip(g, stance):
    best = None
    for ho in np.arange(-25, 15.5, 0.5):
        y = []
        for i in range(100):
            u = []
            if i < stance: u.append(sole(g, i, 'r', ho))
            if ((i + 50) % 100) < stance: u.append(sole(g, i, 'l', ho))
            y.append(-min(u) if u else np.nan)
        y = np.array(y); s = np.nanmax(y) - np.nanmin(y)
        if best is None or s < best[0]: best = (s, ho)
    return round(best[1], 1)


def hea_mean_clip():
    g = lambda S, part, ax: np.mean(np.array(list(bert('HEA', S, part, ax).values())), 0)
    pel_x, pel_y, thx_y = g('R', 'Pelvis', 'X'), g('R', 'Pelvis', 'Y'), g('R', 'Thorax', 'Y')
    tg = dm(thx_y)
    data = {'pelvis_tilt': r3(-dm(pel_x)), 'pelvis_list': r3(dm(pel_y)),
            'pelvis_rotation': Z, 'lumbar_extension': Z,
            'lumbar_bending': r3(tg - dm(pel_y)), 'lumbar_rotation': Z}
    for S, s in (('R', 'r'), ('L', 'l')):
        data['hip_flexion_' + s] = r3(g(S, 'Hip', 'X'))
        data['knee_angle_' + s] = r3(-g(S, 'Knee', 'X'))
        data['ankle_angle_' + s] = r3(g(S, 'Ankle', 'X'))
        data['hip_adduction_' + s] = r3(dm(g(S, 'Hip', 'Y')) - 3.0)
        data['hip_rotation_' + s] = Z; data['subtalar_angle_' + s] = Z; data['mtp_angle_' + s] = Z
    arms, n = bert_arms('HEA')
    data.update(arms)
    ho = best_hip(data, 60.0)
    return {'id': 'hea_mean',
            'label': '健康 Bertaux 對照組平均 ‧ n=%d ‧ 含手臂' % n,
            'group': '健康（Bertaux %d 人，含手臂）' % n,
            'meta': {'n': n, 'cohort': 'HEA', 'age': None},
            'period': 1.10, 'period_src': None,
            'period_note': '此資料集的文字檔版本未提供絕對時間軸，週期未知。播放固定 1.10 s，1× 不代表實際步速。',
            'source': 'Bertaux et al. 2022, Sci Data 9:399（CC BY 4.0）；Plug-in Gait',
            'note': '%d 位健康對照者逐點平均（每人先平均自己的週期）。下肢與手臂是同一批人同一次量到的，'
                    '是本工具唯一手臂與下肢同源的平均片段。' % n,
            'data': data, 'hip_offset': ho,
            'hip_offset_note': '髖角度為相對骨盆量測值。此 clip 施加常數偏移 %+.1f°（幾何閉合）。' % ho,
            'phase_l': 0.5, 'stance_r': 60.0, 'stance_l': 60.0,
            'stance_src': '假設 60%（此資料集未提供事件）',
            'events': [{'p': 0.0, 'label': '右足著地', 'short': 'R-IC', 'src': '資料集定義'}],
            'bands': [], 'stats': {}, 'align': '原始資料第 0 點即為右足著地',
            'arm': {'src': 'own', 'note': '手臂：本資料集實測（Plug-in Gait，n=%d）' % n}}


ARM_KEYS = ['shoulder_flexion_', 'shoulder_adduction_', 'shoulder_rotation_', 'elbow_flexion_', 'wrist_flexion_']


def main():
    m = json.load(open(MOTION, encoding='utf-8'))
    clips = {c['id']: c for c in m['clips']}
    if 'hea_mean' in clips or any(k.startswith('shoulder') for k in clips['vc_young']['data']):
        sys.exit('motion.json 已含手臂通道，不重複加')

    hea = hea_mean_clip()
    hea_arms = {k: hea['data'][k] for k in hea['data'] if any(k.startswith(p) for p in ARM_KEYS)}
    borrow_note = ('手臂：借用 Bertaux 健康對照組 80 人平均（本片段的資料集公開版無手臂資料）。'
                   '手臂與下肢不是同一批人，只示意正常擺臂的相位與幅度。')

    report = []
    for c in m['clips']:
        cid = c['id']
        if c.get('foot_only'):
            continue
        if cid.startswith('hoa_'):
            arms, _ = bert_arms('HOA', c['meta']['subject'])
            c['data'].update(arms)
            c['arm'] = {'src': 'own', 'note': '手臂：該受試者本人實測（Plug-in Gait）'}
        elif cid.startswith('pd_'):
            mt = c['meta']; st = mt['state'].lower()
            if mt.get('subject'): subjs = [mt['subject']]
            elif cid == 'pd_fz_off': subjs = PD_FZ
            elif cid == 'pd_nf_off': subjs = PD_NF
            else: subjs = PD_PAIRED
            assert len(subjs) == (mt.get('n') or 1), (cid, len(subjs), mt.get('n'))
            c['data'].update(pd_arms(subjs, st))
            c['arm'] = {'src': 'own', 'note': '手臂：本資料集實測（雙側肩、肘；腕無資料）' +
                        ('，%d 人平均' % len(subjs) if len(subjs) > 1 else '')}
        elif cid.startswith('stroke_'):
            c['arm'] = {'src': 'none', 'note': '手臂：此資料集公開版無手臂資料，且偏癱的手臂不該套用健康人的擺動，故手臂靜止不動。'}
        else:   # vc_*、mean_*、arch_walk_*
            c['data'].update(hea_arms)
            c['arm'] = {'src': 'borrowed', 'note': borrow_note}
        report.append((cid, c['arm']['src']))

    m['clips'].append(hea)
    m['compare_map']['hea_mean'] = 'hoa_108'
    json.dump(m, open(MOTION, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    for cid, src in report: print('  %-22s %s' % (cid, src))
    print('hea_mean 髖偏移 %+.1f°；motion.json 現有 %d 個片段' % (hea['hip_offset'], len(m['clips'])))


if __name__ == '__main__':
    main()
