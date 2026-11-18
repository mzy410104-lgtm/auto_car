# PROJECT VISUAL IDENTITY & DESIGN SYSTEM: "SPATIAL SHUTTLE"

You must reference and strictly enforce these rules for every component, UI layout, and 3D scene built for this project.

---

## 1. Core Concept & Aesthetic
* **Vibe:** A high-end, premium fusion of Apple's visionOS (liquid glass UI) and Tesla's automotive minimalism (sleek, dark 3D environments).
* **Architecture:** A "Spatial Interface." The background is entirely a live 3D WebGL canvas (React Three Fiber). All HTML UI exists as floating, minimal, heavily blurred glass panels overlaid on top.

---

## 2. Color Palette (Strictly Enforced)
Use these exact colors for UI highlights, glowing 3D elements, and text accents:

* **Imperial Violet (`#2A123F`):** Deep background gradients and primary 3D emissive neon lights (e.g., the glowing numbers on the doors).
* **Amethyst Noir (`#4B1F6F`):** Secondary deep shadows and ambient 3D lighting.
* **Dusted Lavender (`#9C86B9`):** Subdued UI icons, disabled states, and ambient background orbs.
* **Orchid Smoke (`#C686DD`):** Active states, vibrant hover glows, and soft UI highlights.
* **Moon Pearl (`#F1EDF7`):** Primary text, crisp specular borders on glass elements, and bright 3D accents (like the shuttle's headlight).

---

## 3. The HTML UI Layer: "Liquid Glass" (Tailwind CSS)
Never use flat, opaque matte panels. All UI containers must be highly translucent glass.

* **Material:** Apply extreme backdrop blur (e.g., `backdrop-blur-2xl`) so the panels act like thick glass distorting the 3D scene behind them.
* **Fill:** Use highly transparent, neutral backgrounds (`bg-white/5` or `bg-black/10`). Rely on the 3D scene below to provide the actual color.
* **Edge Highlights (Specular):** Every glass card and button must have a crisp, 1px semi-transparent white inner border (`border border-white/20` or `border-white/10`) to simulate bright light catching the rim of the glass.
* **Typography:** High contrast. Primary text is pure white (`#F1EDF7`). Secondary text is slightly transparent (`text-white/60`). Prioritize the `system-ui` font stack (Apple's San Francisco).
* **Shapes:** Use pill-shaped (fully rounded `rounded-full`) buttons and apply heavy, smooth rounding (`rounded-2xl` or `rounded-3xl`) to all interface cards.

---

## 4. The 3D Layer: "Automotive Minimalism" (React Three Fiber)
* **Environment:** A pure black void (`#000000`).
* **Floors:** Polished, highly reflective black (`MeshReflectorMaterial`). It must mirror the glowing elements above it.
* **Geometry (Doors & Shuttle):** Matte black, sleek, untextured, light-absorbing materials. No wood grain, no complex textures.
* **Illumination:** High-contrast emissive lighting. Text on doors glows brightly using Imperial Violet (`#2A123F` / vibrant neon violet). The shuttle casts actual light onto the dark floor.

---

## 5. Motion & Animation (GSAP & R3F)
* Transitions must be cinematic, fluid, and physically based.
* No abrupt snapping. Camera movements (like the pullback from the first-person door view to the isometric tracking view) must use elegant easing curves (`power3.inOut`).
* UI panels should slide, fade, and dynamically resize (like a Dynamic Island), never just instantly popping into existence.
