#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把三組足弓資料（正常／旋前／旋後）分別接到同一段走路片段上，
做成可以邊走邊看足弓的合成片段。

為什麼要合成：
    足弓資料（Sanchis-Sales 2024）只有站立期、只有右腳、只有踝／中跗／第一蹠趾；
    走路資料（Van Criekinge 2023）有全身整個週期，但完全沒有足部分節。
    兩份資料來自不同受試者群，所以這是合成示範，不是同一個人身上量到的。

為什麼三組共用同一個身體：
    三個合成片段的身體完全相同，差別只在腳。這樣並排時看到的差異
    一定來自足部姿勢分組，不會混進不同走路資料的差異。

合成規則（只填空，不覆蓋）：
    1. 身體、骨盆、髖、膝、踝矢狀面  → 全部沿用走路片段的原始值，一個數字都不動
    2. 中跗三平面、第一蹠趾三平面、踝額狀面 → 走路片段原本就沒有這些通道，用足弓資料填入
    3. 站立期 0–100% 對應到走路週期的 0–61.4%（該片段的實測離地時間）
    4. 擺盪期沒有足部資料 → 由離地值以升餘弦平滑回到著地值，標示為模型補值

零位與閉合修正見 CLOSURE 的註解。
"""
import json, math, sys

REPO = '/home/claude/repo/build/'
BODY = 'vc_young'          # 身體來源：n=39、27.2 歲，與足弓三組（27–29 歲）年齡相近

# 要產生的合成片段：新 id → (足部來源, 顯示名稱)
GROUPS = [
    ('arch_walk_normal',    'arch_normal',    '正常足弓 走路中 ‧ 合成示範'),
    ('arch_walk_pronated',  'arch_pronated',  '旋前足（扁平） 走路中 ‧ 合成示範'),
    ('arch_walk_supinated', 'arch_supinated', '旋後足（高弓） 走路中 ‧ 合成示範'),
]

# 走路片段原本沒有、要由足弓資料填入的通道
GRAFT = ['midtarsal_df_r', 'midtarsal_inv_r', 'midtarsal_ab_r',
         'mtp1_df_r', 'mtp1_inv_r', 'mtp1_ab_r',
         'sub_angle_r']

FLAT = (20, 50)            # 站立期 20–50%：前足與後足都在地上的區間

# 中跗矢狀面的閉合修正（度）。
#
# 為什麼需要：本工具的足部以後足為錨點，中跗背屈會把前足抬起來（實測 1.44 mm/度），
# 而真人是前足踩著、足弓往下塌。只扣掉貼平段的平均還不夠，前足仍比原走路片段高，
# 足地接觸判定會誤報「僅腳跟著地」。
#
# 取值方式與既有的髖偏移相同，是幾何閉合條件：
#   「使足部貼平期間（原片段跟與前足皆在門檻內的 15–40%）前足不高於原片段」
#   成立的最小偏移。
# 由 solve_arch_walk.js 用無頭瀏覽器以 0.5° 為間隔掃描求得，不是手調的。
# 這是常數偏移，不影響擺幅、峰值大小與峰值時間。
CLOSURE = {
    'arch_walk_normal':    1.5,
    'arch_walk_pronated':  1.5,
    'arch_walk_supinated': 1.0,
}


def splice(stance_vals, to_pct):
    """把站立期的 101 點攤到整個步態週期的 101 點上。

    0 → to_pct      ：站立期，照實測資料重新取樣
    to_pct → 100    ：擺盪期，無資料，由離地值升餘弦回到著地值
    首尾相接（第 100 點 = 第 0 點），因為這次是完整週期，會一直循環播放。
    """
    out = []
    v_ic, v_to = stance_vals[0], stance_vals[100]
    for i in range(101):
        q = float(i)
        if q <= to_pct:
            x = q / to_pct * 100.0
            j = int(math.floor(x))
            f = x - j
            a = stance_vals[j]
            b = stance_vals[min(j + 1, 100)]
            out.append(a + (b - a) * f)
        else:
            u = (q - to_pct) / (100.0 - to_pct)
            out.append(v_to + (v_ic - v_to) * (1 - math.cos(math.pi * u)) / 2.0)
    out[100] = out[0]                      # 週期閉合，播放時首尾不跳變
    return [round(float(x), 3) for x in out]


def make(body, arch, new_id, label):
    to_pct = float(body['stance_r'])

    clip = json.loads(json.dumps(body))    # 深拷貝，確保身體資料一個數字都沒動
    clip['id'] = new_id
    clip['label'] = label
    clip['group'] = '足弓（走路中・合成）'
    clip['series'] = 'foot'                # 圖表改畫踝／中跗／第一蹠趾
    clip['composite'] = True
    clip['no_compare'] = True              # 髖膝的組間比較表無意義（三組身體相同）

    # 足弓資料的零位是「各受試者自己的放鬆站姿」，與 BodyParts3D 標本的參考姿勢
    # 不是同一個東西。處理方式與工具既有的骨盆零位對齊一致：
    # 只取相對「足部貼平那段」的變化量。擺幅是實測的，絕對角度不是。
    base = {}
    for k in GRAFT:
        seg = arch['data'][k][FLAT[0]:FLAT[1] + 1]
        base[k] = sum(seg) / len(seg)
    base['midtarsal_df_r'] += CLOSURE[new_id]

    for k in GRAFT:
        if k in clip['data']:
            sys.exit('通道 %s 在走路片段裡本來就有，不該覆蓋' % k)
        clip['data'][k] = splice([v - base[k] for v in arch['data'][k]], to_pct)

    am = arch['meta']
    clip['meta'] = {
        'cohort': 'composite',
        'body': 'Van Criekinge 2023 健康年輕組　n=%d　平均 %.1f 歲　步速 %s m/s'
                % (body['meta']['n'], body['meta']['age'], body['meta']['speed']),
        'foot': 'Sanchis-Sales 2024　%s　n=%d　%s　全部為男性'
                % (am.get('fpi', ''), am['n'], am['age']),
        'warn': '合成片段：身體與足部來自不同受試者群，不是同一個人身上量到的',
        'zero': '足部只取相對站立中期（足部貼平）的變化量；擺幅是實測的，絕對角度不是',
        'src': '身體 Van Criekinge 等 2023 ／ 足部 Sanchis-Sales 等 2024',
    }
    clip['note'] = (
        '這段是拼起來的：身體是一組人走路的資料，腳是另一組人的足弓資料，不是同一個人。'
        '身體的數字一個都沒改，腳是補上這份資料原本就沒有的中跗與第一蹠趾。'
        '三個合成片段的身體完全一樣，差別只在腳。'
        '腳的資料只有踩在地上那段（0–%.1f%%）；離地之後沒有資料，是平滑接回去的。'
        '角度看變化就好，絕對數字不要讀。'
        % to_pct
    )
    clip['source'] = (body['source'] + ' ＋ Sanchis-Sales E, Sancho-Bru JL, Roda-Sales A, '
                      'Chiva-Miralles MJ, García-Gomáriz C (2024). Sci Data 11:1307（CC BY 4.0）')
    clip['align'] = (body['align'] +
                     '；足部站立期 0–100%% 線性對應到週期 0–%.1f%%' % to_pct)
    return clip, base


def main():
    M = json.load(open(REPO + 'motion.json', encoding='utf-8'))
    C = {c['id']: c for c in M['clips']}
    body = C[BODY]

    # 重跑時先移除舊的合成片段，讓這支腳本可以重複執行
    old = [g[0] for g in GROUPS]
    M['clips'] = [c for c in M['clips'] if c['id'] not in old]

    for new_id, arch_id, label in GROUPS:
        clip, base = make(body, C[arch_id], new_id, label)
        M['clips'].append(clip)
        print('%-22s 足部取自 %-15s 中跗零位 %.2f°（含閉合修正 %.1f°）'
              % (new_id, arch_id, base['midtarsal_df_r'], CLOSURE[new_id]))

    # 三個合成片段互相對照（身體相同，疊上去看到的差異只來自足部）
    cm = M.setdefault('compare_map', {})
    cm['arch_walk_normal'] = 'arch_walk_pronated'
    cm['arch_walk_pronated'] = 'arch_walk_normal'
    cm['arch_walk_supinated'] = 'arch_walk_normal'

    json.dump(M, open(REPO + 'motion.json', 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))

    # 身體通道一個數字都不能動
    for new_id, _, _ in GROUPS:
        c = [x for x in M['clips'] if x['id'] == new_id][0]
        for k in body['data']:
            assert c['data'][k] == body['data'][k], '%s 的身體通道 %s 被改到了' % (new_id, k)
    print('\n身體 %d 個通道逐點比對：三個片段全部未改動' % len(body['data']))

    print('\n中跗矢狀面（足弓高低）站立期範圍，三組對照：')
    for new_id, arch_id, _ in GROUPS:
        c = [x for x in M['clips'] if x['id'] == new_id][0]
        v = c['data']['midtarsal_df_r'][:62]
        print('  %-22s 著地 %5.1f°  最大背屈 %5.1f°（足弓最低）  離地 %5.1f°'
              % (new_id, v[0], max(v), v[-1]))
    print('\n片段總數 %d' % len(M['clips']))


if __name__ == '__main__':
    main()
