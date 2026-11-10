const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:627}});await p.goto('file://'+process.cwd()+'/og.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
const o=await p.evaluate(()=>{const h=document.querySelector('.l');const r=h.getBoundingClientRect();return [r.right,r.bottom,document.querySelector('.st').getBoundingClientRect().bottom]});console.log(o);
await p.screenshot({path:'og.png'});await b.close()})()
