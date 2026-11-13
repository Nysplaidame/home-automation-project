const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname,'../../../dashboards/ventsys-bridge-page.js'),'utf8');
const nodes = { '#status':{textContent:'Offline'}, '#failsafe':{textContent:''} };
const handlers = {}, parent = {}, location = {origin:'http://ventsys.test'};
let timeout;
const window = {parent, addEventListener:(name,fn)=>handlers[name]=fn};
const document = {documentElement:{dataset:{ventsysSession:'random-session'}},querySelector:s=>nodes[s]};
vm.runInNewContext(source,{window,document,location,Date,Number,Array,Object,clearTimeout:()=>{},setTimeout:fn=>{timeout=fn;return 1;}});
let sequence = 0;
function message(overrides={}, event={}) {
 const now=Date.now(); const data={version:1,type:'state_snapshot',sessionId:'random-session',sequence:++sequence,issuedAtMs:now,expiresAtMs:now+15000,payload:{failsafe:'off'},...overrides};
 handlers.message({data,origin:location.origin,source:parent,...event});
}
function connected() { message(); assert.equal(nodes['#status'].textContent,'Connected'); }
connected(); assert.equal(nodes['#failsafe'].textContent,'Failsafe: off');
for (const [change,event] of [[{sessionId:'wrong'},{}],[{}, {origin:'http://evil.test'}],[{}, {source:{}}],[{sequence:1},{}],[{issuedAtMs:Date.now()-20000,expiresAtMs:Date.now()-1},{}],[{payload:{failsafe:'off',extra:'secret'}},{}],[{type:'command'},{}],[{version:2},{}]]) {
 message(change,event); assert.equal(nodes['#status'].textContent,'Offline'); assert.equal(nodes['#failsafe'].textContent,''); connected();
}
timeout(); assert.equal(nodes['#status'].textContent,'Offline'); assert.equal(nodes['#failsafe'].textContent,'');
connected(); message({type:'offline',payload:undefined}); assert.equal(nodes['#status'].textContent,'Offline');
console.log('PASS: authenticated snapshot, foreign messages, replay, expiry, schema, command and timeout');
