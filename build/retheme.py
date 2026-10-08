#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把模板的配色換成練健康品牌色。

原則（為什麼不是整套換成藍＋橘）：
    工具裡橘色系已經有語意——#ffc46b 是關節標記，#ff8a6b 是警告
    （骨盆偏離過大、兩踝過近）。如果 UI 主色也用品牌橘，警告就不再跳出來。
    所以：底色／面板／線條／內文換成品牌色，主色留冷色，橘色只留給警告。

底色不用品牌原色 #2C4258，而是同色相的暗化版 #0F1A24。
原因是骨頭是米白 #dfe6e2，底色一亮就失去明暗落差，3D 的立體感會掉。
"""
import io, sys, re

# 舊色 → 新色。註解說明這個顏色在介面上是什麼東西。
MAP = [
    # ---- 淺色主題（左右面板）----
    ('#0b1113', '#0F1A24'),   # 3D 舞台底色 → 品牌深藍暗化版
    ('#f2f4f4', '#F4F2EE'),   # 面板底 → 紙色
    ('#e6eaea', '#EAE7E1'),   # 面板次底
    ('#ccd4d4', '#DDD8D0'),   # 分隔線
    ('#151b1d', '#2E4257'),   # 內文
    ('#5a6668', '#7D8A96'),   # 次要文字
    ('#0f8f86', '#3B5570'),   # 淺底主色 → 品牌次深藍

    # ---- 深色主題與 3D 疊加層 ----
    ('#141a1c', '#16232E'),   # 深色面板底
    ('#1c2426', '#1D2C3A'),   # 深色次底、播放列按鈕
    ('#2b3538', '#2A3B4C'),   # 深色邊框
    ('#e4eaea', '#E6EAEF'),   # 深底內文
    ('#8b9a9c', '#8FA0B0'),   # 深底次要文字
    ('#2fc4b6', '#8FB6D6'),   # 深底主色（數值、曲線）→ 淡品牌藍
    ('#06201e', '#0F1A24'),   # 主色上的字
    ('#9fb3b3', '#90A4B6'),   # HUD 次要文字
    ('#e8eeee', '#E6EAEF'),   # HUD 主文字
    ('#5f7477', '#627689'),   # 除錯列、圖表軸標
    ('#3a4a4d', '#3A4C5E'),   # 圖表零線
    ('#7f9496', '#7D8A96'),   # 圖表次要曲線
    ('#8aa0a2', '#90A4B6'),   # 載入遮罩說明文字
    ('#1b2a2c', '#1D2C3A'),   # 載入進度條底
    ('rgba(12,18,20,.8)', 'rgba(15,26,36,.82)'),
    ('rgba(11,17,19,.9)', 'rgba(15,26,36,.9)'),

    # ---- three.js 場景 ----
    ('0x0b1113', '0x0f1a24'),  # 場景背景
    ('0x0a1012', '0x0d1620'),  # 半球光下半
    ('0xcfeae6', '0xd8e4ee'),  # 半球光上半
    ('0x7fded2', '0x8fb6d6'),  # 補光
    ('0x4a6a6e', '0x3b5570'),  # 地面格線主線
    ('0x2c4144', '0x24323f'),  # 地面格線次線
]

# 這些顏色「不換」，而且要確認換完之後它們還在：
# 它們承載語意，被品牌色蓋掉就會失去辨識功能。
KEEP = {
    '#ffc46b': '關節標記與事件線（琥珀）',
    '#ff8a6b': '警告：骨盆偏離過大、兩踝距離過近',
    '#c98be0': '對照組曲線（紫）',
    '#e86a3a': '耦合圖第三平面',
    '#2a1113': '錯誤框底',
    '#7a2b30': '錯誤框邊',
    '#ffd9d5': '錯誤框文字',
    '0xdfe6e2': '骨頭材質',
    '0xffc46b': '關節標記球',
    '0xffffff': '環境光與主光',
}


def main():
    p = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/repo/build/template.html'
    s = io.open(p, encoding='utf-8').read()
    orig = s

    changed = []
    for old, new in MAP:
        # 顏色碼比對不分大小寫，但 rgba() 那種就照字面
        if old.startswith('#'):
            pat = re.compile(re.escape(old), re.I)
            n = len(pat.findall(s))
            s = pat.sub(new, s)
        else:
            n = s.count(old)
            s = s.replace(old, new)
        if n == 0:
            sys.stderr.write('  ! 找不到 %s，跳過\n' % old)
        else:
            changed.append((old, new, n))

    # 換完之後，語意色必須還在
    missing = [c for c in KEEP if c.lower() not in s.lower()]
    if missing:
        sys.exit('語意色消失了，中止：%s' % '、'.join(missing))

    # 換完之後，舊色不該有殘留
    leftover = [old for old, _, _ in changed
                if old.startswith('#') and re.search(re.escape(old), s, re.I)]
    if leftover:
        sys.exit('舊色仍有殘留，中止：%s' % '、'.join(leftover))

    io.open(p, 'w', encoding='utf-8').write(s)
    print('已換色 %d 組：' % len(changed))
    for old, new, n in changed:
        print('  %-20s → %-20s ×%d' % (old, new, n))
    print('語意色全部保留：%s' % '、'.join(sorted(KEEP)))
    print('模板由 %d 變為 %d 位元組' % (len(orig.encode()), len(s.encode())))


if __name__ == '__main__':
    main()
