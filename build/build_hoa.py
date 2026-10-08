import pickle, numpy as np, json, warnings
warnings.filterwarnings('ignore')
CH,META=pickle.load(open('hoa.pkl','rb'))
J={k:np.array(v['p']) for k,v in json.load(open('skeleton.json'))['joints'].items()}
Z=[0.0]*101; d=np.deg2rad
def Rz(a):c,s=np.cos(a),np.sin(a);return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def roll50(a):
    v=np.roll(np.asarray(a)[:100],-50); return np.append(v,v[0])
def sole(g,i,side,ho):
    hip,knee,ank,sub,mtp=[J[k+'_'+side] for k in('hip','knee','ankle','sub','mtp')]
    Rh=Rz(d(g['hip_flexion_'+side][i]+ho)); Rk=Rh@Rz(d(g['knee_angle_'+side][i]))
    Pk=hip+Rh@(knee-hip); Pa=Pk+Rk@(ank-knee); Ra=Rk@Rz(d(g['ankle_angle_'+side][i]))
    return min((Pa+Ra@(sub-ank))[1]-0.030,(Pa+Ra@(mtp-ank))[1]-0.020)
def best_hip(g,stance):
    best=None
    for ho in np.arange(-25,15.5,0.5):
        y=[]
        for i in range(100):
            u=[]
            if i<stance: u.append(sole(g,i,'r',ho))
            if ((i+50)%100)<stance: u.append(sole(g,i,'l',ho))
            y.append(-min(u) if u else np.nan)
        y=np.array(y); s=np.nanmax(y)-np.nanmin(y)
        if best is None or s<best[0]: best=(s,ho)
    return round(best[1],1)
def get(side,part,ax,k):
    D=CH.get(('HOA',side,part,ax))
    if D and k in D: return np.array(D[k])
    D=CH.get(('HOA','L' if side=='R' else 'R',part,ax))
    if D and k in D: return roll50(D[k])   # 同一剛體，換起點
    return None
def clip_for(k,cid,label,note,group):
    m=META[k]
    dm=lambda v: np.asarray(v,float)-np.mean(np.asarray(v,float)[:100])
    # 左右檔的原始相位已相差約 50%（186 人實測，四分位距 50–50），不可再平移
    hr,hl=get('R','Hip','X',k),   get('L','Hip','X',k)
    kr,kl=get('R','Knee','X',k),  get('L','Knee','X',k)
    ar,al=get('R','Ankle','X',k), get('L','Ankle','X',k)
    adr,adl=get('R','Hip','Y',k), get('L','Hip','Y',k)
    pel_x,pel_y=get('R','Pelvis','X',k), get('R','Pelvis','Y',k)
    thx_y=get('R','Thorax','Y',k)
    tg=dm(thx_y)
    data={'pelvis_tilt':[round(float(-x),3) for x in dm(pel_x)],
          'pelvis_list':[round(float(x),3) for x in dm(pel_y)],
          'pelvis_rotation':Z,'lumbar_extension':Z,
          # 本繫結的 lumbar_bending 是相對骨盆的角；Spine ＝ −(Thorax−Pelvis)（實測 r=−0.991）
          'lumbar_bending':[round(float(x),3) for x in (tg-dm(pel_y))],
          'lumbar_rotation':Z}
    for s,(hf,kf,af,ad) in (('r',(hr,kr,ar,adr)),('l',(hl,kl,al,adl))):
        data['hip_flexion_'+s]=[round(float(x),3) for x in hf]
        data['knee_angle_'+s]=[round(float(-x),3) for x in kf]
        data['ankle_angle_'+s]=[round(float(x),3) for x in af]
        data['hip_adduction_'+s]=[round(float(x),3) for x in (dm(ad)-3.0)]
        data['hip_rotation_'+s]=Z; data['subtalar_angle_'+s]=Z; data['mtp_angle_'+s]=Z
    stance=60.0; ho=best_hip(data,stance)
    rg=lambda v: float(max(v[:100])-min(v[:100]))
    return {'id':cid,'label':label,'group':group,
      'meta':{'subject':k,'age':m['age'],'sex':m['sex'],'bmi':m['bmi'],'kl':m['kl'],
              'oaside':m['side'],'cls':m['cls'],'cohort':'HOA',
              'thorax_obl':round(rg(tg),1),'pelvis_obl':round(rg(dm(pel_y)),1)},
      'period':1.10,'period_src':None,
      'period_note':'此資料集的文字檔版本未提供絕對時間軸，週期未知。播放固定 1.10 s，1× 不代表實際步速。',
      'source':'Bertaux et al. 2022, Sci Data 9:399（CC BY 4.0）；Plug-in Gait',
      'note':note,'data':data,'hip_offset':ho,
      'hip_offset_note':'髖角度為相對骨盆量測值。此 clip 施加常數偏移 %+.1f°（幾何閉合）。'%ho,
      'phase_l':0.5,'stance_r':stance,'stance_l':stance,
      'stance_src':'假設 60%（此資料集未提供事件）',
      'events':[{'p':0.0,'label':'右足著地','short':'R-IC','src':'資料集定義'}],
      'bands':[],'stats':{},'align':'原始資料第 0 點即為右足著地'}
