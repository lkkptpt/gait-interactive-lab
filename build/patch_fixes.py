#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""四個修正：

1. 貼地按鈕看過「只有腳」的片段之後回不來
   setClip 裡只有 c.foot_only 時把 groundOn 關掉，沒有在切回全身片段時打開。
   結果是看過站立期片段之後，所有片段的貼地都是關的，接觸狀態列也跟著空白。

2. 點畫面不會暫停
   點到骨頭時切換透明（原本行為保留），點到空白處改為暫停／繼續。

3. 足弓指示只在有足部資料的片段才出得來
   足弓是由骨骼幾何算的，任何片段都算得出來。改成按鈕隨時可按；
   片段沒有足部資料時，明確標示「此片段無足部資料，足弓不會變化」。

4. 足弓的線太細看不到
   WebGL 的 linewidth 永遠是 1 像素，再怎麼設都沒用。改用細圓柱體畫，
   才真的有粗細。
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


# ---- 1) 貼地狀態要能回復 ----
rep("""  if(c.foot_only){
    groundOn=false;
    var gb=document.getElementById('gndToggle'); if(gb) gb.classList.remove('on');
    zoomMode='foot'; rad=0.45;
    document.querySelectorAll('#zoomBtns button').forEach(function(x){
      x.classList.toggle('on', x.dataset.zoom==='foot'); });
  }""",
    """  // 只有腳的片段沒有骨盆與髖膝，貼地閉合無從算起，暫時關掉；
  // 切回有全身資料的片段時必須打開回來，否則接觸狀態列會一直是空的。
  var gb=document.getElementById('gndToggle');
  if(c.foot_only){
    groundOn=false;
    if(gb) gb.classList.remove('on');
    zoomMode='foot'; rad=0.45;
    document.querySelectorAll('#zoomBtns button').forEach(function(x){
      x.classList.toggle('on', x.dataset.zoom==='foot'); });
  } else {
    groundOn=true;
    if(gb) gb.classList.add('on');
  }""", what='貼地狀態回復')

# ---- 2) 點空白處暫停 ----
rep("""  var h=ray.intersectObjects(meshes,false); if(!h.length)return;""",
    """  var h=ray.intersectObjects(meshes,false);
  if(!h.length){                      // 點到空白處：暫停／繼續
    var pb=document.getElementById('play');
    if(pb) pb.click();
    return;
  }""", what='點空白處暫停')

# ---- 3) 足弓指示不再綁定片段 ----
rep("""  archSide = c.side || 'r';
  var _wantArch = !!(c.data && c.data['midtarsal_df_'+archSide]);
  if(_wantArch!==archOn){
    archOn=_wantArch;
    var ab=document.getElementById('archToggle');
    if(ab) ab.classList.toggle('on',archOn);
  }
  computeArchRef();""",
    """  archSide = c.side || 'r';
  // 有足部資料的片段自動打開足弓指示；其餘片段保留使用者自己的設定，
  // 按鈕任何片段都能按（足弓是由幾何算的，不需要資料也畫得出來）。
  if(c.data && c.data['midtarsal_df_'+archSide] && !archOn){
    archOn=true;
    var ab=document.getElementById('archToggle');
    if(ab) ab.classList.add('on');
  }
  computeArchRef();""", what='足弓不綁片段')

rep("""  txt+='　弓角 '+ang.toFixed(1)+'°<span style="opacity:.6">　模型推算</span>';
  return txt;""",
    """  txt+='　弓角 '+ang.toFixed(1)+'°<span style="opacity:.6">　模型推算</span>';
  if(!(G && G['midtarsal_df_'+archSide]))
    txt+='<br><span style="color:var(--warn)">此片段沒有足部資料，足弓不會變化</span>';
  return txt;""", what='無足部資料提示')

