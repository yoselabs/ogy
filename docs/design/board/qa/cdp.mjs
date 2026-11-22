// usage: node cdp.mjs scenes.json
import {spawn} from 'node:child_process';import fs from 'node:fs';
const S=process.env.OUT;
if(!S)throw Error('OUT must name the output folder');
fs.mkdirSync(S,{recursive:true});
const C='/nix/store/sx0yv1as1yxfqkdxwf9khbii0cmkbj8v-chromium-156.0.8078.47/bin/chromium';
const port=9400+Math.floor(Math.random()*400);
const proc=spawn(C,['--headless=new','--no-sandbox','--disable-gpu','--hide-scrollbars','--remote-debugging-port='+port,'--user-data-dir='+S+'/prof'+port,'about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let ver;for(let i=0;i<50;i++){try{ver=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();if(ver.length)break}catch{}await sleep(200)}
if(!ver?.length){proc.kill();throw Error('Chromium did not expose a page')}
const ws=new WebSocket(ver.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
let id=0;const pend=new Map();const errs=[];
ws.onmessage=m=>{const d=JSON.parse(m.data);if(d.id&&pend.has(d.id)){pend.get(d.id)(d.result||d);pend.delete(d.id)}else if(d.method==='Runtime.exceptionThrown')errs.push(d.params.exceptionDetails.exception?.description?.split('\n')[0]||d.params.exceptionDetails.text)};
const send=(method,params={})=>new Promise(r=>{pend.set(++id,r);ws.send(JSON.stringify({id,method,params}))});
const ev=async e=>{const r=await send('Runtime.evaluate',{expression:e,returnByValue:true,awaitPromise:true});return r.result?.value??r.exceptionDetails?.exception?.description};
await send('Page.enable');await send('Runtime.enable');
const center=async sel=>ev(`(()=>{const e=document.querySelector(${JSON.stringify(sel)});if(!e)return null;e.scrollIntoViewIfNeeded?.();const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()`);
const mouse=(type,x,y,o={})=>send('Input.dispatchMouseEvent',{type,x,y,button:'left',clickCount:1,...o});
for(const sc of JSON.parse(fs.readFileSync(process.argv[2]))){
  errs.length=0;const [w,h]=sc.size||[1440,1000];const out=[];
  await send('Emulation.setDeviceMetricsOverride',{width:w,height:h,deviceScaleFactor:1,mobile:!!sc.mobile});
  await send('Page.navigate',{url:sc.url});await sleep(sc.wait||3500);
  for(const a of sc.actions||[]){
    if(a.media){await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:a.media}]})}
    else if(a.click){const p=await center(a.click);if(!p){out.push('MISSING '+a.click);continue}await mouse('mouseMoved',p[0],p[1],{button:'none'});await mouse('mousePressed',p[0],p[1]);await mouse('mouseReleased',p[0],p[1])}
    else if(a.clickAt){const p=a.clickAt;await mouse('mouseMoved',p[0],p[1],{button:'none'});await mouse('mousePressed',p[0],p[1]);await mouse('mouseReleased',p[0],p[1])}
    else if(a.hover){const p=await center(a.hover);if(!p){out.push('MISSING '+a.hover);continue}await mouse('mouseMoved',p[0]-3,p[1]-1,{button:'none'});await mouse('mouseMoved',p[0],p[1],{button:'none'})}
    else if(a.drag){const p=await center(a.drag);await mouse('mouseMoved',p[0],p[1],{button:'none'});await mouse('mousePressed',p[0],p[1]);for(let i=1;i<=6;i++)await mouse('mouseMoved',p[0]+a.by[0]*i/6,p[1]+a.by[1]*i/6,{buttons:1});if(!a.hold)await mouse('mouseReleased',p[0]+a.by[0],p[1]+a.by[1])}
    else if(a.wheel){await send('Input.dispatchMouseEvent',{type:'mouseWheel',x:a.at[0],y:a.at[1],deltaX:0,deltaY:a.wheel,modifiers:a.mod||0})}
    else if(a.key){const k=a.key;await send('Input.dispatchKeyEvent',{type:'keyDown',key:k,code:a.code||k,windowsVirtualKeyCode:a.vk||0,modifiers:a.mod||0});await send('Input.dispatchKeyEvent',{type:'keyUp',key:k,code:a.code||k,windowsVirtualKeyCode:a.vk||0,modifiers:a.mod||0})}
    else if(a.type){await send('Input.insertText',{text:a.type})}
    else if(a.eval){out.push(String(await ev(a.eval)))}
    else if(a.shot){const r=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(S+'/'+a.shot+'.png',Buffer.from(r.data,'base64'))}
    await sleep(a.wait||500);
  }
  out.push('vp='+await ev('innerWidth+"x"+innerHeight'));
  const r=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(S+'/'+sc.name+'.png',Buffer.from(r.data,'base64'));
  console.log(sc.name,'|',out.join(' | '),errs.length?'| ERRORS: '+[...new Set(errs)].join(' ;; '):'');
}
ws.close();proc.kill();await new Promise(r=>proc.once('exit',r));fs.rmSync(S+'/prof'+port,{recursive:true,force:true,maxRetries:5});process.exit(0);
