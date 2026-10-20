#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v1.12.2：肘的靜態角做成三檔切換，肩中心定在 Murray 1967。

討論定案（2026-10-20）：
  - 肘靜態角三檔：實測 35°（Yegian 2019 走路平均；Bertaux 的 47° 不用，
    因為兩個 PiG 資料集的絕對值互相矛盾）／折衷 25°／視覺 15°（後擺時約 9°，
    接近一般人「走路手臂是直的」的視覺印象）。預設實測 35°。
  - 三檔只改整條曲線的高度；擺幅（實測 ±6.5°）與肩肘耦合（r=0.97）不變。
  - 肩中心固定 −8°（Murray 1967：伸 24°／屈 8° 的中點），不做檔位，
    因為肩的文獻值沒有分歧。
  - 這組切換本身是教學素材：視覺印象 vs 儀器量測的落差。
"""
import io, sys

P = '/home/claude/repo/build/template.html'
s = io.open(P, encoding='utf-8').read()
orig = s


def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: sys.exit('錨點「%s」出現 %d 次，預期 %d 次' % (old[:40], c, n))
    s = s.replace(old, new)


rep('<title>步態互動實驗室 v1.12.1</title>', '<title>步態互動實驗室 v1.12.2</title>')
rep('v1.12.1 · 公開版：34 個片段', 'v1.12.2 · 公開版：34 個片段')

# ---- 常數：肩 −8、肘預設 35 ----
rep("""var ARM_POSE={sh:-5, el:25, pron:80};""",
    """var ARM_POSE={sh:-8, el:35, pron:80};
/* 肘靜態角三檔（顯示常數，非量測；擺幅與肩肘耦合不受影響）：
     35° 實測——Yegian 2019 走路平均（Bertaux 的 47° 與 Shida 的 12° 互相矛盾，不用）
     25° 折衷
     15° 視覺——後擺時約 9°，符合「走路手臂是直的」的視覺印象
   肩中心固定 −8°：Murray 1967 伸 24°／屈 8° 的中點，文獻無分歧，不做檔位。 */""")

rep("""   中立位取正常行走擺臂的中位：肩 −5°（略後於鉛垂線）、肘屈 25°（Murray 1967；
   Meyns 2013 綜述）。前臂另加旋前 80°（解剖姿勢是旋後手掌朝前，走路手掌朝大腿）。 */""",
    """   肩中立 −8°（Murray 1967 伸 24°／屈 8° 的中點）；肘見下方三檔。
   前臂另加旋前 80°（解剖姿勢是旋後手掌朝前，走路手掌朝大腿）。 */""")

# ---- UI：三檔按鈕 ----
rep("""      <button id="archToggle">足弓</button>
    </div>""",
    """      <button id="archToggle">足弓</button>
    </div>
    <div class="row" id="elbPose" style="margin-top:6px;align-items:center">
      <span style="font-size:11px;color:#90A4B6;font-family:'Noto Sans TC',sans-serif">肘靜態角</span>
      <button data-el="35" class="on" title="Yegian 2019 走路平均。量測上走路的肘其實維持半屈，只微動 ±7°">實測 35°</button>
      <button data-el="25" title="實測與視覺之間的折衷">折衷 25°</button>
      <button data-el="15" title="後擺時約 9°，符合「走路手臂是直的」視覺印象">視覺 15°</button>
      <span style="font-size:10.5px;color:#627689;font-family:'Noto Sans TC',sans-serif">顯示常數（模型）；擺幅與肩肘耦合為實測，不受此切換影響</span>
    </div>""")

rep("""grp('#zoomBtns button',function(b){zoomMode=b.dataset.zoom;""",
    """grp('#elbPose button',function(b){ARM_POSE.el=+b.dataset.el;});
grp('#zoomBtns button',function(b){zoomMode=b.dataset.zoom;""")

# ---- 關節面板文字 ----
rep("""      'Plug-in Gait 的肩肘絕對角度在不同資料集互相矛盾（肩 −15° vs −7°、肘 47° vs 12°），'+
      '不可信。本工具的手臂資料一律只取週期內變化量，靜態姿勢用文獻常數：'+
      '肩中立 '+ARM_POSE.sh+'°、肘屈 '+ARM_POSE.el+'°（Murray 1967；Meyns 2013），'+
      '前臂旋前 '+ARM_POSE.pron+'°（解剖姿勢手掌朝前，走路應朝大腿）。'+
      '這三個常數全片段相同，組間差異只來自實測擺幅。'+""",
    """      'Plug-in Gait 的肩肘絕對角度在不同資料集互相矛盾（肩 −15° vs −7°、肘 47° vs 12°），'+
      '不可信。本工具的手臂資料一律只取週期內變化量，靜態姿勢用文獻常數：'+
      '肩中立 '+ARM_POSE.sh+'°（Murray 1967 伸 24°／屈 8° 的中點）、'+
      '肘目前 '+ARM_POSE.el+'°（左側「肘靜態角」三檔可切：實測 35° 為 Yegian 2019 的走路平均，'+
      '視覺 15° 對應一般人的視覺印象——量測與視覺的落差本身值得教），'+
      '前臂旋前 '+ARM_POSE.pron+'°（解剖姿勢手掌朝前，走路應朝大腿）。'+
      '這些常數全片段相同，組間差異只來自實測擺幅。'+""")

# ---- 資料來源面板 ----
rep('靜態姿勢改用文獻常數（模型，全片段相同）：肩中立 −5°、肘屈 25°（Murray 1967；Meyns 2013 綜述），前臂旋前 80°（解剖標本是旋後掌心朝前，走路時掌心朝大腿），肩內收常數由幾何求得（腕垂在肩正下方）——<b>擺幅是實測的，絕對角度不是</b>。',
    '靜態姿勢改用文獻常數（模型，全片段相同）：肩中立 −8°（Murray 1967 量到伸 24°／屈 8°，取中點；疊上實測擺幅後為伸 21°／屈 6°，與 Murray 一致）；肘提供三檔切換——實測 35°（Yegian 2019 的走路平均，J Exp Biol 222:jeb197228；該研究同時量到跑步為 88°）、折衷 25°、視覺 15°（後擺時約 9°，符合「走路手臂接近伸直」的視覺印象；量測顯示實際上肘維持半屈、僅微動約 ±7°，視覺與量測的落差為已知現象）——預設實測 35°，三檔只改整條曲線的高度，擺幅與肩肘耦合（相關 r=0.97：肩伸時肘伸）不變。前臂旋前 80°（解剖標本是旋後掌心朝前，走路時掌心朝大腿），肩內收常數由幾何求得（腕垂在肩正下方）——<b>擺幅是實測的，絕對角度不是</b>。')

io.open(P, 'w', encoding='utf-8').write(s)
print('三檔切換已套用（%d → %d 位元組）' % (len(orig.encode()), len(s.encode())))
