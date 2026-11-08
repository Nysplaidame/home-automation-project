import * as THREE from "three";
import { evaluate, toScene, validateSegment, type TrajectorySegment } from "./astronomy.ts";
import { fitOrientedCamera, motionAt, retarget, type Motion, type SphereBounds } from "./camera.ts";
import type { EphemerisBundle } from "./cache.ts";
import { connectSafetyDisplay } from "./safety-browser.ts";
import type { SafetyView } from "./safety.ts";
import { SurfaceLibrary } from "./surfaces.ts";
import { surfaceAxes, type OrientedBody } from "./orientation.ts";
import "./style.css";

const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
const canvas = $<HTMLCanvasElement>("scene");
const viewport = $("viewport");
const params = new URLSearchParams(location.search);
const reduced = matchMedia("(prefers-reduced-motion: reduce)");
const referenceRequested = params.get("reference") === "1";
const fixedTime = params.get("time");
const simulation = params.get("simulation") === "1";
const alertStorageKey = `observatory.pending-alert:${location.pathname}:${simulation ? "simulation" : "host"}`;
const names = ["earth", "jupiter", "saturn"] as const;
type Target = typeof names[number];
const bodies = {
  earth: { name: "Earth", radius: 6378.1366, polar: 6356.7519, color: 0x6b98ad, moon: "moon", moonRadius: 1737.4 },
  jupiter: { name: "Jupiter", radius: 71492, polar: 66854, color: 0xc7b197, moon: "io", moonRadius: 1821.6 },
  saturn: { name: "Saturn", radius: 60268, polar: 54364, color: 0xcdbf93, moon: null, moonRadius: 0 },
};
// Equatorial/polar radii and Saturn pole: NASA NAIF pck00011.tpc.
// Earth/Moon use approximate text-PCK attitude; other body surfaces remain illustrative.
const titleCase = (text: string) => text[0].toUpperCase() + text.slice(1);
const direction = new THREE.Vector3(0, 0.4, 1).normalize();
let target: Target = "earth";
let system = false;
let paused = false;
let pauseStarted = 0;
let alertLatched = false;
try { alertLatched = sessionStorage.getItem(alertStorageKey) === "pending"; } catch { /* Storage can be disabled; in-document latch still applies. */ }
let resumeAllowed = true;
let failed = false;
let replay = false;
let epoch = Date.now();
let bundle: EphemerisBundle;
let nextAutomatic = performance.now() + 90000;
let renderer: THREE.WebGLRenderer;
let surfaces: SurfaceLibrary;
let planetMesh: THREE.Mesh | null = null;
let orientationAvailable = false;
let moonMesh: THREE.Mesh | null = null;
let trajectory: TrajectorySegment | undefined;
let pathLine: THREE.Line | null = null;
let pathPoints: THREE.Vector3[] = [];
let bounds: SphereBounds[] = [];
let bodyBounds: SphereBounds[] = [];
let moonLabel: HTMLDivElement | null = null;
let planetLabel: HTMLDivElement | null = null;
let lastPositionUpdate = -Infinity;
let animation = 0;
let lastFrame = -Infinity;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(32, 1, 0.01, 2000);
const group = new THREE.Group();
scene.add(group);
scene.add(new THREE.AmbientLight(0xc2d4e4, 0.45));
const sun = new THREE.DirectionalLight(0xfff4dc, 2.5);
scene.add(sun);
let logDistance: Motion = { startMs: 0, durationMs: 24000, initial: { value: Math.log(7), velocity: 0, acceleration: 0 }, target: Math.log(7) };
let lookMotions: Motion[] = [0, 0, 0].map(value => ({ startMs: 0, durationMs: 24000, initial: { value, velocity: 0, acceleration: 0 }, target: value }));

function fail(message: string): void {
  failed = true;
  cancelAnimationFrame(animation);
  $("failure").hidden = false;
  $("failure").textContent = message;
  $("data-state").textContent = "Astronomy unavailable";
  $("labels").replaceChildren();
}

function disposeGroup(): void {
  for (const object of [...group.children]) {
    group.remove(object);
    object.traverse(child => {
      const drawable = child as THREE.Mesh;
      drawable.geometry?.dispose();
      const materials = Array.isArray(drawable.material) ? drawable.material : [drawable.material];
      materials.forEach(material => { if (material) { material.userData.released = true; material.dispose(); } });
    });
  }
  $("labels").replaceChildren();
  moonMesh = null;
  planetMesh = null;
  moonLabel = null;
  planetLabel = null;
  pathLine = null;
  pathPoints = [];
}