G1='髖關節退化（Bertaux 106 人，術前）'
PICK=[('HOA108','hoa_108','髖退化 HOA108 ‧ 59歲男 ‧ Trendelenburg ‧ 軀幹傾 14.4°','醫師判定 Trendelenburg。軀幹左右傾為健康組平均的 8.1 個標準差。',G1),
      ('HOA87','hoa_87','髖退化 HOA87 ‧ 65歲女 ‧ Trendelenburg ‧ 軀幹傾 12.8°','醫師判定 Trendelenburg。KL 第 4 級。',G1),
      ('HOA55','hoa_55','髖退化 HOA55 ‧ 51歲女 ‧ Trendelenburg ‧ 軀幹傾 7.9°','醫師判定 Trendelenburg，程度中等。KL 第 2 級。',G1),
      ('HOA116','hoa_116','髖退化 HOA116 ‧ 76歲女 ‧ Trendelenburg ‧ 軀幹傾 3.7°','醫師判定 Trendelenburg，但軀幹與骨盆擺幅與健康組相當（0.2 個標準差）。肉眼判讀與儀器量測不一致的例子。',G1),
      ('HOA68','hoa_68','髖退化 HOA68 ‧ 63歲男 ‧ Duchenne ‧ 軀幹傾 8.0°','醫師判定 Duchenne（軀幹與骨盆一起倒向站立側）。D3 組中軀幹擺幅最大者。',G1),
      ('HOA15','hoa_15','髖退化 HOA15 ‧ 59歲男 ‧ Duchenne ‧ 軀幹傾 5.4°','醫師判定 Duchenne。軀幹擺幅 5.4°，介於健康組（3.4±1.4°）與 Trendelenburg 組（7.9±4.1°）之間。',G1),
      ('HOA73','hoa_73','髖退化 HOA73 ‧ 74歲男 ‧ Duchenne ‧ 軀幹傾 5.2°','醫師判定 Duchenne。D3 組 8 位右側患病者中，唯一軀幹與骨盆呈反向擺動者。',G1)]
cl=[clip_for(*p) for p in PICK]
json.dump(cl,open('_clips_hoa.json','w'),ensure_ascii=False)
print('建立 %d 個 clip'%len(cl))
for c in cl:
    m=c['meta']
    print('  %-10s %-14s 髖偏移 %+6.1f°  軀幹傾 %5.1f°  骨盆傾 %5.1f°'
          %(c['id'],{'D1':'Trendelenburg','D3':'Duchenne'}[m['cls']],c['hip_offset'],m['thorax_obl'],m['pelvis_obl']))
