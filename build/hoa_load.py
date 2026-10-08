import numpy as np, openpyxl, pickle, warnings
warnings.filterwarnings('ignore')
U='/mnt/user-data/uploads/'
def permean(f):
    out={}
    with open(U+f,encoding='latin-1') as fh:
        d=False
        for l in fh:
            l=l.strip()
            if not d:
                if l.lower().startswith('@data'): d=True
                continue
            if not l: continue
            p=l.split(',')
            if len(p)!=105: continue
            try: v=np.array([float(x) for x in p[:101]])
            except ValueError: continue
            if np.isnan(v).any(): continue
            out.setdefault(p[101],[]).append(v)
    return {k:np.mean(v,0) for k,v in out.items()}
rows=[r for r in openpyxl.load_workbook(U+'Metadata_20_23R1.xlsx',read_only=True,data_only=True)['Metadata of Volunteers'].iter_rows(values_only=True) if any(c is not None for c in r)]
h=[str(x) for x in rows[0]]; I={k:i for i,k in enumerate(h)}
META={}
for r in rows[1:]:
    if r[I['Cohorte']]=='HOA' and r[I['session']]=='M0':
        META['HOA'+(str(r[I['Id Inclusion']]).lstrip('0') or '0')]={
            'cls':r[I['Distubances']],'side':r[I['OASide']],'age':r[I['age (years)']],
            'sex':r[I['Sex (Male / Female)']],'bmi':r[I['BMI (kg.m-2)']],
            'kl':r[I['Kellgren and Lawrence Grade']]}
CH={}
for pre in ('HOA','HEA'):
    for part,axes in (('Pelvis','XY'),('Thorax','XY'),('Hip','XY'),('Knee','X'),('Ankle','X')):
        for side in ('R','L'):
            for ax in axes:
                try: CH[(pre,side,part,ax)]=permean('%s_M0_%s%sAngles_%s.arff'%(pre,side,part,ax))
                except FileNotFoundError: pass
pickle.dump((CH,META),open('hoa.pkl','wb'))
print('載入 %d 個通道，%d 位病人臨床資料'%(len(CH),len(META)))