function bodyMesh(radius: number, color: number, id: string): THREE.Mesh {
  const material = new THREE.MeshStandardMaterial({ color, roughness: 1, metalness: 0 });
  surfaces.apply(id, material);
  return new THREE.Mesh(new THREE.SphereGeometry(radius, 96, 64), material);
}

function displayPoint(time: number): THREE.Vector3 {
  return new THREE.Vector3(...toScene(evaluate(trajectory!, time).positionKm, bodies[target].radius));
}

function orientSurface(mesh: THREE.Mesh, id: OrientedBody): boolean {
  try {
    const axes = surfaceAxes(id, epoch);
    const matrix = new THREE.Matrix4().makeBasis(new THREE.Vector3(...axes.x), new THREE.Vector3(...axes.y), new THREE.Vector3(...axes.z));
    mesh.quaternion.setFromRotationMatrix(matrix);
    return true;
  } catch (error) {
    if (!(error instanceof RangeError)) throw error;
    mesh.quaternion.identity();
    return false;
  }
}

function updatePositions(): void {
  const parent = bundle.segments.find(s => s.objectId === target)!;
  const first = parent.samples[0].utcMs;
  const last = parent.samples.at(-1)!.utcMs;
  epoch = replay ? Date.parse(fixedTime || "2026-10-04T01:00:00Z") : Date.now();
  if (!Number.isFinite(epoch) || epoch < first || epoch > last) throw new Error("Ephemeris coverage has expired; refresh data before continuing.");
  $("epoch").textContent = new Date(epoch).toISOString().replace("T", " ").slice(0, 19) + " UTC";
  const ageHours = Math.max(0, Math.floor((Date.now() - bundle.generatedAtMs) / 3600000));
  $("data-state").textContent = replay ? "Recorded reference / not live" : `Calculated positions / data ${ageHours}h old`;
  const position = evaluate(parent, epoch).positionKm;
  orientationAvailable = target === "earth" && planetMesh !== null && orientSurface(planetMesh, "earth");
  if (target === "earth" && moonMesh) orientationAvailable = orientSurface(moonMesh, "moon") && orientationAvailable;
  updateSurfaceNote();
  sun.position.set(...toScene(position.map(n => -n) as [number, number, number], bodies[target].radius)).normalize().multiplyScalar(100);
  if (trajectory && moonMesh && pathLine) {
    moonMesh.position.copy(displayPoint(epoch));
    // Include the evaluated instant in the line, rather than placing the mesh on a separate ellipse.
    pathPoints = trajectory.samples.map(sample => new THREE.Vector3(...toScene(sample.positionKm, bodies[target].radius)));
    const index = trajectory.samples.findIndex(sample => sample.utcMs >= epoch);
    if (index >= 0 && trajectory.samples[index].utcMs !== epoch) pathPoints.splice(index, 0, moonMesh.position.clone());
    const geometry = new THREE.BufferGeometry().setFromPoints(pathPoints);
    pathLine.geometry.dispose();
    pathLine.geometry = geometry;
  }
}

function buildSystem(): void {
  disposeGroup();
  const body = bodies[target];
  bodyBounds = [{ center: [0, 0, 0], radius: 1 }];
  const planet = bodyMesh(1, body.color, target);
  planetMesh = planet;
  planet.scale.y = body.polar / body.radius;
  group.add(planet);
  planetLabel = document.createElement("div");
  planetLabel.className = "object-label";
  planetLabel.textContent = body.name;
  $("labels").append(planetLabel);
  trajectory = body.moon ? bundle.segments.find(s => s.objectId === body.moon) : undefined;
  if (trajectory) {
    moonMesh = bodyMesh(Math.max(body.moonRadius / body.radius, 0.07), 0xb9b8ab, body.moon!);
    group.add(moonMesh);
    pathLine = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0x6d989d, transparent: true, opacity: 0.65 }));
    group.add(pathLine);
    moonLabel = document.createElement("div");
    moonLabel.className = "object-label";
    moonLabel.textContent = titleCase(body.moon!);
    $("labels").append(moonLabel);
  }
  if (target === "saturn") {
    const century = (epoch - Date.UTC(2000, 0, 1, 12)) / (36525 * 86400000);
    const ra = THREE.MathUtils.degToRad(40.589 - 0.036 * century);
    const dec = THREE.MathUtils.degToRad(83.537 - 0.004 * century);
    const pole = new THREE.Vector3(...toScene([Math.cos(dec) * Math.cos(ra), Math.cos(dec) * Math.sin(ra), Math.sin(dec)], 1));
    planet.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), pole);
    // Approximate ring bands for geometry/occlusion proof, not a photometric model.
    for (const [inner, outer, opacity] of [[1.24, 1.52, 0.25], [1.52, 1.95, 0.85], [2.03, 2.27, 0.6]]) {
      const ring = new THREE.Mesh(new THREE.RingGeometry(inner, outer, 180), new THREE.MeshStandardMaterial({
        color: 0xbeb293, roughness: 1, side: THREE.DoubleSide, transparent: true, opacity, depthWrite: false,
      }));
      ring.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), pole);
      group.add(ring);
      if (outer === 2.27) {
        for (let i = 0; i < 180; i++) {
          const angle = i / 180 * Math.PI * 2;
          const point = new THREE.Vector3(outer * Math.cos(angle), outer * Math.sin(angle), 0).applyQuaternion(ring.quaternion);
          bodyBounds.push({ center: [point.x, point.y, point.z], radius: 0.01 });
        }
      }
    }
  }
  updatePositions();
}

