#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把上肢接進介面（v1.12.0）。

搭配 build_arms.py（骨頭與關節中心）與 build_arms_motion.py（動作通道）。

介面上要做到的事：
  1. 六個新關節（肩／肘／腕 × 左右）進 JOINTS，可選、可拉滑桿、有鏡像對應。
  2. pose() 依資料驅動手臂。資料零位與標本姿勢不同，用兩個由骨頭幾何算出的常數對齊：
       - 肘：標本的前臂本來就屈 12.4°，資料的 0° 是伸直，所以肘角 = 資料 − 12.4°，
         畫面上的肘屈曲角才會等於量到的值。
       - 肩內收：標本的手臂外展垂著，腕在肩外側 9 cm。額狀面資料只取週期內變化量
         （PiG 的絕對值不可信），所以加一個常數讓腕垂在肩的正下方（幾何條件，非量測）。
  3. 沒有手臂資料的片段，手臂垂直靜止、肘伸直，HUD 標示；借用的片段標「借用」。
  4. 圖表多肩／肘兩張（只在有資料時畫）、對照表多一列肩擺幅。
  5. 「顯示」多一個上肢核取方塊。
  6. 資料來源面板補上肢骨頭來源、手臂資料逐片段說明。
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


# ---- 版本 ----
rep('<title>步態互動實驗室 v1.11.0</title>', '<title>步態互動實驗室 v1.12.0</title>', what='title')
rep('v1.11.0 · 公開版：33 個片段', 'v1.12.0 · 公開版：34 個片段', what='sub')

# ---- 1) JOINTS ----
rep(""" {id:'mtp_l',mir:1,seg:'toes_l',label:'第2–5蹠趾關節（左）· 模型',ax:[['sag','伸展','屈曲']]}
];""",
    """ {id:'mtp_l',mir:1,seg:'toes_l',label:'第2–5蹠趾關節（左）· 模型',ax:[['sag','伸展','屈曲']]},
 {id:'shoulder_r',seg:'humerus_r',label:'肩關節（右）',ax:[['sag','屈曲','伸展'],['fro','內收','外展'],['tra','內旋','外旋']]},
 {id:'elbow_r',seg:'forearm_r',label:'肘關節（右）',ax:[['sag','屈曲','伸展']]},
 {id:'wrist_r',seg:'hand_r',label:'腕關節（右）',ax:[['sag','屈曲','伸展'],['fro','尺偏','橈偏']]},
 {id:'shoulder_l',mir:1,seg:'humerus_l',label:'肩關節（左）',ax:[['sag','屈曲','伸展'],['fro','內收','外展'],['tra','內旋','外旋']]},
 {id:'elbow_l',mir:1,seg:'forearm_l',label:'肘關節（左）',ax:[['sag','屈曲','伸展']]},
 {id:'wrist_l',mir:1,seg:'hand_l',label:'腕關節（左）',ax:[['sag','屈曲','伸展'],['fro','尺偏','橈偏']]}
];""", what='JOINTS')

rep("""         tmt_r:'tmt_l',tmt_l:'tmt_r'};""",
    """         tmt_r:'tmt_l',tmt_l:'tmt_r',
         shoulder_r:'shoulder_l',shoulder_l:'shoulder_r',elbow_r:'elbow_l',elbow_l:'elbow_r',
         wrist_r:'wrist_l',wrist_l:'wrist_r'};""", what='MIR')

