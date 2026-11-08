const {test,expect}=require('@playwright/test');
const {openCard}=require('./ventsys-fixture.cjs');
const path=require('node:path'),os=require('node:os');

for(const size of [{width:800,height:480},{width:1024,height:600}]) {
  test(`touch diagram fits ${size.width}x${size.height} and menus do not change the diagram`,async({page})=>{
    await page.setViewportSize(size);await openCard(page,{layout:'touch'});
    await expect(page.locator('.touch-logo')).toHaveText('PRINTAIRPIPE');
    await expect(page.locator('#touch-clock')).toHaveText(/\d\d:\d\d:\d\d/);
    await expect(page.locator('.touch-statusbar')).toContainText('Unmeasured');
    await expect(page.locator('#touch-menu')).not.toBeVisible();
    await expect(page.locator('#diagram')).toHaveAttribute('viewBox','0 0 1300 820');
    await expect(page.locator('#circle-enc1-print')).toHaveAttribute('cy','598');
    const bounds=await page.locator('#diagram').boundingBox();
    expect(bounds.y+bounds.height).toBeLessThanOrEqual(size.height);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(size.width);
    const buttons=await page.locator('.touch-toolbar button').all();for(const button of buttons)expect((await button.boundingBox()).height).toBeGreaterThanOrEqual(44);
    await page.screenshot({path:path.join(os.tmpdir(),`ventsys-touch-${size.width}.png`)});
    await page.locator('#diagram [data-select="fdm_360"]').click();
    await expect(page.locator('#touch-menu')).toBeVisible();await expect(page.locator('#device-name')).toHaveText('FDM 360° intake');
    await expect(page.locator('#position-slider')).toHaveAttribute('min','0');
    await page.locator('#touch-close').click();await expect(page.locator('#touch-menu')).not.toBeVisible();
    await page.locator('#environment-box').click();await expect(page.locator('#touch-menu-title')).toHaveText('Environmental sensors');
    await page.keyboard.press('Escape');await expect(page.locator('#touch-menu')).not.toBeVisible();
    await page.locator('#svg-log-box').click();await expect(page.locator('#touch-menu-title')).toHaveText('System log · this session');
    expect(await page.evaluate(()=>window.calls)).toEqual([]);
  });
}

test('touch commands retain confirmation, cancellation and failsafe gates',async({page})=>{
  await page.setViewportSize({width:800,height:480});await openCard(page,{layout:'touch'});
  await page.locator('[data-touch-menu="controls"]').click();
  await page.locator('#position-number').fill('75');await page.locator('#position-number').press('Tab');
  await expect(page.locator('dialog[aria-labelledby="confirm-title"]')).toBeVisible();
  expect(await page.evaluate(()=>window.calls)).toEqual([]);
  await page.locator('#cancel-command').click();await expect(page.locator('#touch-menu')).toBeVisible();
  await page.evaluate(()=>{window.fixture.states['input_boolean.ventsys_failsafe'].state='on';window.card.hass={...window.fixture};});
  await expect(page.locator('#position-number')).toBeDisabled();
  await page.locator('#touch-close').click();await expect(page.locator('[data-touch-menu="status"]')).toHaveClass('alarm');
  await page.locator('[data-touch-menu="status"]').click();await expect(page.locator('#fault-title')).toContainText('Failsafe active');
  expect(await page.evaluate(()=>window.calls)).toEqual([]);
});

test('duct highlights end inside the main duct and log messages use larger type',async({page})=>{
  await openCard(page);
  for(const id of ['main-duct-highlight-top','main-duct-highlight-bottom']) {
    const end=await page.locator('#'+id).evaluate(node=>Number(node.getAttribute('x'))+Number(node.getAttribute('width')));
    expect(end).toBeLessThanOrEqual(1252);
  }
  await expect(page.locator('#log-msg-1')).toHaveAttribute('font-size','20');
  await expect(page.locator('#log-ts-1')).toHaveAttribute('font-size','18');
  await expect(page.locator('.touch-toolbar')).toHaveCount(0);
});

test('reported closed/open valves use saturated endpoint colours including calibrated intakes',async({page})=>{
  await openCard(page);
  await page.evaluate(()=>{
    const values={
      'number.ventsys_e1_branch_valve_valve_position':'0',
      'number.ventsys_e2_branch_valve_valve_position':'0',
      'number.ventsys_main_duct_valve_1_valve_position':'100',
      'number.ventsys_sla_360_intake_valve_valve_position':'30',
      'number.ventsys_fdm_360_intake_valve_valve_position':'60'};
    for(const [id,value] of Object.entries(values)) window.fixture.states[id].state=value;
    window.card.hass={...window.fixture};
  });
  for(const id of ['ellipse-enc1-vert','ellipse-enc2-vert']) await expect(page.locator('#'+id)).toHaveAttribute('fill','#e00000');
  await expect(page.locator('#ellipse-main-1')).toHaveAttribute('fill','#00ff00');
  await expect(page.locator('#circle-360-enc1')).toHaveAttribute('stroke','#e00000');
  await expect(page.locator('#circle-360-enc2')).toHaveAttribute('stroke','#00ff00');
  await expect(page.locator('#valve-enc1-vert-pos')).toHaveAttribute('fill','#e00000');
  await page.evaluate(()=>{window.fixture.states['number.ventsys_e2_branch_valve_valve_position'].state='unavailable';window.card.hass={...window.fixture};});
  await expect(page.locator('#ellipse-enc2-vert')).toHaveAttribute('fill','#91a2b8');
});

test('log, enclosure and booth frames share a bottom edge',async({page})=>{
  await page.setViewportSize({width:1024,height:600});await openCard(page,{layout:'touch'});
  const bottoms=await page.locator('#system-log-frame,#enclosure1-frame,#enclosure2-frame,#spray-booth-frame').evaluateAll(nodes=>nodes.map(node=>Number(node.getAttribute('y'))+Number(node.getAttribute('height'))));
  expect(bottoms).toHaveLength(4);expect(bottoms.every(bottom=>bottom===800)).toBe(true);
  await page.screenshot({path:path.join(os.tmpdir(),'ventsys-aligned-colours.png')});
});
