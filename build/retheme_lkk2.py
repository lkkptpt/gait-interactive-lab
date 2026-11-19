#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v1.13.0：配色與字體改用練健康品牌規範（design system）的正式色值。

沿用 retheme.py 的原則：
    資料語意色不換——#ffc46b 關節標記／事件線、#ff8a6b 警告、#c98be0 對照組、
    #e86a3a 耦合圖第三平面、骨頭材質 0xdfe6e2。被品牌色蓋掉就失去辨識功能。
    品牌只換「介面外殼」：面板、按鈕、線條、內文、3D 舞台底色、HUD 中性色。

色值來源（品牌規範）：
    strength #00547A（主色）、warmth #F2EDE0、trust #585657、science #FFFFFF、
    energy #F37200（只用在非文字元素：此處只用在載入進度條）。
    以下為同色相推得值（品牌沒有提供深色／淡色階）：
    #062433 舞台底（strength 暗化，骨頭米白要有明暗落差）、
    #0A2B3B／#0F3649／#1E4A5F 深色主題面板層、#7DBAD6 深底上的主色（strength 淡化）。
    #646162 次要文字（trust 加深，確保在 warmth 底上 ≥4.5:1）。

字體：標題 Noto Serif TC Black；其餘 Noto Sans TC（數字用 tabular-nums 對齊），
IBM Plex Mono 只留在錯誤框（除錯用）。
"""
import io, re, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'template.html'
s = io.open(P, encoding='utf-8').read()


def sub1(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, '預期 %d 處，實際 %d：%s' % (count, n, old[:60])
    s = s.replace(old, new)


# ---- 1. :root 色票整段換掉 ----
root_old = s[s.index(':root{--stage'):s.index('*{box-sizing')]
root_new = (
    ':root{--stage:#062433;--surface:#FFFFFF;--surface-2:#F2EDE0;--line:#E0D8C6;\n'
    '  --ink:#585657;--ink-2:#646162;--ink-heading:#00547A;--accent:#00547A;--accent-ink:#fff;--radius:3px}\n'
    '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){\n'
    '  --surface:#0A2B3B;--surface-2:#0F3649;--line:#1E4A5F;--ink:#F2EDE0;--ink-2:#A3B4BE;\n'
    '  --ink-heading:#F2EDE0;--accent:#7DBAD6;--accent-ink:#062433}}\n'
    ':root[data-theme="dark"]{--surface:#0A2B3B;--surface-2:#0F3649;--line:#1E4A5F;\n'
    '  --ink:#F2EDE0;--ink-2:#A3B4BE;--ink-heading:#F2EDE0;--accent:#7DBAD6;--accent-ink:#062433}\n')
s = s.replace(root_old, root_new)

# ---- 2. 字體 ----
sub1('family=Noto+Sans+TC:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500',
     'family=Noto+Sans+TC:wght@400;500;700;900&family=Noto+Serif+TC:wght@900&family=IBM+Plex+Mono:wght@400')
sub1('font-size:14px;line-height:1.6;\n', 'font-size:14px;line-height:1.6;font-variant-numeric:tabular-nums;\n')
sub1('h1{font-size:15px;font-weight:700;margin:0 0 2px}',
     'h1{font-family:"Noto Serif TC",serif;font-size:17px;font-weight:900;color:var(--ink-heading);margin:0 0 2px;letter-spacing:.02em}')
sub1('h2{font-size:12px;font-weight:700;', 'h2{font-size:12px;font-weight:700;color:var(--ink-heading);')
err = '#err{'
head, tail = s.split(err, 1)
errblk, rest = tail.split('}', 1)
head = head.replace('"IBM Plex Mono",monospace', '"Noto Sans TC",sans-serif')
rest = rest.replace('"IBM Plex Mono",monospace', '"Noto Sans TC",sans-serif')
rest = rest.replace("'IBM Plex Mono',monospace", "'Noto Sans TC',sans-serif")
s = head + err + errblk + '}' + rest

# ---- 3. 載入畫面 ----
sub1('.boot-quote{color:#C9D6E2', '.boot-quote{color:#E4DFD2')
sub1('.boot-by{color:#7D8A96', '.boot-by{color:#9DB3BF')
sub1('.boot-title{color:var(--accent);font-size:15px;font-weight:600;letter-spacing:.04em}',
     '.boot-title{color:#F2EDE0;font-family:"Noto Serif TC",serif;font-size:20px;font-weight:900;letter-spacing:.06em}')
sub1('.boot-bar i{display:block;height:100%;width:40%;background:var(--accent);',
     '.boot-bar i{display:block;height:100%;width:40%;background:#F37200;')  # energy：非文字元素
sub1("stroke=\"'+(idx?'#7D8A96':", "stroke=\"'+(idx?'#8C9CA5':")  # 圖表次要虛線（深底）

# ---- 4. 舞台與疊加層中性色（全部出現處一起換）----
MAP = [
    ('#0F1A24', '#062433'), ('#8FB6D6', '#7DBAD6'), ('#1D2C3A', '#0F3649'),
    ('#2A3B4C', '#1E4A5F'), ('#90A4B6', '#9DB3BF'), ('#627689', '#5F8091'),
    ('#3A4C5E', '#2A5468'), ('#E6EAEF', '#F2EDE0'), ('rgba(15,26,36,', 'rgba(6,36,51,'),
    ('0x0f1a24', '0x062433'), ('0x0d1620', '0x041c28'), ('0x8fb6d6', '0x7dbad6'),
    ('0x3b5570', '0x1f5a78'), ('0x24323f', '0x0f3346'),
]
for old, new in MAP:
    pat = re.compile(re.escape(old), re.I)
    n = len(pat.findall(s))
    s = pat.sub(new, s)
    print('%-16s → %-14s %2d 處' % (old, new, n))

# ---- 5. 語意色必須原封不動 ----
for k in ['#ffc46b', '#ff8a6b', '#c98be0', '#e86a3a', '0xdfe6e2', '0xffc46b']:
    assert k in s.lower(), '語意色被換掉了：' + k
for k in ['#2E4257', '#3B5570', '#F4F2EE', '#16232E']:
    assert k.lower() not in s.lower(), '舊品牌色殘留：' + k

# ---- 6. 版號 ----
sub1('<title>步態互動實驗室 v1.12.3</title>', '<title>步態互動實驗室 v1.13.0</title>')
sub1('<p class="sub">v1.12.3 ·', '<p class="sub">v1.13.0 ·')

io.open(P, 'w', encoding='utf-8').write(s)
print('完成')
