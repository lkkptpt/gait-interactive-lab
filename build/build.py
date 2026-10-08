#!/usr/bin/env python3
"""把資料檔塞進模板，產生單一可離線開啟的 HTML。

用法：python3 build.py [輸出檔名]
預設輸出 ../index.html（GitHub Pages 直接吃這個檔）。
"""
import json, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'index.html')

tpl = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
for tag, fn in (('ANATOMY', 'anatomy.json'), ('SKELETON', 'skeleton.json'), ('MOTION', 'motion.json')):
    data = json.load(open(os.path.join(HERE, fn), encoding='utf-8'))
    ph = '__%s__' % tag
    assert ph in tpl, '模板缺少佔位符 ' + ph
    tpl = tpl.replace(ph, json.dumps(data, ensure_ascii=False, separators=(',', ':')))

open(OUT, 'w', encoding='utf-8').write(tpl)
print('已輸出 %s（%.2f MB）' % (OUT, len(tpl.encode()) / 1048576))
