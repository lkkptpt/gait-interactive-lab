// 逐一檢查三個合成片段的閉合修正是否足夠（也檢查有沒有改過頭）
const { chromium } = require('playwright'); const path=require('path');
(async()=>{
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
   args:['--disable-background-networking','--no-first-run','--disable-sync']});
 const p=await b.newPage({viewport:{width:1200,height:800}});
 await p.route(/^https?:/,r=>r.abort());
 await p.goto('file://'+path.join(__dirname,'measure.html'),{waitUntil:'load'});
 await p.waitForTimeout(3000); await p.click('#play').catch(()=>{});

 await p.selectOption('#clipSel','vc_young'); await p.waitForTimeout(900);
 const base=await p.evaluate(()=>window.__clear());
 const flat=[]; base.rows.forEach((r,i)=>{ if(r[0]<base.tol && r[1]<base.tol) flat.push(i); });
 const baseMax=Math.max(...flat.map(i=>base.rows[i][1]));
 console.log('貼平區間 '+flat[0]+'–'+flat[flat.length-1]+'%，原片段前足最高 '+baseMax.toFixed(2)+' mm（門檻 '+base.tol+'）\n');

 for(const id of ['arch_walk_normal','arch_walk_pronated','arch_walk_supinated']){
   await p.selectOption('#clipSel',id); await p.waitForTimeout(900);
   const line=[];
   for(const d of [1.0,0.5,0,-0.5,-1.0]){
     const r=await p.evaluate(dd=>window.__trial(dd),d);
     const mx=Math.max(...flat.map(i=>r[i][1]));
     line.push((d>0?'+':'')+d.toFixed(1)+'°→'+mx.toFixed(1)+(mx<=baseMax?'✓':'✗'));
   }
   console.log(id.padEnd(22)+line.join('  '));
 }
 console.log('\n（0° = 目前設定的閉合修正。✓ 表示前足不高於原片段。');
 console.log(' 往 + 的方向仍為 ✓ 表示修正可以再小一點，仍為 ✗ 表示修正不夠。）');
 await b.close();})();
