"use client";

import { Suspense, useEffect, useState } from "react";
import { Canvas } from "@react-three/fiber";
import {
  BakeShadows,
  ContactShadows,
  Environment,
  ScrollControls,
} from "@react-three/drei";
import { Bloom, EffectComposer, Vignette } from "@react-three/postprocessing";
import Door from "@/components/Door";
import Wall from "@/components/Wall";
import Floor from "@/components/Floor";
import CameraRig from "@/components/CameraRig";
import { DOORS, WALL_Z } from "@/lib/hallway";

// Horizontal center of the door row, so the contact shadows sit under all doors.
const ROW_CENTER_X = (DOORS[0].x + DOORS[DOORS.length - 1].x) / 2;

export default function Scene() {
  const [dpr, setDpr] = useState<[number, number]>([1, 1.5]);

  useEffect(() => {
    // Cap pixel ratio lower on small/mobile screens.
    if (window.innerWidth < 768) setDpr([1, 1.25]);
  }, []);

  return (
    <Canvas
      shadows
      frameloop="demand" // only render while something changes (scroll, loading)
      dpr={dpr}
      camera={{ position: [4, 1.6, 2.5], fov: 55, near: 0.1, far: 100 }}
      // No MSAA: bloom hides most aliasing and MSAA is costly on phones
      gl={{ antialias: false, powerPreference: "high-performance" }}
    >
      <color attach="background" args={["#000000"]} />

      {/* Very dim ambient + a steep ceiling light grazing the top edges */}
      <ambientLight intensity={0.04} />
      <directionalLight position={[0, 14, 2]} intensity={1.2} color="#ffffff" />

      <Suspense fallback={null}>
        {/* Faint studio reflections for the doors */}
        <Environment preset="studio" environmentIntensity={0.15} />
        <ScrollControls pages={5} damping={0.2} horizontal>
          <Wall />
          <Floor />
          {DOORS.map((d) => (
            <Door key={d.id} position={[d.x, 0, WALL_Z]} roomNumber={d.roomNumber} />
          ))}

          {/* Contact shadows grounding the doors on the floor */}
          <ContactShadows
            position={[ROW_CENTER_X, 0.01, WALL_Z]}
            scale={60}
            opacity={0.8}
            blur={2.5}
            far={10}
            frames={1} // doors are static: render the contact shadows once
            color="#000000"
          />
          <CameraRig />
        </ScrollControls>

        {/* Doors and lights are static: render the shadow maps only once */}
        <BakeShadows />
      </Suspense>

      <EffectComposer multisampling={0}>
        <Bloom intensity={1.5} luminanceThreshold={0.3} mipmapBlur />
        <Vignette eskil={false} offset={0.2} darkness={0.8} />
      </EffectComposer>
    </Canvas>
  );
}
