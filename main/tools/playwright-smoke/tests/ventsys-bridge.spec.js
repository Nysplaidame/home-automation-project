const {test, expect} = require('@playwright/test');
const fs = require('node:fs'), path = require('node:path');
const root = path.resolve(__dirname, '../../../dashboards');
test('bridge delivers authenticated state and clears it on rejection and disconnect', async ({page}) => {
 await page.route('**/*', route => {
  const name = new URL(route.request().url()).pathname.slice(1);
  if (name === 'host') return route.fulfill({contentType:'text/html',body:'<script type="module" src="/ventsys-bridge-card.js"></script>'});
  if (!['ventsys-bridge-card.js','ventsys-bridge-page.js','ventsys-bridge-page.html'].includes(name)) return route.fulfill({status:404});
  return route.fulfill({contentType:name.endsWith('.html')?'text/html':'text/javascript',body:fs.readFileSync(path.join(root,name),'utf8')});
 });
 await page.goto('http://ventsys.test/host');
 await page.evaluate(async()=>{await customElements.whenDefined('ventsys-bridge-card'); window.card=document.createElement('ventsys-bridge-card'); document.body.append(card); card.hass={connection:{connected:true},states:{'input_boolean.ventsys_failsafe':{state:'on'}}};});
 const frame=page.frameLocator('ventsys-bridge-card iframe');
 await expect(frame.locator('#failsafe')).toHaveText('Failsafe: on');
 await page.evaluate(()=>card.frame.contentWindow.dispatchEvent(new MessageEvent('message',{origin:'http://evil.test',source:window,data:card.envelope('state_snapshot',{failsafe:'off'})})));
 await expect(frame.locator('#status')).toHaveText('Offline');
 await page.evaluate(()=>card.send()); await expect(frame.locator('#status')).toHaveText('Connected');
 const old=await page.evaluate(()=>card.session); await page.evaluate(()=>card.frame.contentWindow.location.reload());
 await expect.poll(()=>page.evaluate(()=>card.session)).not.toBe(old); await expect(frame.locator('#status')).toHaveText('Connected');
 await page.evaluate(()=>card.hass={connection:{connected:false}}); await expect(frame.locator('#status')).toHaveText('Offline'); await expect(frame.locator('#failsafe')).toBeEmpty();
});
