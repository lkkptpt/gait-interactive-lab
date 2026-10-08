import re, sys
t=open(sys.argv[1],encoding='utf-8').read()
m=re.search(r'<script>\nfunction showErr[\s\S]*?\n\}\)\(\);\n</script>', t)
src=m.group(0) if m else t
funcs={}
for fm in re.finditer(r'function\s+(\w+)\s*\([^)]*\)\s*\{', src):
    name=fm.group(1); i=fm.end()-1; depth=0
    for j in range(i,len(src)):
        if src[j]=='{': depth+=1
        elif src[j]=='}':
            depth-=1
            if depth==0: break
    funcs[name]=src[i:j+1]
calls={f:set() for f in funcs}
for f,body in funcs.items():
    for cm in re.finditer(r'(?<![\w.])(\w+)\s*\(', body):
        g=cm.group(1)
        if g in funcs and g!=f: calls[f].add(g)
cycles=[]
def dfs(n,path,seen):
    for g in calls[n]:
        if g in path:
            cyc=path[path.index(g):]+[g]
            if len(cyc)>2 and cyc not in cycles: cycles.append(cyc)
        elif g not in seen:
            seen.add(g); dfs(g,path+[g],seen)
for f in funcs: dfs(f,[f],{f})
GUARDS=['GBUILD','building','_busy','inBuild']
bad=[c for c in cycles if not any(any(g in funcs[n] for g in GUARDS) for n in c[:-1])]
if bad:
    print('✗ 發現無阻斷旗標的呼叫環：')
    for c in bad[:6]: print('   '+' → '.join(c))
    sys.exit(1)
print('✓ 呼叫環檢查通過（%d 個環，全部有阻斷旗標或為安全遞迴）'%len(cycles))