# ---- 2) 靜態姿勢對齊常數 + pose ----
rep("""var mode='gait',live={};""",
    """/* 手臂的靜態姿勢對齊：由關節中心的幾何算出來，不是量測、也不是手調。
   restFlex：標本肱骨相對鉛垂線的矢狀偏角；restElbow：標本前臂相對肱骨的屈曲角；
   restAdd：要讓腕垂在肩正下方，肱骨需要內收幾度（PiG 額狀面絕對值不可信，只取變化量，
   所以靜態姿勢由幾何決定）。畫面上的肩屈曲、肘屈曲角 = 資料值。 */
var ARM_REST={};
['r','l'].forEach(function(s){
  var sh=Jc['shoulder_'+s], el=Jc['elbow_'+s], wr=Jc['wrist_'+s];
  if(!sh||!el||!wr){ ARM_REST[s]={flex:0,elbow:0,add:0}; return; }
  var a1=Math.atan2(el[0]-sh[0], sh[1]-el[1])/D2R;      // 肱骨：肘在肩前方為正
  var a2=Math.atan2(wr[0]-el[0], el[1]-wr[1])/D2R;      // 前臂：腕在肘前方為正
  var ad=Math.atan2(Math.abs(wr[2]-sh[2]), sh[1]-wr[1])/D2R;
  ARM_REST[s]={flex:a1, elbow:a2-a1, add:ad};
});
function hasArm(){ return !!(G && G['shoulder_flexion_r']); }
var mode='gait',live={};""", what='ARM_REST')

rep("""    } else {
      setJ('mtp1_'+s, (g?samp('mtp_angle_'+s,p):0) + mtpModel(_q,_st), 0, 0, p);
    }
  });""",
    """    } else {
      setJ('mtp1_'+s, (g?samp('mtp_angle_'+s,p):0) + mtpModel(_q,_st), 0, 0, p);
    }
    // 手臂：有通道的片段照資料走；沒有的片段 samp 回 0，手臂垂直靜止、肘伸直。
    // 三個 ARM_REST 常數是標本姿勢與資料零位之間的幾何差，見上方說明。
    var R=ARM_REST[s];
    setJ('shoulder_'+s, (g?samp('shoulder_flexion_'+s,p):0) - R.flex,
                        k*((g?samp('shoulder_adduction_'+s,p):0) + R.add),
                        k*(g?samp('shoulder_rotation_'+s,p):0), p);
    setJ('elbow_'+s, (g?samp('elbow_flexion_'+s,p):0) - R.elbow, 0, 0, p);
    setJ('wrist_'+s, g?samp('wrist_flexion_'+s,p):0, 0, 0, p);
  });""", what='pose 手臂')

# ---- 3) 圖表 ----
rep(""" {t:'踝',  pos:'背屈', neg:'蹠屈', k:['ankle_angle_r','ankle_angle_l'],  sg:1}
];""",
    """ {t:'踝',  pos:'背屈', neg:'蹠屈', k:['ankle_angle_r','ankle_angle_l'],  sg:1},
 // 肩／肘只在片段有手臂通道時才畫（opt）
 {t:'肩',  pos:'屈曲', neg:'伸展', k:['shoulder_flexion_r','shoulder_flexion_l'], sg:1, opt:true},
 {t:'肘',  pos:'屈曲', neg:'伸展', k:['elbow_flexion_r','elbow_flexion_l'], sg:1, opt:true}
];""", what='SERIES_BODY')

rep("""  SERIES.forEach(function(sr){
    if(cc && cc.foot_only!==CLIP.foot_only) cc=null;   // 足部與全身片段不互比""",
    """  SERIES.forEach(function(sr){
    if(sr.opt && !G[sr.k[0]]) return;                  // 沒有這個通道就不畫
    if(cc && cc.foot_only!==CLIP.foot_only) cc=null;   // 足部與全身片段不互比""", what='buildCharts opt')

rep("""   ['踝蹠屈峰值', function(c){return mn(c.data.ankle_angle_r);},1,'°'],""",
    """   ['踝蹠屈峰值', function(c){return mn(c.data.ankle_angle_r);},1,'°'],
   ['肩擺幅（右）', function(c){var v=c.data.shoulder_flexion_r; if(!v||(c.arm||{}).src!=='own') return NaN; return mx(v)-mn(v);},1,'°'],
   ['肘擺幅（右）', function(c){var v=c.data.elbow_flexion_r;    if(!v||(c.arm||{}).src!=='own') return NaN; return mx(v)-mn(v);},1,'°'],""",
    what='對照表')

