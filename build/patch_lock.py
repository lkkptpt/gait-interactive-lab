#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""兩個修正：

1. 「腳一直在動」
   目前的足部視角是把鏡頭對準距骨，距骨會隨著走路上下前後跑，
   鏡頭只能一直追，看起來整隻腳都在飄。要研究足弓的時候很難盯。

   新增「定住」視角：鏡頭改放在跟骨自己的座標系裡，跟骨因此在畫面上
   完全不動，看到的就只有前足相對後足的變化——也就是真正要看的東西。

2. 「還是太快」
   8 秒播完整段，但真正有事情發生的推進期只佔週期的 10%，
   等於 0.8 秒就過去了。加一個 60 秒檔。
"""
import io, sys

P = '/home/claude/repo/build/template.html'
s = io.open(P, encoding='utf-8').read()
orig = s


def rep(old, new, n=1, what=''):
    global s
    c = s.count(old)
    if c != n:
        sys.exit('錨點「%s」出現 %d 次，預期 %d 次' % (what or old[:40], c, n))
    s = s.replace(old, new)


# ---- 1) 定住視角 ----
rep("""      <button data-zoom="foot">足部</button>""",
    """      <button data-zoom="foot">足部</button>
      <button data-zoom="lock" title="鏡頭跟著跟骨走，腳在畫面上不動">定住</button>""",
    what='定住按鈕')

rep("""  if(zoomMode==='foot'){
    nodes.talus_r.getWorldPosition(tmp);
    tmp.y=Math.min(tmp.y,yMax);
    if(target.distanceTo(tmp)>0.004) target.lerp(tmp,0.06);
  }""",
    """  if(zoomMode==='lock'){
    // 把鏡頭放進跟骨自己的座標系：跟骨在畫面上完全不動，
    // 看到的就只有前足相對後足的變化。研究足弓時不會被整隻腳的位移干擾。
    var fn=nodes['foot_'+archSide] || nodes.foot_r;
    _lkT.set(0.055, 0.010, 0);                  // 看向足部中段（跟骨座標系）
    fn.localToWorld(_lkT);
    _lkP.set(0.055 + rad*Math.sin(pol)*Math.sin(az),
             0.010 + rad*Math.cos(pol),
             rad*Math.sin(pol)*Math.cos(az));
    fn.localToWorld(_lkP);
    camera.position.copy(_lkP);
    _lkU.set(0,1,0).applyQuaternion(fn.getWorldQuaternion(_lkQ));
    camera.up.copy(_lkU);
    camera.lookAt(_lkT);
    target.copy(_lkT);
    return;
  }
  camera.up.set(0,1,0);
  if(zoomMode==='foot'){
    nodes.talus_r.getWorldPosition(tmp);
    tmp.y=Math.min(tmp.y,yMax);
    if(target.distanceTo(tmp)>0.004) target.lerp(tmp,0.06);
  }""", what='定住視角')

rep("""var drag=null, ptrs={}, pinch=null;""",
    """var _lkT=new THREE.Vector3(), _lkP=new THREE.Vector3(),
    _lkU=new THREE.Vector3(), _lkQ=new THREE.Quaternion();
var drag=null, ptrs={}, pinch=null;""", what='定住暫存變數')

rep("""grp('#zoomBtns button',function(b){zoomMode=b.dataset.zoom;
  rad=zoomMode==='foot'?0.45:(zoomMode==='leg'?1.6:3.5);});""",
    """grp('#zoomBtns button',function(b){zoomMode=b.dataset.zoom;
  rad=(zoomMode==='foot'||zoomMode==='lock')?0.45:(zoomMode==='leg'?1.6:3.5);});""",
    what='定住的鏡頭距離')

# 重設鏡頭時也要把 up 轉回來，否則離開定住視角畫面會是歪的
rep("""  az=0; pol=84*D2R; rad=3.5; zoomMode='body'; target.set(0.09,0.95,0);""",
    """  az=0; pol=84*D2R; rad=3.5; zoomMode='body'; target.set(0.09,0.95,0);
  camera.up.set(0,1,0);""", what='重設鏡頭的 up')

# ---- 2) 60 秒檔 ----
rep("""          <button data-sec="20" title="整段播完 20 秒">20s</button>""",
    """          <button data-sec="60" title="整段播完 60 秒">60s</button>
          <button data-sec="20" title="整段播完 20 秒">20s</button>""",
    what='60 秒檔')
rep("""          <button data-speed="0.25">0.25×</button>\n""", "", what='移除 0.25 倍率')

io.open(P, 'w', encoding='utf-8').write(s)
print('已加入定住視角與 60 秒檔（%d → %d 位元組）' % (len(orig.encode()), len(s.encode())))
