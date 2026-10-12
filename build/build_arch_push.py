#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推進期放大片段：把站立期的最後 30% 單獨拉出來，重新攤成完整的 0–100%。

為什麼要做：
    三組足型的差異幾乎全部集中在推進期。站立期 0–85% 三組差不到 1°，
    85–100% 中跗差 7.9°、第一蹠趾差 12.8°（Cohen d ≈ 1.9）。
    在完整片段裡，這段只佔整個步態週期的 9%，一眨眼就過去，看不出來。
    把它攤開之後，整條時間軸、整張圖表都是這一段。

這是「重新取樣」，不是「新資料」：
    數值一個都沒改，只是把 x 軸從「站立期 70–100%」線性拉伸成「0–100%」。
    介面上會標示原本的站立期百分比，不會讓人誤以為這是完整站立期。
"""
import json, math, sys

REPO = '/home/claude/repo/build/'
SRC = [
    ('arch_push_normal',    'arch_normal',    '正常足'),
    ('arch_push_pronated',  'arch_pronated',  '旋前足（扁平）'),
    ('arch_push_supinated', 'arch_supinated', '旋後足（高弓）'),
]
LO, HI = 70, 100           # 取站立期的這一段


def zoom(vals):
    """把 vals[LO..HI] 線性重新取樣成 101 點。數值不改，只改時間軸。"""
    out = []
    for i in range(101):
        x = LO + (HI - LO) * i / 100.0
        j = int(math.floor(x))
        f = x - j
        a = vals[j]
        b = vals[min(j + 1, 100)]
        out.append(round(float(a + (b - a) * f), 3))
    return out


def main():
    M = json.load(open(REPO + 'motion.json', encoding='utf-8'))
    C = {c['id']: c for c in M['clips']}

    new_ids = [s[0] for s in SRC]
    M['clips'] = [c for c in M['clips'] if c['id'] not in new_ids]

    for new_id, src_id, name in SRC:
        src = C[src_id]
        clip = json.loads(json.dumps(src))
        clip['id'] = new_id
        clip['label'] = '%s 推進期放大 ‧ n=%d' % (name, src['meta']['n'])
        clip['group'] = '推進期放大（站立期 %d–%d%%）' % (LO, HI)
        clip['data'] = {k: zoom(v) for k, v in src['data'].items()}
        if 'sd' in clip:
            clip['sd'] = {k: zoom(v) for k, v in src['sd'].items()}

        clip['pct_label'] = '推進期'
        clip['period'] = round(src['period'] * (HI - LO) / 100.0, 3)
        clip['period_note'] = ('顯示用的名目長度，依原片段 %.2f s 的 %d%% 換算；'
                               '資料集未提供絕對時間，1× 不代表實際步速'
                               % (src['period'], HI - LO))
        clip['events'] = [
            {'p': 0.0,   'label': '站立期 %d%%' % LO, 'short': '%d%%' % LO,
             'src': '原片段的時間軸位置'},
            {'p': 100.0, 'label': '右足離地', 'short': 'R-TO',
             'src': '資料集定義（站立期終點）'},
        ]
        clip['bands'] = [{'a': 0.0, 'b': 100.0}]
        clip['note'] = (
            '這是放大鏡，不是新資料。把原本站立期 %d–%d%% 這一段，'
            '橫軸拉開成完整的 0–100%%，數值一個都沒改。'
            '三組足型的差別幾乎全部在這一段——前面 %d%% 三組差不到 1°。'
            '左右兩端對應的是原片段的站立期 %d%% 與離地那一刻。'
            % (LO, HI, LO, LO)
        )
        clip['align'] = ('原片段站立期 %d–%d%% 線性拉伸為 0–100%%，未改動任何數值' % (LO, HI))
        clip['no_compare'] = True
        M['clips'].append(clip)

    cm = M.setdefault('compare_map', {})
    cm['arch_push_normal'] = 'arch_push_pronated'
    cm['arch_push_pronated'] = 'arch_push_normal'
    cm['arch_push_supinated'] = 'arch_push_normal'

    json.dump(M, open(REPO + 'motion.json', 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))

    print('推進期放大片段（站立期 %d–%d%%）\n' % (LO, HI))
    hdr = '%-16s %10s %10s %10s' % ('', '起點', '終點(離地)', '全段變化')
    for ch, cn in [('midtarsal_df_r', '中跗（足弓）'), ('mtp1_df_r', '第一蹠趾')]:
        print('%s：%s' % (cn, hdr))
        base = None
        for new_id, _, name in SRC:
            v = [x for x in M['clips'] if x['id'] == new_id][0]['data'][ch]
            line = '  %-16s %9.1f° %9.1f° %9.1f°' % (name, v[0], v[-1], v[-1] - v[0])
            if base is None:
                base = v
            else:
                line += '   與正常差 %+.1f°' % (v[-1] - base[-1])
            print(line)
        print()
    print('片段總數 %d' % len(M['clips']))


if __name__ == '__main__':
    main()
