#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v1.12.1：手臂看起來不會擺——改用「擺幅實測、靜態姿勢文獻常數」。

v1.12.0 的做法是肩屈曲與肘屈曲顯示資料絕對值。實測結果（headless 量測）：
手其實前後移動 30 cm、左右反相，數據沒錯；但 Bertaux（Plug-in Gait）的絕對角度
把肩放在鉛垂線後方整個週期（−26°～0°）、肘恆定屈 41°–54°，上臂貼著軀幹、
前臂永遠朝前，視覺上完全不像擺臂。Shida 同為 PiG 的肩平均卻是 −7°、肘 12°——
兩個資料集的絕對值互相矛盾，證實 PiG 肩肘的絕對角度不可信（胸廓座標與
標記放置的系統差），只有週期內變化量可信。

所以比照本工具對骨盆、腰椎、髖額狀面的既有原則：
  - motion.json：肩屈曲、肘屈曲通道一律扣掉週期平均，只留變化量（擺幅不變）。
  - template：靜態姿勢改用文獻常數（模型，介面標示）：
      肩中立 −5°、肘屈 25°（正常行走的擺臂中位，Murray 1967；Meyns 2013 綜述）
    再疊上實測變化量。左右、各片段同一組常數，所以組間比較只反映實測差異。
  - 前臂加常數旋前 80°（模型）：BodyParts3D 是解剖姿勢（前臂旋後、手掌朝前、
    五指張開），走路時手掌應朝向大腿。繞前臂長軸轉，掛在肘關節的水平自由度上。
"""
import io, json, sys
import numpy as np

T = '/home/claude/repo/build/template.html'
M = '/home/claude/repo/build/motion.json'

# ---- 1) motion.json：肩肘矢狀面去均值 ----
m = json.load(open(M, encoding='utf-8'))
nch = 0
for c in m['clips']:
    for k in list(c.get('data', {})):
        if k.startswith('shoulder_flexion_') or k.startswith('elbow_flexion_'):
            v = np.asarray(c['data'][k], float)
            mu = v[:100].mean()
            if abs(mu) < 0.05:
                continue
            c['data'][k] = [round(float(x), 3) for x in (v - mu)]
            nch += 1
m['version'] = '1.12.1'
json.dump(m, open(M, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('去均值 %d 個通道' % nch)

# ---- 2) template ----
s = io.open(T, encoding='utf-8').read()
orig = s


def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: sys.exit('錨點「%s」出現 %d 次，預期 %d 次' % (old[:40], c, n))
    s = s.replace(old, new)


rep('<title>步態互動實驗室 v1.12.0</title>', '<title>步態互動實驗室 v1.12.1</title>')
rep('v1.12.0 · 公開版：34 個片段', 'v1.12.1 · 公開版：34 個片段')

rep("""function hasArm(){ return !!(G && G['shoulder_flexion_r']); }""",
    """function hasArm(){ return !!(G && G['shoulder_flexion_r']); }
/* 手臂的靜態姿勢：文獻常數（模型）。PiG 的肩肘絕對角度在兩個資料集互相矛盾
   （Bertaux 肩 −15°、肘 47°；Shida 肩 −7°、肘 12°），不可信，資料只取週期內變化量。
   中立位取正常行走擺臂的中位：肩 −5°（略後於鉛垂線）、肘屈 25°（Murray 1967；
   Meyns 2013 綜述）。前臂另加旋前 80°（解剖姿勢是旋後手掌朝前，走路手掌朝大腿）。 */