function frameTarget(immediate = false): void {
  const rectangle = viewport.getBoundingClientRect();
  bounds = [...bodyBounds];
  if (system && trajectory) {
    for (const point of pathPoints) bounds.push({ center: [point.x, point.y, point.z], radius: 0.15 });
    const p = moonMesh!.position;
    bounds.push({ center: [p.x, p.y, p.z], radius: Math.max(bodies[target].moonRadius / bodies[target].radius, 0.07) });
  }
  const fit = fitOrientedCamera(bounds, rectangle.width, rectangle.height, [direction.x, direction.y, direction.z], 32, system ? 0.8 : 0.7);
  const now = performance.now();
  const duration = reduced.matches || immediate ? 1 : 24000;
  logDistance = retarget(logDistance, now, Math.log(fit.distance), duration);
  lookMotions = lookMotions.map((motion, axis) => retarget(motion, now, fit.target[axis], duration));
  if (immediate || reduced.matches) {
    logDistance.initial = { value: logDistance.target, velocity: 0, acceleration: 0 };
    lookMotions.forEach(motion => { motion.initial = { value: motion.target, velocity: 0, acceleration: 0 }; });
  }
  if (moonMesh) moonMesh.visible = system;
  if (pathLine) pathLine.visible = system;
  updateSurfaceNote();
  $("coverage").textContent = trajectory && system ? `${(trajectory.samples.at(-1)!.utcMs - trajectory.samples[0].utcMs) / 3600000}h trajectory span; not a closed orbit` : target === "saturn" ? "IAU pole / approximate ring bands" : "Source: JPL Horizons";
  $("title").textContent = `${bodies[target].name}${system ? " system" : ""}`;
  $("mode").setAttribute("aria-pressed", String(system));
  $("mode").textContent = system ? "Portrait view" : "System view";
  $<HTMLSelectElement>("target").value = target;
  document.body.dataset.target = target;
  document.body.dataset.mode = system ? "system" : "portrait";
}

function updateSurfaceNote(): void {
  document.body.dataset.surfaces = surfaces.status;
  $("view-note").textContent = system ? "System / physical distances; small moons enlarged" :
    target !== "earth" ? "Portrait / matte geometry proof" :
    surfaces.status === "ready" ? (orientationAvailable ? "NASA surface map / approximate IAU orientation" : "Surface orientation unavailable / visual fallback") :
    surfaces.status === "partial" ? "Surface imagery incomplete / geometry fallback" : "Loading surface imagery";
}

function select(nextTarget: Target, nextSystem: boolean): void {
  if (failed) return;
  target = nextTarget;
  system = nextSystem;
  nextAutomatic = performance.now() + 120000;
  try { buildSystem(); frameTarget(); } catch (error) { fail(String(error)); }
}

function next(): void {
  const index = names.indexOf(target) * 2 + Number(system);
  const following = (index + 1) % 6;
  select(names[Math.floor(following / 2)], following % 2 === 1);
}

