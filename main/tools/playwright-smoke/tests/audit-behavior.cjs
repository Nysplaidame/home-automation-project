const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '../../../dashboards');
function extract(source, name) {
  const match = source.match(new RegExp(`  function ${name}\\([^]*?\\n  }`));
  assert(match, name);
  return match[0];
}
const card = fs.readFileSync(path.join(root, 'ventsys-card.js'), 'utf8');
assert(!card.includes('postMessage('));
assert(!card.includes('new WebSocket'));

const screensaver = fs.readFileSync(path.join(root, 'ventsys_solar_screensaver.html'), 'utf8');
const sockets = [], timers = [];
class Socket { constructor() { sockets.push(this); } send() {} close() { this.onclose(); } }
const screen = vm.createContext({CONFIG:{ha:{token:'test-only',wsUrl:'wss://test.invalid'}}, state:{ha:{}},
  WebSocket:Socket, setTimeout:(fn,delay)=>timers.push(delay), updateSafetyStrip() {}, applyHaState() {}});
vm.runInContext(extract(screensaver, 'connectHa') + '\nconnectHa();', screen);
assert.doesNotThrow(() => sockets[0].onmessage({data:'not-json'}));
sockets[0].onmessage({data:JSON.stringify({type:'auth_invalid'})});
assert.deepEqual(timers, []);
console.log('PASS: authenticated card has no frame command bridge; malformed frames ignored; invalid auth stops reconnect');
