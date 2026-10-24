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
 const r=await first.evaluate(async()=>{
   const config=await (await fetch("/storage.json")).json();
   return (await (await fetch(config.url,{cache:"no-store"})).json());
 });
 assert(Object.keys(r.entries||{}).length===0,"Remote data should be empty after delete");
 assert(problems.every(x=>!x.includes("JS error")),"Unexpected page errors: "+JSON.stringify(problems));
 console.log("PASS: two-device add, edit, checkbox, delete, remote verification");
 if(problems.length)console.log("Browser console warnings:",problems.slice(0,8));
}catch(e){
 console.error("FAIL:",e.message);
 console.error("Errors:",problems.slice(0,15));
 process.exitCode=1;
}finally{
 await Promise.all([one.close(),two.close()]);
 await browser.close();
}
