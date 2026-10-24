import {chromium} from "playwright";
const base="http://127.0.0.1:8765/";
const browser=await chromium.launch({headless:true});
const one=await browser.newContext(),two=await browser.newContext();
const first=await one.newPage(),second=await two.newPage();
const problems=[];
for(const [name,page] of [["first",first],["second",second]]){
 page.on("pageerror",e=>problems.push(name+" JS error: "+e.message));
 page.on("console",m=>{if(m.type()==="error")problems.push(name+" console: "+m.text().slice(0,200));});
}
function assert(ok,msg){if(!ok)throw new Error(msg);}
async function count(page,n,timeout=16000){
 await page.waitForFunction(n=>document.querySelectorAll("article.card").length===n,n,{timeout});
}
async function waitFor(page,expression,timeout=16000){
 await page.waitForFunction(expression,null,{timeout});
}
try{
 await Promise.all([first.goto(base),second.goto(base)]);
 await Promise.all([
   waitFor(first,()=>document.querySelector("#syncStatus")?.classList.contains("offline")===false),
   waitFor(second,()=>document.querySelector("#syncStatus")?.classList.contains("offline")===false)
 ]);
 await Promise.all([count(first,0),count(second,0)]);
 console.log("Both independent browser contexts connected.");
 const sample="https://minecraft.tools/en/banner.php?color_id_0=13&shape_id_1=32&color_id_1=5&shape_id_2=17&color_id_2=15#crafting";
 const t0=Date.now();
 await first.locator("#urlInput").fill(sample);
 await count(first,1);
 await count(second,1);
 console.log("Remote add appeared on second browser in",Date.now()-t0,"ms");
 await second.locator(".card").first().getByRole("button",{name:"Rename banner"}).click();
 await second.locator(".editor").fill("Cross-device banner");
 await second.locator(".editor").press("Enter");
 await waitFor(first,()=>document.querySelector(".name-text")?.textContent==="Cross-device banner");
 console.log("Rename synchronized.");
 await first.locator(".card input[type=checkbox]").check();
 await waitFor(second,()=>document.querySelector(".card input[type=checkbox]")?.checked===true);
 console.log("Checkbox synchronized.");
 await second.locator(".card").first().getByRole("button",{name:"Remove banner"}).click();
 await count(second,0);
 await count(first,0);
 console.log("Deletion synchronized.");

 // Real browser DataTransfer: dragging the gallery title should preserve its name.
 const owl="https://minecraft.tools/en/banner.php?color_id_0=15&shape_id_1=32&color_id_1=0&shape_id_2=31&color_id_2=15&shape_id_3=1&color_id_3=15&shape_id_4=8&color_id_4=15&shape_id_5=6&color_id_5=15#crafting";
 await first.evaluate(url=>{
   const transfer=new DataTransfer();
   transfer.setData("text/html",'<a href="'+url.replace(/&/g,"&amp;")+'" title="Owl"><strong>Owl</strong><span class="author">CrystalDrop</span></a>');
   transfer.setData("text/plain",url);
   document.querySelector("#dropzone").dispatchEvent(new DragEvent("drop",{bubbles:true,cancelable:true,dataTransfer:transfer}));
 },owl);
 await waitFor(first,()=>document.querySelector(".name-text")?.textContent==="Owl");
 await waitFor(second,()=>document.querySelector(".name-text")?.textContent==="Owl");
 console.log("PASS: dragged gallery title imported as Owl and synced to other browser.");
 // Importing the same design again should never create a duplicate.
 await first.evaluate(url=>{
   const transfer=new DataTransfer();
   transfer.setData("text/html",'<a href="'+url+'" title="Owl">Owl</a>');
   transfer.setData("text/plain",url);
   document.querySelector("#dropzone").dispatchEvent(new DragEvent("drop",{bubbles:true,cancelable:true,dataTransfer:transfer}));
 },owl);
 await count(first,1);
 await second.locator(".card").first().getByRole("button",{name:"Remove banner"}).click();
 await count(first,0);
 await count(second,0);
 // A plain URL receives a default name; dragging the title later upgrades it.
 await first.locator("#urlInput").fill(owl);
 await waitFor(first,()=>/^Banner \d+$/.test(document.querySelector(".name-text")?.textContent||""));
 await first.evaluate(url=>{
   const transfer=new DataTransfer();
   transfer.setData("text/x-moz-url",url+"\nOwl");
   transfer.setData("text/plain",url);
   document.querySelector("#dropzone").dispatchEvent(new DragEvent("drop",{bubbles:true,cancelable:true,dataTransfer:transfer}));
 },owl);
 await waitFor(first,()=>document.querySelector(".name-text")?.textContent==="Owl");
 await waitFor(second,()=>document.querySelector(".name-text")?.textContent==="Owl");
 await count(first,1);
 await second.locator(".card").first().getByRole("button",{name:"Remove banner"}).click();
 await count(first,0);
 await count(second,0);
 console.log("PASS: re-dropping Firefox title upgrades unnamed entry with no duplicate.");

 const r=await first.evaluate(async()=>{
   const config=await (await fetch("/storage.json")).json();
   return (await (await fetch(config.url,{cache:"no-store"})).json());
 });
 assert(Object.keys(r.entries||{}).length===0,"Remote data should be empty after delete");
 assert(problems.every(x=>!x.includes("JS error")),"Unexpected page errors: "+JSON.stringify(problems));
 console.log("PASS: two-device add, edit, checkbox, delete, remote verification");
 // Test the actual public GitHub Pages origin too, without modifying live data.
 const live=await browser.newContext();
 try{
   const livePage=await live.newPage();
   livePage.on("pageerror",e=>problems.push("live JS error: "+e.message));
   await livePage.goto("https://ryanehinkle.github.io/mc-banner-tracker/?check=live-sync", {waitUntil:"domcontentloaded",timeout:25000});
   await waitFor(livePage,()=>document.querySelector("#syncStatus")?.classList.contains("offline")===false,20000);
   const remote=await livePage.evaluate(async()=>{
     const config=await (await fetch("storage.json",{cache:"no-store"})).json();
     const result=await (await fetch(config.url,{cache:"no-store"})).json();
     return Object.values(result.entries||{}).length;
   });
   assert(remote>=0,"Public site could not read its collection");
   console.log("PASS: actual GitHub Pages origin can read live shared storage ("+remote+" banners)");
 }finally{await live.close();}

 if(problems.length)console.log("Browser console warnings:",problems.slice(0,8));
}catch(e){
 console.error("FAIL:",e.message);
 console.error("Errors:",problems.slice(0,15));
 process.exitCode=1;
}finally{
 await Promise.all([one.close(),two.close()]);
 await browser.close();
}
