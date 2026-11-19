#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v1.13.2：前臂旋前改繞前臂長軸（肘中心→腕中心），不再繞鉛垂 Y 軸。

錯誤：setJ 的 tra 是繞節點的鉛垂 Y 軸。標本前臂不是鉛垂的——腕在肘前方 45 mm、
外側 42 mm（提攜角 carrying angle）。繞鉛垂軸轉 80° 等於把腕在水平面上甩一圈：
腕從肘外側 42 mm 甩到內側約 37 mm，淨內移約 80 mm；再疊上 ARM_REST.add
（以未旋前幾何算出的 10° 內收），手落在髖關節中心前方（z≈85 mm，髖中心 82 mm）。
實測：所有含手臂片段的手與骨盆／股骨網格重疊 19–42 mm，約半個週期。

旋前旋後本來就是繞前臂長軸（橈骨頭→尺骨莖突附近）的轉動，腕的位置不該因此移動，
只有手的朝向改變。改成繞肘→腕連線後，腕位置與 ARM_REST.add 的幾何前提一致。
角度 80° 與正負號約定不變（軸取由腕指向肘、接近 +Y，與原本 +Y 同向）。
"""
import io, sys
P = sys.argv[1] if len(sys.argv) > 1 else 'template.html'
s = io.open(P, encoding='utf-8').read()
def sub1(o, n):
    global s
    assert s.count(o) == 1, o[:60]
    s = s.replace(o, n)
sub1("""  ARM_REST[s]={flex:a1, elbow:a2-a1, add:ad};
});""", """  ARM_REST[s]={flex:a1, elbow:a2-a1, add:ad,
    // 前臂長軸（腕→肘，單位向量）：旋前旋後繞這條軸轉，腕的位置不動
    pax:new THREE.Vector3(el[0]-wr[0], el[1]-wr[1], el[2]-wr[2]).normalize()};
});
var _qPron=new THREE.Quaternion();""")
sub1("""    setJ('elbow_'+s, (g?samp('elbow_flexion_'+s,p):0) + ARM_POSE.el - R.elbow,
                     0, k*ARM_POSE.pron, p);""",
"""    setJ('elbow_'+s, (g?samp('elbow_flexion_'+s,p):0) + ARM_POSE.el - R.elbow, 0, 0, p);
    // 旋前繞前臂長軸，不繞鉛垂 Y 軸（v1.13.2 修正：繞 Y 會把腕甩到內側、手穿進骨盆）
    if(R.pax){ _qPron.setFromAxisAngle(R.pax, k*ARM_POSE.pron*D2R);
      nodes[JM['elbow_'+s].seg].quaternion.multiply(_qPron); live['elbow_'+s].tra=k*ARM_POSE.pron; }""")
sub1('<title>步態互動實驗室 v1.13.1</title>', '<title>步態互動實驗室 v1.13.2</title>')
sub1('<p class="sub">v1.13.1 ·', '<p class="sub">v1.13.2 ·')
io.open(P, 'w', encoding='utf-8').write(s)
print('完成')
