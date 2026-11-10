const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+__dirname+'/cv.html');await p.waitForTimeout(500);
const info=await p.evaluate(()=>{const m=document.querySelector('main'),a=document.querySelector('aside');
 // find last lines with a single word
 const out=[];document.querySelectorAll('li,p,h3').forEach(el=>{const r=document.createRange();r.selectNodeContents(el);const rects=[...r.getClientRects()].filter(x=>x.width>0);
  if(rects.length<2)return;const lastTop=Math.max(...rects.map(x=>Math.round(x.top)));const last=rects.filter(x=>Math.round(x.top)===lastTop);const w=last.reduce((s,x)=>s+x.width,0);
  if(w<70)out.push(el.textContent.trim().slice(-40)+' | lastw='+Math.round(w));});
 const bot=el=>Math.max(...[...el.children].map(c=>c.getBoundingClientRect().bottom));return {pageH:document.querySelector('.page').getBoundingClientRect().height,mainBottom:bot(m)+parseFloat(getComputedStyle(m).paddingBottom),asideBottom:bot(a)+parseFloat(getComputedStyle(a).paddingBottom),short:out}});
console.log(JSON.stringify(info,null,1));
await p.pdf({path:'CV_Kevin_NGUYEN_Alternance_Assistant_Marketing.pdf',format:'A4',printBackground:true,margin:{top:0,bottom:0,left:0,right:0}});await b.close()})()