# ---- 4) 改用圓柱體畫線 ----
rep("""(function(){
  function line(color, n, w){
    var g=new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n*3),3));
    var m=new THREE.LineBasicMaterial({color:color, linewidth:w||1,
          transparent:true, opacity:0.95, depthTest:false});
    var o=new THREE.Line(g,m); o.frustumCulled=false; o.renderOrder=10;
    archGroup.add(o); return o;
  }
  ARCH.span = line(0xffc46b, 3);          // 跟 → 舟 → 蹠1
  ARCH.ref  = line(0xffc46b, 2);          // 貼平時的高度，水平基準
  ARCH.ref.material.opacity=0.42;
  ARCH.drop = line(0xff8a6b, 2);          // 弓高本身
  ARCH.ghost= line(0x8fa0b0, 3);          // 貼平時的足弓輪廓，當殘影比對
  ARCH.ghost.material.opacity=0.55;""",
    """// WebGL 的 LineBasicMaterial.linewidth 在絕大多數瀏覽器永遠是 1 像素，
// 設了也沒用。足弓的變化只有幾毫米，一像素的線根本看不到，
// 所以這裡改用細圓柱體畫，才真的有粗細。
var _ua=new THREE.Vector3(0,1,0), _ub=new THREE.Vector3(), _um=new THREE.Vector3();
function tube(color, r, op){
  var g=new THREE.CylinderGeometry(r, r, 1, 8, 1, true);
  var m=new THREE.MeshBasicMaterial({color:color, depthTest:false,
        transparent:true, opacity:op==null?0.95:op});
  var o=new THREE.Mesh(g,m); o.frustumCulled=false; o.renderOrder=10;
  archGroup.add(o); return o;
}
function setTube(o, a, b){
  _ub.subVectors(b,a);
  var L=_ub.length();
  if(L<1e-6){ o.visible=false; return; }
  o.visible=true;
  _um.addVectors(a,b).multiplyScalar(0.5);
  o.position.copy(_um);
  o.scale.set(1,L,1);
  o.quaternion.setFromUnitVectors(_ua, _ub.multiplyScalar(1/L));
}
(function(){""", what='改用圓柱體')

rep("""  ARCH.dot   = ball(0xffc46b, 0.0020);        // 目前的舟狀骨""",
    """  ARCH.span1= tube(0xffc46b, 0.0012);        // 跟 → 舟
  ARCH.span2= tube(0xffc46b, 0.0012);        // 舟 → 蹠1
  ARCH.ref  = tube(0xffc46b, 0.0008, 0.40);  // 基線：兩個著地點
  ARCH.drop = tube(0xff8a6b, 0.0016);        // 弓高本身
  ARCH.gh1  = tube(0x8fa0b0, 0.0009, 0.60);  // 貼平時的輪廓（殘影）
  ARCH.gh2  = tube(0x8fa0b0, 0.0009, 0.60);
  ARCH.dot   = ball(0xffc46b, 0.0020);        // 目前的舟狀骨""", what='圓柱體元件')

rep("""  setLine(ARCH.span,[pt.heel, pt.nav, pt.mt1]);
  setLine(ARCH.ref ,[pt.heel, pt.mt1]);                 // 基線：兩個著地點
  setLine(ARCH.drop,[foot, pt.nav]);                    // 弓高本身
  ARCH.ref.visible=true; ARCH.drop.visible=true;
  ARCH.dot.position.copy(pt.nav);""",
    """  setTube(ARCH.span1, pt.heel, pt.nav);
  setTube(ARCH.span2, pt.nav,  pt.mt1);
  setTube(ARCH.ref,   pt.heel, pt.mt1);                 // 基線：兩個著地點
  setTube(ARCH.drop,  foot,    pt.nav);                 // 弓高本身
  ARCH.dot.position.copy(pt.nav);""", what='畫足弓三角形')

rep("""    setLine(ARCH.ghost,[pt.heel, gnav, pt.mt1]);
    ARCH.ghost.visible=true;
    ARCH.gdot.visible=true; ARCH.gdot.position.copy(gnav);
  } else { ARCH.ghost.visible=false; ARCH.gdot.visible=false; }""",
    """    setTube(ARCH.gh1, pt.heel, gnav);
    setTube(ARCH.gh2, gnav,  pt.mt1);
    ARCH.gdot.visible=true; ARCH.gdot.position.copy(gnav);
  } else { ARCH.gh1.visible=false; ARCH.gh2.visible=false; ARCH.gdot.visible=false; }""",
    what='畫殘影輪廓')

io.open(P, 'w', encoding='utf-8').write(s)
print('四個修正已套用（%d → %d 位元組）' % (len(orig.encode()), len(s.encode())))