# ---- 4) 顯示核取方塊 ----
rep("""var VIS={head:true, thorax:true, lumbar:true, pelvis:true, right:true, left:true, toes:true};""",
    """var VIS={head:true, thorax:true, lumbar:true, pelvis:true, right:true, left:true, toes:true, arms:true};""",
    what='VIS')
rep("""  head:      function(){return VIS.head;},
  cervical:  function(){return VIS.head;},""",
    """  head:      function(){return VIS.head;},
  cervical:  function(){return VIS.head;},
  humerus_r: function(){return VIS.arms;},
  forearm_r: function(){return VIS.arms;},
  hand_r:    function(){return VIS.arms;},
  humerus_l: function(){return VIS.arms;},
  forearm_l: function(){return VIS.arms;},
  hand_l:    function(){return VIS.arms;},""", what='SEGVIS')
rep(""" ['thorax','胸廓（胸椎、肋骨、胸骨）'],""",
    """ ['thorax','胸廓（胸椎、肋骨、胸骨、鎖骨、肩胛骨）'],
 ['arms','上肢（肱骨、前臂、手）'],""", what='顯示清單')

# ---- 5) HUD 與片段資訊：手臂資料來源 ----
rep("""      <div id="archHud" style="font-family:'Noto Sans TC',sans-serif;font-size:12px;line-height:1.6"></div>""",
    """      <div id="archHud" style="font-family:'Noto Sans TC',sans-serif;font-size:12px;line-height:1.6"></div>
      <div id="armHud" style="font-family:'Noto Sans TC',sans-serif;font-size:12px;line-height:1.6"></div>""",
    what='armHud')

rep("""  var hl=document.getElementById('hudPctLbl');
  if(hl) hl.textContent = c.pct_label || (c.stance_only ? '站立期' : '步行周期');""",
    """  var hl=document.getElementById('hudPctLbl');
  if(hl) hl.textContent = c.pct_label || (c.stance_only ? '站立期' : '步行周期');
  // 手臂資料來源：實測／借用／無。借用與無資料一律用警示色，不讓人誤以為是量到的。
  var ah=document.getElementById('armHud');
  if(ah){
    var a=c.arm;
    if(c.foot_only||!a) ah.innerHTML='';
    else if(a.src==='own') ah.innerHTML='<span style="color:#90A4B6">手臂　實測</span>';
    else if(a.src==='borrowed') ah.innerHTML='<span style="color:var(--warn)">手臂　借用健康組平均（本片段無手臂資料）</span>';
    else ah.innerHTML='<span style="color:var(--warn)">手臂　無資料，靜止</span>';
  }""", what='setClip armHud')

rep("""  if(c.note) h+='<br><span style="opacity:.75">'+c.note+'</span>';
  h+='<br><span style="opacity:.7">週期 '""",
    """  if(c.note) h+='<br><span style="opacity:.75">'+c.note+'</span>';
  if(c.arm&&!c.foot_only) h+='<br><span style="'+(c.arm.src==='own'?'opacity:.75':'color:var(--warn)')+'">'+c.arm.note+'</span>';
  h+='<br><span style="opacity:.7">週期 '""", what='fmtMeta arm note')

rep("""  } else if(m.cohort==='VC-healthy'){""",
    """  } else if(m.cohort==='HEA'){
    h+='<br>n='+m.n+'　健康對照組（Bertaux 2022）　下肢與手臂同源';
  } else if(m.cohort==='VC-healthy'){""", what='fmtMeta HEA')