var ARM_POSE={sh:-5, el:25, pron:80};""")

rep("""    var R=ARM_REST[s];
    setJ('shoulder_'+s, (g?samp('shoulder_flexion_'+s,p):0) - R.flex,
                        k*((g?samp('shoulder_adduction_'+s,p):0) + R.add),
                        k*(g?samp('shoulder_rotation_'+s,p):0), p);
    setJ('elbow_'+s, (g?samp('elbow_flexion_'+s,p):0) - R.elbow, 0, 0, p);
    setJ('wrist_'+s, g?samp('wrist_flexion_'+s,p):0, 0, 0, p);""",
    """    var R=ARM_REST[s];
    // 資料是變化量；絕對姿勢＝文獻常數（ARM_POSE，模型）扣掉標本本來的姿勢（ARM_REST，幾何）
    setJ('shoulder_'+s, (g?samp('shoulder_flexion_'+s,p):0) + ARM_POSE.sh - R.flex,
                        k*((g?samp('shoulder_adduction_'+s,p):0) + R.add),
                        k*(g?samp('shoulder_rotation_'+s,p):0), p);
    setJ('elbow_'+s, (g?samp('elbow_flexion_'+s,p):0) + ARM_POSE.el - R.elbow,
                     0, k*ARM_POSE.pron, p);
    setJ('wrist_'+s, g?samp('wrist_flexion_'+s,p):0, 0, 0, p);""")

rep("""  if(/^(shoulder|elbow|wrist)_/.test(curJ)){
    var sd=curJ.slice(-1), R=ARM_REST[sd]||{};
    html+='<br><br><b>靜態姿勢對齊（幾何，非量測）</b><br>'+
      '標本前臂原本屈 '+(R.elbow||0).toFixed(1)+'°、肱骨矢狀偏 '+(R.flex||0).toFixed(1)+'°，已扣除，'+
      '畫面上的肩屈曲與肘屈曲角＝資料值。肱骨另加內收 '+(R.add||0).toFixed(1)+'° 讓腕垂在肩正下方'+
      '（額狀面與水平面只取週期內變化量，絕對角度不是量測的）。'+
      (hasArm()?'':'<br><span style="color:var(--warn)">此片段沒有手臂資料，手臂維持靜止。</span>');
  }""",
    """  if(/^(shoulder|elbow|wrist)_/.test(curJ)){
    var sd=curJ.slice(-1), R=ARM_REST[sd]||{};
    html+='<br><br><b style="color:var(--warn)">靜態姿勢＝模型，擺幅＝實測</b><br>'+
      'Plug-in Gait 的肩肘絕對角度在不同資料集互相矛盾（肩 −15° vs −7°、肘 47° vs 12°），'+
      '不可信。本工具的手臂資料一律只取週期內變化量，靜態姿勢用文獻常數：'+
      '肩中立 '+ARM_POSE.sh+'°、肘屈 '+ARM_POSE.el+'°（Murray 1967；Meyns 2013），'+
      '前臂旋前 '+ARM_POSE.pron+'°（解剖姿勢手掌朝前，走路應朝大腿）。'+
      '這三個常數全片段相同，組間差異只來自實測擺幅。'+
      '肱骨另加內收 '+(R.add||0).toFixed(1)+'°（幾何：讓腕垂在肩正下方）。'+
      (hasArm()?'':'<br><span style="color:var(--warn)">此片段沒有手臂資料，手臂維持靜止。</span>');
  }""")

rep('零位：肩屈曲與肘屈曲取資料絕對值，並扣除標本靜態姿勢（前臂原本屈 12.4°）使畫面角度＝資料值；肩的額狀面與水平面、腕的矢狀面只取週期內變化量（Plug-in Gait 的這些角度受試者間靜態偏移達 ±8–20°），再以幾何條件讓腕垂在肩正下方——<b>擺幅是實測的，絕對角度不是</b>。',
    '零位：手臂所有通道一律只取週期內變化量。Plug-in Gait 的肩肘絕對角度在兩個資料集互相矛盾（Bertaux 肩平均 −15°、肘 47°；Shida 肩 −7°、肘 12°，同一套標記協定），是胸廓座標定義與標記放置的系統差，不可信。靜態姿勢改用文獻常數（模型，全片段相同）：肩中立 −5°、肘屈 25°（Murray 1967；Meyns 2013 綜述），前臂旋前 80°（解剖標本是旋後掌心朝前，走路時掌心朝大腿），肩內收常數由幾何求得（腕垂在肩正下方）——<b>擺幅是實測的，絕對角度不是</b>。')

io.open(T, 'w', encoding='utf-8').write(s)
print('template 已更新（%d → %d 位元組）' % (len(orig.encode()), len(s.encode())))
