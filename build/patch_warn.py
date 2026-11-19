#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v1.13.1：補上從未定義的 --warn。

介面 16 處用 var(--warn) 標「借用／模型／未知」，但 :root 從沒定義這個變數，
一直顯示成一般內文色，違反「實測／推得／模型要分開標示」。
色值沿用 3D 畫面上既有的警告色 #ff8a6b；淺色面板上 #ff8a6b 對比只有 2.0:1，
改用同色系加深的 #A8430F（白底 6.0:1、warmth 底 5.2:1）。
3D 舞台永遠是深底，所以 .stage 內固定 #ff8a6b（舞台底 7.0:1）。
"""
import io, sys
P = sys.argv[1] if len(sys.argv) > 1 else 'template.html'
s = io.open(P, encoding='utf-8').read()
def sub1(o, n):
    global s
    assert s.count(o) == 1, o
    s = s.replace(o, n)
sub1('--ink-heading:#00547A;--accent:#00547A;--accent-ink:#fff;',
     '--ink-heading:#00547A;--accent:#00547A;--accent-ink:#fff;--warn:#A8430F;')
assert s.count('--accent:#7DBAD6;--accent-ink:#062433') == 2
s = s.replace('--accent:#7DBAD6;--accent-ink:#062433', '--accent:#7DBAD6;--accent-ink:#062433;--warn:#ff8a6b')
sub1('.stage{position:relative;', '.stage{--warn:#ff8a6b;position:relative;')
sub1('<title>步態互動實驗室 v1.13.0</title>', '<title>步態互動實驗室 v1.13.1</title>')
sub1('<p class="sub">v1.13.0 ·', '<p class="sub">v1.13.1 ·')
io.open(P, 'w', encoding='utf-8').write(s)
print('完成')
# 另：「週期（未知…）」原本包在 opacity:.7 的 span 裡，警告色被淡化到對比不足，
# 已在 template.html 手動把它移出該 span（一處，見 v1.13.1 commit）。