function wake(): void {
  if (!paused) pauseStarted = performance.now();
  paused = true;
  $("welcome").classList.add("visible");
  if (!alertLatched) {
    $("welcome-title").textContent = "Dashboard preview";
    $("welcome-note").textContent = "Read-only preview. No ventilation controls are available here.";
    $("resume").focus();
  }
  for (const id of ["target", "mode", "next"]) ($<HTMLButtonElement>(id)).disabled = true;
}
$("resume").addEventListener("click", () => {
  if (!resumeAllowed) return;
  const pauseDuration = performance.now() - pauseStarted;
  logDistance.startMs += pauseDuration;
  lookMotions.forEach(motion => { motion.startMs += pauseDuration; });
  paused = false;
  alertLatched = false;
  try { sessionStorage.removeItem(alertStorageKey); } catch { /* No storage permissions are required for safety display. */ }
  $("welcome").classList.remove("visible");
  $("welcome").classList.remove("alert");
  for (const id of ["target", "mode", "next"]) ($<HTMLButtonElement>(id)).disabled = false;
  nextAutomatic = performance.now() + 120000;
  $("dashboard").focus();
});
canvas.addEventListener("click", wake);
$("dashboard").addEventListener("click", wake);
$("next").addEventListener("click", next);
$("mode").addEventListener("click", () => select(target, !system));
$("target").addEventListener("change", event => select((event.target as HTMLSelectElement).value as Target, false));
canvas.addEventListener("webglcontextlost", event => { event.preventDefault(); fail("Graphics context lost. Reload to restore astronomy. The safety strip remains active."); });

function updateSafety(view: SafetyView): void {
  const setText = (id: string, value: string) => { if ($(id).textContent !== value) $(id).textContent = value; };
  setText("safety-title", view.critical ? "Failsafe active" : view.connected ? (simulation ? "Mock HA connected" : "HA connected") : "VentSys offline");
  setText("safety-note", view.connected ? `${view.label} / Fan ${view.state!.fan}` : "Live safety status unavailable");
  setText("safety-tag", simulation ? "SIMULATION" : "READ-ONLY PREVIEW");
  $("safety-strip").classList.toggle("critical", view.critical);
  document.body.dataset.safety = view.critical ? "critical" : view.connected ? "connected" : "offline";
  if (view.critical && !alertLatched) {
    alertLatched = true;
    try { sessionStorage.setItem(alertStorageKey, "pending"); } catch { /* Keep the in-document latch even if persistence is unavailable. */ }
  }
  if (alertLatched) {
    resumeAllowed = view.connected && view.state?.failsafe === "off";
    const heading = view.critical ? "Ventilation failsafe reported" : resumeAllowed ? "Failsafe cleared; inspection still required" : "Status lost after a failsafe alert";
    setText("welcome-title", simulation ? `Simulation: ${heading}` : heading);
    setText("welcome-note", resumeAllowed ? "The host now reports failsafe off. Check the ventilation system before returning to the observatory." : "Astronomy is paused. Verify ventilation using the accepted dashboard or physical controls. This preview cannot operate the system.");
    $("welcome").classList.add("alert");
    const alreadyPaused = paused;
    wake();
    if (!alreadyPaused) {
      $("welcome-title").tabIndex = -1;
      $("welcome-title").focus();
    }
  } else resumeAllowed = true;
  $<HTMLButtonElement>("resume").disabled = !resumeAllowed;
}

const disconnectSafety = connectSafetyDisplay(updateSafety);
window.addEventListener("pagehide", event => { if (!event.persisted) disconnectSafety(); });

function resize(): void {
  const rect = viewport.getBoundingClientRect();
  if (!rect.width || !rect.height) return;
  renderer.setSize(rect.width, rect.height, false);
  camera.aspect = rect.width / rect.height;
  camera.updateProjectionMatrix();
  if (bundle) frameTarget(true);
}

function label(): void {
  if (planetLabel) {
    const p = new THREE.Vector3().project(camera);
    planetLabel.hidden = !system || Math.abs(p.x) >= 1 || Math.abs(p.y) >= 1 || p.z < -1 || p.z > 1;
    planetLabel.style.left = `${Math.min(viewport.clientWidth - planetLabel.offsetWidth - 8, Math.max(8, (p.x + 1) * viewport.clientWidth / 2 + 14))}px`;
    planetLabel.style.top = `${Math.min(viewport.clientHeight - 28, Math.max(8, (1 - p.y) * viewport.clientHeight / 2 + 14))}px`;
  }
  if (!moonLabel || !moonMesh) return;
  const p = moonMesh.position.clone().project(camera);
  const w = viewport.clientWidth;
  const h = viewport.clientHeight;
  // Hide labels for moons occulted by the central unit sphere.
  const ray = new THREE.Ray(camera.position, moonMesh.position.clone().sub(camera.position).normalize());
  const hit = ray.intersectSphere(new THREE.Sphere(new THREE.Vector3(), 1), new THREE.Vector3());
  const occluded = hit && hit.distanceTo(camera.position) < moonMesh.position.distanceTo(camera.position);
  const visible = system && !occluded && p.z >= -1 && p.z <= 1 && Math.abs(p.x) < 0.98 && Math.abs(p.y) < 0.98;
  moonLabel.hidden = !visible;
  if (visible) {
    moonLabel.style.left = `${Math.min(w - moonLabel.offsetWidth - 8, Math.max(8, (p.x + 1) * w / 2 + 12))}px`;
    moonLabel.style.top = `${Math.min(h - 28, Math.max(8, (1 - p.y) * h / 2 - 10))}px`;
  }
}

