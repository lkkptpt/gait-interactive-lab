#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更正兩處過時的腳踝說明。

查核結果（讀 code，非猜測）：
  - setAxisJ('sub_r'/'ankle_r') 繞 AXIS[...] 旋轉，AXIS 由 subAxis()/ankAxis() 建立，
    參數 AXP={sub:{incl:42,dev:23}, ank:{down:8,post:6}}，就是 Inman 1976 的斜軸，
    關節面板還能切換 Gait2392／van den Bogert 參數。
    → 「距下關節目前以正交軸近似，尚未採用 Inman 斜軸」這句是舊版留下來的，與程式不符。
  - sub_r/sub_l 的標籤寫「無資料」，但足弓片段（arch_*、arch_walk_*、arch_push_*）
    有 sub_angle_r 通道而且 pose() 真的拿來轉。
    → 改成「僅足弓片段有資料」。
"""
import io, sys

P = '/home/claude/repo/build/template.html'
s = io.open(P, encoding='utf-8').read()


def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: sys.exit('錨點「%s」出現 %d 次，預期 %d 次' % (old[:40], c, n))
    s = s.replace(old, new)


rep('距下關節目前以正交軸近似，尚未採用 Inman 斜軸。原始 IK 未追蹤距下與蹠趾，只能手動操作。',
    '距腿與距下關節皆繞 Inman 1976 的斜軸旋轉（參數可在關節面板調整），但距下關節只有足弓片段有實測資料'
    '（Sanchis-Sales 的後足相對小腿角），其餘片段的距下與蹠趾未被原始資料追蹤，只能手動操作。'
    '各資料集的踝關節額狀面與水平面角度（Plug-in Gait 的 Y／Z）未採用：這兩個角度的量測信度低、各實驗室定義不一，本工具不拿它們驅動距下關節。')
rep("label:'距下關節（右）· 無資料'", "label:'距下關節（右）· 僅足弓片段有資料'")
rep("label:'距下關節（左）· 無資料'", "label:'距下關節（左）· 僅足弓片段有資料'")
io.open(P, 'w', encoding='utf-8').write(s)

R = '/home/claude/repo/README.md'
r = io.open(R, encoding='utf-8').read()
old = '- 距下關節以正交軸近似，尚未採用 Inman 斜軸\n'
assert r.count(old) == 1
r = r.replace(old, '- 距腿與距下關節繞 Inman 1976 斜軸旋轉（可調），但距下關節只有足弓片段有實測資料，其餘片段只能手動操作；'
                   '各資料集的踝額狀面／水平面角度（信度低、定義不一）未採用\n')
io.open(R, 'w', encoding='utf-8').write(r)
print('腳踝說明已更正')
