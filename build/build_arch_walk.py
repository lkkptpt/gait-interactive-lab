#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把「正常足弓」的足部資料接到一段走路片段上，做成可以邊走邊看足弓的合成片段。

為什麼要合成：
    足弓資料（Sanchis-Sales 2024）只有站立期、只有右腳、只有踝／中跗／第一蹠趾；
    走路資料（Van Criekinge 2023）有全身整個週期，但完全沒有足部分節。
    兩份資料來自不同受試者群，所以這是合成示範，不是同一個人身上量到的。

合成規則（只填空，不覆蓋）：
    1. 身體、骨盆、髖、膝、踝矢狀面  → 全部沿用走路片段的原始值，一個數字都不動
    2. 中跗三平面、第一蹠趾三平面、踝額狀面 → 走路片段原本就沒有這些通道，用足弓資料填入
    3. 站立期 0–100% 對應到走路週期的 0–61.4%（該片段的實測離地時間）
    4. 擺盪期沒有足部資料 → 由離地值以升餘弦平滑回到著地值，標示為模型補值
"""
import json, math, sys

REPO = '/home/claude/repo/build/'
BODY = 'vc_young'          # 身體來源：n=39、27.2 歲，與足弓組（n=30、27.3 歲）年齡相近
ARCH = 'arch_normal'       # 足部來源：FPI 判定為正常足的 30 人

# 走路片段原本沒有、要由足弓資料填入的通道
GRAFT = ['midtarsal_df_r', 'midtarsal_inv_r', 'midtarsal_ab_r',
         'mtp1_df_r', 'mtp1_inv_r', 'mtp1_ab_r',
         'sub_angle_r']


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


def main():
    M = json.load(open(REPO + 'motion.json', encoding='utf-8'))
    C = {c['id']: c for c in M['clips']}

    if 'arch_walk_normal' in C:
        sys.exit('片段已存在，請先移除再重跑')

    body, arch = C[BODY], C[ARCH]
    to_pct = float(body['stance_r'])

    clip = json.loads(json.dumps(body))    # 深拷貝，確保身體資料一個數字都沒動
    clip['id'] = 'arch_walk_normal'
    clip['label'] = '正常足弓 走路中 ‧ 合成示範'
    clip['group'] = '足弓（走路中・合成）'
    clip['series'] = 'foot'                # 圖表改畫踝／中跗／第一蹠趾
    clip['composite'] = True
    clip['no_compare'] = True

    # 足弓資料的零位是「各受試者自己的放鬆站姿」，與 BodyParts3D 標本的參考姿勢
    # 不是同一個東西，直接套上去會讓前足在站立中期浮起來。
    # 處理方式與工具既有的骨盆零位對齊一致：只取相對「足部貼平那段」的變化量。
    # 擺幅是實測的，絕對角度不是。
    #
    # 中跗矢狀面再多扣一個閉合修正：本工具的足部以後足為錨點，中跗背屈會把前足
    # 抬起來（實測 1.44 mm/度），而真人是前足踩著、足弓往下塌。扣掉平均之後
    # 前足在貼平段仍比原片段高 1.1 mm，判定會誤報「僅腳跟著地」。
    # 取值方式與既有的髖偏移相同，是幾何閉合條件：
    #   「使足部貼平期間（原片段跟與前足皆在門檻內的 15–40%）前足不高於原片段」
    #   成立的最小偏移。無頭瀏覽器掃描 0 至 −2.5°，實測 −1.0° 為臨界值。
    # 這是常數偏移，不影響擺幅與峰值時間。
    FLAT = (20, 50)          # 站立期 20–50%，前足與後足都在地上的區間
    MT_CLOSURE = 1.0
    base = {}
    for k in GRAFT:
        seg = arch['data'][k][FLAT[0]:FLAT[1] + 1]
        base[k] = sum(seg) / len(seg)
    base['midtarsal_df_r'] += MT_CLOSURE

    for k in GRAFT:
        if k in clip['data']:
            sys.exit('通道 %s 在走路片段裡本來就有，不該覆蓋' % k)
        zeroed = [v - base[k] for v in arch['data'][k]]
        clip['data'][k] = splice(zeroed, to_pct)

    clip['meta'] = {
        'cohort': 'composite',
        'body': 'Van Criekinge 2023 健康年輕組　n=%d　平均 %.1f 歲　步速 %s m/s'
                % (body['meta']['n'], body['meta']['age'], body['meta']['speed']),
        'foot': 'Sanchis-Sales 2024 正常足（FPI 0–5）　n=%d　%s　全部為男性'
                % (arch['meta']['n'], arch['meta']['age']),
        'warn': '合成片段：身體與足部來自不同受試者群，不是同一個人身上量到的',
        'zero': '足部只取相對站立中期（足部貼平）的變化量；擺幅是實測的，絕對角度不是',
        'src': '身體 Van Criekinge 等 2023 ／ 足部 Sanchis-Sales 等 2024',
    }
    clip['note'] = (
        '這段是拼起來的：身體是一組人走路的資料，腳是另一組人的足弓資料，不是同一個人。'
        '身體的數字一個都沒改，腳是補上這份資料原本就沒有的中跗與第一蹠趾。'
        '腳的資料只有踩在地上那段（0–%.1f%%）；離地之後沒有資料，是平滑接回去的。'
        '角度看變化就好，絕對數字不要讀。'
        % to_pct
    )
    clip['source'] = (body['source'] + ' ＋ Sanchis-Sales E, Sancho-Bru JL, Roda-Sales A, '
                      'Chiva-Miralles MJ, García-Gomáriz C (2024). Sci Data 11:1307（CC BY 4.0）')
    clip['align'] = (body['align'] +
                     '；足部站立期 0–100%% 線性對應到週期 0–%.1f%%' % to_pct)

    M['clips'].append(clip)
    json.dump(M, open(REPO + 'motion.json', 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))

    print('已加入 arch_walk_normal（身體 %s ＋ 足部 %s）' % (BODY, ARCH))
    print('離地 %.1f%%，站立期佔週期 %.1f%%\n' % (to_pct, to_pct))
    for k in GRAFT:
        v = clip['data'][k]
        s = arch['data'][k]
        print('  %-16s 站立期實測 %6.1f→%6.1f  合成後週期 %6.1f→%6.1f  峰值 %6.1f'
              % (k, s[0], s[100], v[0], v[100], max(v, key=abs)))
    body_keys = set(body['data'])
    assert all(clip['data'][k] == body['data'][k] for k in body_keys), '身體通道被改到了'
    print('\n身體 %d 個通道逐點比對：完全未改動' % len(body_keys))


if __name__ == '__main__':
    main()
