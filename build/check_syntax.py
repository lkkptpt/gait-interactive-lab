#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第三道檢查：抽出 index.html 所有內嵌 <script>（不含 JSON 與外部檔）交給 node --check。

取代原本的 `node --check <(sed ...)`：那行會把一行寫完的 CDN 備援 <script> 連 HTML 一起抽出，
不論程式碼對錯都報 SyntaxError，等於從沒檢查過。
用法：python3 build/check_syntax.py index.html
"""
import re, subprocess, sys, tempfile
p = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
s = open(p, encoding='utf-8').read()
blocks = re.findall(r'<script>(.*?)</script>', s, re.S)
assert blocks, '找不到內嵌 script'
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
    f.write('\n;\n'.join(blocks)); fn = f.name
r = subprocess.run(['node', '--check', fn], capture_output=True, text=True)
if r.returncode:
    print('✗ JS 語法錯誤\n' + r.stderr); sys.exit(1)
print('✓ JS 語法檢查通過（%d 個內嵌 script）' % len(blocks))
