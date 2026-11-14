// Exercises the actual checklist script without external applications or storage.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const handlers={},values=new Map();
function el(id){return {id,hidden:id==='vt-send-actions',textContent:'',href:'',addEventListener:(event,fn)=>handlers[id+':'+event]=fn};}
const ids=['vt-request-builder','vt-request-output','vt-send-actions','vt-tool-status','vt-send-wa','vt-send-mail','vt-copy','vt-print'];
const elements=Object.fromEntries(ids.map(id=>[id,el(id)]));
let copied='',prints=0;
const context={document:{getElementById:id=>elements[id]},FormData:class{get(k){return values.get(k)}},navigator:{clipboard:{writeText:async t=>{copied=t}}},window:{print:()=>prints++},encodeURIComponent};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../assets/checklist.js'),'utf8'),context);
values.set('kavel','Kavel 123 & toebehoren');values.set('link','https://example.test/kavel?x=1&y=2');values.set('laden','Gent, België');values.set('lossen','Oudenaarde, België');
handlers['vt-request-builder:submit']({preventDefault(){}});
assert.match(elements['vt-request-output'].textContent,/Kavel 123 & toebehoren/);
assert.match(elements['vt-request-output'].textContent,/Nog aan te vullen/);
assert.equal(elements['vt-send-actions'].hidden,false);
const wa=new URL(elements['vt-send-wa'].href);
assert.equal(wa.origin+wa.pathname,'https://wa.me/32471379064');
assert.equal(wa.searchParams.get('text'),elements['vt-request-output'].textContent);
assert.equal(elements['vt-send-mail'].href.split('?')[0],'mailto:depannageacr@hotmail.com');
assert.match(decodeURIComponent(elements['vt-send-mail'].href),/Kavel 123 & toebehoren/);
(async()=>{await handlers['vt-copy:click']();assert.equal(copied,elements['vt-request-output'].textContent);handlers['vt-print:click']();assert.equal(prints,1);handlers['vt-request-builder:reset']();assert.equal(elements['vt-send-actions'].hidden,true);console.log('PASS: checklist output, incomplete fields, WhatsApp encoding, email recipient, copy, print and reset.');})();
