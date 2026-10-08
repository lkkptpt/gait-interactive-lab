import sys, re
t=open(sys.argv[1],encoding='utf-8').read()
DEFS=['computeRef','setClip','fmtMeta','buildCmpTable','buildCharts','drawTimeline','applyVis',
      'pair','slab','setOff','contactState','pelvisDev','groundOffset','buildGProf','lowest',
      'probeY','drawCoupling','updCharts','cmpClip','clipById','pose','setJ','setAxisJ','subAxis',
      'ankAxis','rebuildAxes','decomp','offAt','samp','placeCam','pick','fit','tick','phaseName',
      'nearEvent','build','applyWeak','ankleGap','screwHome','mtpModel','ptrList','endPtr']
miss=[f for f in DEFS
      if re.search(r'(?<![\w.])'+f+r'\s*\(',t) and not re.search(r'function\s+'+f+r'\s*\(',t)]
if miss: print('✗ 有呼叫但無定義:',miss); sys.exit(1)
for a in ['CLIPS.forEach','setClip(CLIP.id)','optgroup','compare_map','cycChk','symChk']:
    if a not in t: print('✗ 缺少:',a); sys.exit(1)
print('✓ 建置後檢查通過（%d 個函式定義齊全）'%sum(1 for f in DEFS if 'function '+f in t))
