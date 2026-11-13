const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
let code = fs.readFileSync(path.join(__dirname, '../static/app-v2.js'), 'utf8');
code = code.replace('  boot();', `
  renderRecords = () => {}; toast = () => {}; render = () => {}; selectTab = () => {}; buildWorkoutSummary = () => ({});
  globalThis.test = {state, deleteWorkouts, restoreWorkouts, localDate, pointsInWindow, measurementRate, datePlus, saveParts, VERSIONS, KEY, hiitAlarm, stopHiitAlarm, finishWorkout, hiitRuntime, advanceHiitPhase, hiitPhaseDuration, hiitSetRoundLabel, constantMacros, constantQuantity, snapshotConstant, snapshotMacros, archivedConstantEntries, dietTotals, workoutUuid};
`);
const context = { console, Date, Math, JSON, Number, String, Set, Map, Promise, crypto: require('node:crypto').webcrypto,
  document: {addEventListener(){}, querySelector(){return null;}}, window: {addEventListener(){}}, confirm:()=>true,
  setTimeout:()=>0, clearTimeout(){}, setInterval:()=>0, clearInterval(){}, queueMicrotask };
let rejectSave = false, calls = [], version = 0;
context.fetch = async (url, options) => {const body = JSON.parse(options.body); calls.push(body); if(rejectSave) throw Error('Network unavailable'); return {ok:true,json:async()=>({versions:Object.fromEntries(Object.keys(body.data).map(k=>[k,String(++version)]))})};};
vm.createContext(context); vm.runInContext(code, context);
(async()=>{
  const t = context.test;
  const session = id => ({id,date:'2026-09-16',exercises:[]});
  t.state.workouts = {sessions:[session('a'),session('b')],trash:[]};
  await t.deleteWorkouts(['missing']); assert.equal(t.state.workouts.sessions.length,2); assert.equal(calls.length,0);
  rejectSave=true; await assert.rejects(t.deleteWorkouts(['a'])); assert.equal(t.state.workouts.sessions.length,2); assert.equal(t.state.workouts.trash.length,0); rejectSave=false;
  await Promise.all([t.deleteWorkouts(['a']),t.deleteWorkouts(['a'])]); assert.equal(t.state.workouts.sessions.length,1); assert.equal(t.state.workouts.trash.length,1);
  await t.restoreWorkouts(['a']); await t.restoreWorkouts(['a']); assert.equal(t.state.workouts.sessions.length,2); assert.equal(new Set(t.state.workouts.sessions.map(x=>x.id)).size,2);
  const points=Array.from({length:29},(_,i)=>({date:new Date(Date.UTC(2026,0,i+1)).toISOString().slice(0,10),value:90-i*.05}));
  assert.equal(t.pointsInWindow(points,7,t.datePlus(points[0].date,6)).length,7); assert.equal(t.measurementRate(points).spanDays,28);
  assert.equal(t.localDate(new Date(2026,6,1,0,30)), '2026-07-01');
  const before=calls.length; await Promise.all([t.saveParts({settings:{a:1}}),t.saveParts({settings:{a:2}})]); assert.notEqual(calls[before+1].versions.settings,calls[before].versions.settings);
  t.state.active={id:null,date:'2026-09-16',elapsedSeconds:0,exercises:[{name:'test',sets:[{done:true,reps:'1'}]}]};
  rejectSave=true; await t.finishWorkout(); assert.ok(t.state.active); assert.equal(t.state.workouts.sessions.length,2);
  context.crypto={getRandomValues: require('node:crypto').webcrypto.getRandomValues.bind(require('node:crypto').webcrypto)};
  const fallbackUuid=t.workoutUuid(); assert.match(fallbackUuid,/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
  rejectSave=false; await t.finishWorkout(); assert.equal(t.state.active,null); assert.equal(t.state.workouts.sessions.length,3); assert.match(t.state.lastWorkoutId,/^workout-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
  const nodes=[];
  const param=()=>({value:0,setValueAtTime(){},exponentialRampToValueAtTime(){},linearRampToValueAtTime(){}});
  class Audio { constructor(){this.state='running';this.currentTime=0;this.destination={}} createGain(){const n={gain:param(),connect(){return this},disconnect(){}};nodes.push(n);return n} createOscillator(){const n={frequency:param(),connect(){return this},start(){},stop(){this.stopped=true},disconnect(){}};nodes.push(n);return n} createDynamicsCompressor(){return {threshold:param(),knee:param(),ratio:param(),attack:param(),release:param(),connect(){return this},disconnect(){}}} }
  context.window.AudioContext=Audio;
  for(const alarmStyle of ['school','dive']) {await t.hiitAlarm('work',true,{alarmStyle,volume:.85,sound:true});t.stopHiitAlarm();}
  assert.ok(nodes.filter(n=>n.frequency).length>10); assert.ok(nodes.filter(n=>n.frequency).every(n=>n.stopped));
  t.hiitRuntime.config={workSeconds:10,restSeconds:2,rounds:2,sets:2,setRestSeconds:30,prepareSeconds:0}; t.hiitRuntime.status='running'; t.hiitRuntime.set=1; t.hiitRuntime.round=1; t.hiitRuntime.phase='work'; t.hiitRuntime.endAt=Date.now();
  t.advanceHiitPhase(); assert.equal(t.hiitRuntime.phase,'round-rest');
  t.advanceHiitPhase(); assert.equal(t.hiitRuntime.phase,'work'); assert.equal(t.hiitRuntime.round,2);
  t.advanceHiitPhase(); assert.equal(t.hiitRuntime.phase,'set-rest'); assert.equal(t.hiitRuntime.set,1); assert.equal(t.hiitSetRoundLabel(),'Set 1 of 2 · round 2 of 2');
  t.advanceHiitPhase(); assert.equal(t.hiitRuntime.phase,'work'); assert.equal(t.hiitRuntime.set,2); assert.equal(t.hiitRuntime.round,1);
  const recipe={id:'recipe',name:'QA recipe',calories:250,protein:10,carbs:20,fat:5,basis:'100g'}; t.state.foods={items:[recipe]}; const constant={id:'constant',foodId:'recipe',quantity:40}; const constantDay={constantSnapshots:{},constantQuantities:{}};
  assert.equal(t.constantMacros(constantDay,constant).calories,100); constantDay.constantSnapshots.constant=t.snapshotConstant(constant,40); recipe.calories=999; assert.equal(t.constantMacros(constantDay,constant).calories,100); constantDay.constantQuantities.constant=60; assert.equal(t.constantMacros(constantDay,constant).calories,150);
  const legacy={id:'legacy',name:'Two eggs',sourceMode:'legacy-portion',quantity:100,calories:144,protein:12.6,carbs:.7,fat:9.6}; const legacyDay={constantSnapshots:{},constantQuantities:{legacy:500}};
  assert.equal(t.constantMacros(legacyDay,legacy).calories,144); assert.equal(t.snapshotConstant(legacy,100).per100,false); legacyDay.constantSnapshots.legacy=t.snapshotConstant(legacy,100); assert.equal(t.constantMacros(legacyDay,legacy).calories,144);
  const convertedLegacy={...legacy,sourceMode:'per100',quantity:14}; assert.equal(t.constantQuantity(legacyDay,convertedLegacy),14);
  const archivedQuantity={id:'archived-quantity',name:'Archived ground flaxseed',sourceMode:'per100',quantity:15,calories:534,protein:18,carbs:29,fat:42,archived:true};
  const archivedDay={constants:{'archived-quantity':true},constantSnapshots:{'archived-quantity':{calories:534,protein:18,carbs:29,fat:42,per100:true,quantity:15}},constantQuantities:{'archived-quantity':15},meals:{}};
  t.state.dietSettings={constants:[archivedQuantity]}; const archivedEntries=t.archivedConstantEntries(archivedDay);
  assert.equal(archivedEntries.length,1); assert.ok(Math.abs(archivedEntries[0].macros.calories-80.1)<.0001); assert.ok(Math.abs(t.dietTotals(archivedDay).total.calories-80.1)<.0001);
  archivedDay.constants['archived-quantity']=false; assert.equal(t.dietTotals(archivedDay).total.calories,0);
  const estimatedDay={constants:{},constantSnapshots:{},constantQuantities:{},meals:{},oneTimeMeals:[{id:'estimate-1',name:'Restaurant lunch',checked:true,calories:850,protein:35.5,carbs:91,fat:32},{id:'estimate-2',name:'Unticked snack',checked:false,calories:250,protein:5,carbs:30,fat:12},{id:'estimate-3',name:'',checked:true,calories:0,protein:0,carbs:0,fat:0}]};
  t.state.dietSettings={constants:[]}; const estimatedTotals=t.dietTotals(estimatedDay);
  assert.equal(estimatedTotals.total.calories,850); assert.equal(estimatedTotals.total.protein,35.5); assert.equal(estimatedTotals.total.carbs,91); assert.equal(estimatedTotals.total.fat,32); assert.equal(estimatedTotals.completed,1); assert.equal(estimatedTotals.trackable,2);
  console.log('PASS: absent ID, failed save, repeated delete, idempotent restore, seven-day baseline, 28-day span, local date, serialized writes, alarms, set/recovery HIIT phases, quantity-linked constants, archived quantity snapshots, legacy portions, and one-time meal estimates.');
})().catch(error=>{console.error(error);process.exitCode=1});