# ---- 6) 關節面板：肩肘腕的提示 ----
rep("""  if(meta.axis_src) html+='<br><br><b>轉軸來源</b><br>'+meta.axis_src;
  document.getElementById('prov').innerHTML=html;""",
    """  if(meta.axis_src) html+='<br><br><b>轉軸來源</b><br>'+meta.axis_src;
  if(/^(shoulder|elbow|wrist)_/.test(curJ)){
    var sd=curJ.slice(-1), R=ARM_REST[sd]||{};
    html+='<br><br><b>靜態姿勢對齊（幾何，非量測）</b><br>'+
      '標本前臂原本屈 '+(R.elbow||0).toFixed(1)+'°、肱骨矢狀偏 '+(R.flex||0).toFixed(1)+'°，已扣除，'+
      '畫面上的肩屈曲與肘屈曲角＝資料值。肱骨另加內收 '+(R.add||0).toFixed(1)+'° 讓腕垂在肩正下方'+
      '（額狀面與水平面只取週期內變化量，絕對角度不是量測的）。'+
      (hasArm()?'':'<br><span style="color:var(--warn)">此片段沒有手臂資料，手臂維持靜止。</span>');
  }
  document.getElementById('prov').innerHTML=html;""", what='關節面板')

# ---- 7) 資料來源面板 ----
rep("""<p><b>零位對齊</b>：""",
    """<p><b>上肢（v1.12.0 新增）</b>：鎖骨、肩胛骨、肱骨、橈骨、尺骨、8 塊腕骨、5 根掌骨、14 節指骨，左右共 64 塊，與其餘骨頭同為 BodyParts3D 同一副標本（取自 GitHub 鏡像 Kevin-Mattheus-Moerman/BodyParts3D 的 STL，座標轉換後與既有骨頭的包圍盒誤差 &lt;0.1 mm）。肩關節中心為肱骨頭球面擬合（半徑 22.3／22.5 mm），肘為肱骨遠端 20 mm 切片質心，腕為橈尺骨遠端 15 mm 切片質心，皆為推估。鎖骨與肩胛骨併入胸廓，沒有肩帶的動作資料；前臂旋前旋後沒有拆出來。<br><b>手臂的動作資料逐片段不同，介面左上角與片段資訊都有標示：</b><br>・<b>實測</b>：Bertaux 2022 健康對照組平均（新片段 hea_mean，n=80）與 7 位髖關節炎受試者（同一資料集）；Shida 2023 帕金森資料集的全部片段（雙側肩、肘；該資料集無腕）。這些片段的手臂與下肢是同一批人同一次量到的。<br>・<b>借用</b>：Van Criekinge 健康組（年輕／中年／高齡）、Fukuchi 兩段平均、足弓合成三段——這些資料集的公開版本沒有手臂資料，畫面上的手臂借用 Bertaux 健康對照組 80 人平均，手臂與下肢不是同一批人，只示意正常擺臂的相位與幅度，不可拿來比較族群差異。<br>・<b>無</b>：中風四段。偏癱的手臂不該套用健康人的擺動，所以手臂垂直靜止。<br>零位：肩屈曲與肘屈曲取資料絕對值，並扣除標本靜態姿勢（前臂原本屈 12.4°）使畫面角度＝資料值；肩的額狀面與水平面、腕的矢狀面只取週期內變化量（Plug-in Gait 的這些角度受試者間靜態偏移達 ±8–20°），再以幾何條件讓腕垂在肩正下方——<b>擺幅是實測的，絕對角度不是</b>。相位：Bertaux 的左右檔在同一時間軸上（右肩在右足著地後約 5% 最伸展、左肩在 0% 最屈曲，與對側手腳同步一致），直接使用；Shida 的每一側以該側著地為 0%，左側平移 50%（與該資料集下肢相同）。</p><p><b>零位對齊</b>：""",
    what='資料來源 上肢')

rep("""<p><b>動作（L3）</b>：五個公開研究資料集""",
    """<p><b>動作（L3）</b>：五個公開研究資料集""", what='L3 anchor')

io.open(P, 'w', encoding='utf-8').write(s)
print('上肢介面已套用（%d → %d 位元組）' % (len(orig.encode()), len(s.encode())))