function draw(now: number): void {
  if (failed) return;
  animation = requestAnimationFrame(draw);
  if (document.hidden || paused || now - lastFrame < 1000 / 30) return;
  lastFrame = now;
  try {
    if (now - lastPositionUpdate > 1000) { updatePositions(); lastPositionUpdate = now; }
    if (now > nextAutomatic && !reduced.matches) next();
    const look = new THREE.Vector3(...lookMotions.map(m => motionAt(m, now).value) as [number, number, number]);
    const distance = Math.exp(motionAt(logDistance, now).value);
    camera.position.copy(look).addScaledVector(direction, distance);
    camera.near = 0.01;
    camera.far = Math.max(2000, distance * 4);
    camera.updateProjectionMatrix();
    camera.lookAt(look);
    camera.updateMatrixWorld();
    label();
    renderer.render(scene, camera);
  } catch (error) { fail(String(error)); }
}

async function loadData(): Promise<void> {
  let data: EphemerisBundle | null = null;
  if (!referenceRequested) {
    const response = await fetch("./data/current.json");
    if (response.ok) data = await response.json();
  }
  const now = Date.now();
  if (!data || !Array.isArray(data.segments) || !data.segments.filter(s => s.objectId !== "jwst").every(s => now >= s.samples[0].utcMs && now <= s.samples.at(-1)!.utcMs)) {
    const response = await fetch("./data/reference.json");
    if (!response.ok) throw new Error("No ephemeris data available");
    data = await response.json();
    replay = true;
  }
  if (data?.version !== 1 || !Array.isArray(data.segments)) throw new Error("Invalid ephemeris bundle");
  data.segments.forEach(validateSegment);
  for (const id of ["earth", "moon", "jupiter", "io", "saturn"]) {
    if (data.segments.filter(s => s.objectId === id).length !== 1) throw new Error(`Missing or duplicate ${id} trajectory`);
  }
  bundle = data;
}

async function start(): Promise<void> {
  try {
    await loadData();
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    surfaces = new SurfaceLibrary(renderer.capabilities.getMaxAnisotropy(), updateSurfaceNote);
    surfaces.preload();
    buildSystem();
    resize();
    const observer = new ResizeObserver(resize);
    observer.observe(viewport);
    reduced.addEventListener("change", () => frameTarget(true));
    animation = requestAnimationFrame(draw);
    // Read-only diagnostics for geometry QA; no HA messages, commands or clock mutation.
    Object.assign(window, { observatoryDiagnostics: () => {
      const projectedMoon = moonMesh?.getWorldPosition(new THREE.Vector3()).project(camera);
      const vertices = pathLine?.geometry.getAttribute("position");
      const pathError = projectedMoon && vertices?.count ? Math.min(...Array.from({ length: vertices.count }, (_, i) => {
        const p = new THREE.Vector3().fromBufferAttribute(vertices, i).applyMatrix4(pathLine!.matrixWorld).project(camera);
        return Math.hypot((p.x - projectedMoon.x) * viewport.clientWidth / 2, (p.y - projectedMoon.y) * viewport.clientHeight / 2);
      })) : null;
      return { target, system, replay, paused, failed, epoch, pathErrorPixels: pathError,
        canvasCount: document.querySelectorAll("canvas").length, geometries: renderer.info.memory.geometries,
        textures: renderer.info.memory.textures, surfaces: surfaces.status,
        orientationAvailable, planetRotation: planetMesh?.quaternion.toArray(), moonRotation: moonMesh?.quaternion.toArray(),
        position: camera.position.toArray(), distance: camera.position.length(),
        meshes: group.children.length, pathSamples: pathPoints.length,
        planet: new THREE.Vector3().project(camera).toArray(),
        moon: projectedMoon?.toArray(),
      };
    } });
    document.body.dataset.ready = "true";
    window.addEventListener("pagehide", event => {
      if (!event.persisted) { cancelAnimationFrame(animation); observer.disconnect(); disposeGroup(); surfaces.dispose(); renderer.dispose(); }
    });
  } catch (error) { fail(`Unable to start observatory: ${String(error)}`); }
}
void start();
