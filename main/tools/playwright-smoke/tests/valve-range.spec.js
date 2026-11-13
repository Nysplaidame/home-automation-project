const { test, expect } = require('@playwright/test');
const { openCard } = require('./ventsys-fixture.cjs');
test('standard valves retain full 0–100 range; 360 controls retain their correct 30–60 range', async ({ page }) => {
  await openCard(page);
  for (const key of ['main1','main2','fdm_branch','fdm_print','fdm_360','sla_branch','sla_print','sla_360']) {
    await page.locator(`[data-device="${key}"]`).click();
    await expect(page.locator('#position-slider')).toHaveAttribute('max',key.endsWith('_360') ? '60' : '100');
    for (const value of (key.endsWith('_360') ? [30,45,60] : [0,25,50,75,100])) {
      await page.evaluate(async ({key,value})=>{
        const {DEVICES}=await import('/ventsys-model.mjs?v=20261027-1');
        window.fixture.states[DEVICES[key].native[0]].state=String(value);
        window.card.hass={...window.fixture};
      },{key,value});
      await expect(page.locator('#device-value')).toHaveText(String(value));
    }
  }
  expect(await page.evaluate(()=>window.calls)).toEqual([]);
});
