import * as THREE from "three";

type Surface = "earth" | "moon";

// Two shared 2K maps: bounded residency rather than one allocation per focus.
export class SurfaceLibrary {
  private maps = new Map<Surface, THREE.Texture>();
  private pending = new Map<Surface, Promise<THREE.Texture | null>>();
  private disposed = false;
  private failures = new Set<Surface>();

  constructor(private anisotropy: number, private changed: () => void) {}

  get status(): string { return this.failures.size ? "partial" : this.maps.size === 2 ? "ready" : "loading"; }

  apply(id: string, material: THREE.MeshStandardMaterial): void {
    if (id !== "earth" && id !== "moon") return;
    const ready = this.maps.get(id);
    const install = (map: THREE.Texture | null) => {
      if (!map || this.disposed || material.userData.released) return;
      material.map = map;
      material.color.set(0xffffff);
      material.needsUpdate = true;
    };
    if (ready) install(ready);
    else void this.load(id).then(install);
  }

  preload(): void { void this.load("earth"); void this.load("moon"); }

  private load(id: Surface): Promise<THREE.Texture | null> {
    const existing = this.pending.get(id);
    if (existing) return existing;
    const request = (async () => {
      try {
        const response = await fetch(`./assets/${id}.jpg`, { signal: AbortSignal.timeout(8000) });
        if (!response.ok) throw new Error("Surface unavailable");
        const bitmap = await createImageBitmap(await response.blob(), { imageOrientation: "flipY" });
        if (this.disposed) { bitmap.close(); return null; }
        const texture = new THREE.Texture(bitmap);
        texture.flipY = false;
        texture.colorSpace = THREE.SRGBColorSpace;
        texture.anisotropy = Math.min(4, this.anisotropy);
        texture.needsUpdate = true;
        this.maps.set(id, texture);
        return texture;
      } catch {
        this.failures.add(id);
        return null;
      } finally { if (!this.disposed) this.changed(); }
    })();
    this.pending.set(id, request);
    return request;
  }

  dispose(): void {
    this.disposed = true;
    for (const map of this.maps.values()) { map.dispose(); (map.image as ImageBitmap).close(); }
    this.maps.clear();
  }
}
