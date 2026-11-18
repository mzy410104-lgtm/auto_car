"use client";

import { useMemo } from "react";
import { RoundedBox, Text, useTexture } from "@react-three/drei";
import * as THREE from "three";

// Cold white rim light color (edge separation from the dark wall).
const RIM_COLOR = "#e2e8f0";

// Neon number: deep violet, driven by very high emissive intensity.
const NEON_COLOR = "#4B1F6F"; // Amethyst Noir
const NEON_LIGHT = "#2A123F"; // Imperial Violet

// Door leaf dimensions (meters).
const LEAF_W = 2.4;
const LEAF_H = 5;
const LEAF_D = 0.3;
const LEAF_FRONT = LEAF_D / 2; // z of the leaf's front face

// Vertical layout of the three panels on the leaf (center y, height).
const TOP_PANEL = { y: 3.7, h: 2.0 };
const MID_PANEL = { y: 2.125, h: 0.55 };
const BOTTOM_PANEL = { y: 1.0, h: 1.3 };
const PANEL_W = 1.7;

const DOOR_TEXTURES = [
  "/door_texture/Plastic006_4K-JPG_Color.jpg",
  "/door_texture/Plastic006_4K-JPG_NormalGL.jpg",
  "/door_texture/Plastic006_4K-JPG_Roughness.jpg",
];

/** One PBR material shared by every part of the door (single painted object). */
function useDoorMaterial() {
  const [doorColor, doorNormal, doorRough] = useTexture(DOOR_TEXTURES);

  return useMemo(() => {
    for (const t of [doorColor, doorNormal, doorRough]) {
      t.wrapS = t.wrapT = THREE.RepeatWrapping;
      t.repeat.set(2, 2);
      t.anisotropy = 8;
    }
    doorColor.colorSpace = THREE.SRGBColorSpace;

    return new THREE.MeshPhysicalMaterial({
      color: "#050505",
      map: doorColor,
      normalMap: doorNormal,
      normalScale: new THREE.Vector2(0.8, 0.8),
      roughnessMap: doorRough,
      roughness: 1,
      metalness: 0.1,
      clearcoat: 0.1,
      clearcoatRoughness: 0.8,
    });
  }, [doorColor, doorNormal, doorRough]);
}

/** Classic raised panel: an outer slab with a smaller inset slab on top. */
function Panel({
  y,
  h,
  material,
}: {
  y: number;
  h: number;
  material: THREE.Material;
}) {
  return (
    <group position={[0, y, LEAF_FRONT]}>
      <RoundedBox
        args={[PANEL_W, h, 0.1]}
        radius={0.015}
        smoothness={2}
        position={[0, 0, 0.025]}
        material={material}
        castShadow
        receiveShadow
      />
      <RoundedBox
        args={[PANEL_W - 0.3, h - 0.3, 0.1]}
        radius={0.015}
        smoothness={2}
        position={[0, 0, 0.065]}
        material={material}
        castShadow
        receiveShadow
      />
    </group>
  );
}

function Block({
  args,
  position,
  material,
}: {
  args: [number, number, number];
  position: [number, number, number];
  material: THREE.Material;
}) {
  return (
    <mesh position={position} material={material} castShadow receiveShadow>
      <boxGeometry args={args} />
    </mesh>
  );
}

interface DoorProps {
  position: [number, number, number];
  roomNumber: string;
}

/** Paneled architectural door: frame, leaf, three panels, lever, neon number. */
export default function Door({ position, roomNumber }: DoorProps) {
  const material = useDoorMaterial();
  const postX = LEAF_W / 2 + 0.125;
  const textZ = LEAF_FRONT + 0.15;
  const rimTarget = useMemo(() => new THREE.Object3D(), []);

  return (
    <group position={position}>
      {/* ---- Frame (architrave) ---- */}
      <Block args={[0.25, 5.2, 0.5]} position={[-postX, 2.6, 0]} material={material} />
      <Block args={[0.25, 5.2, 0.5]} position={[postX, 2.6, 0]} material={material} />
      <Block args={[LEAF_W + 0.5, 0.2, 0.5]} position={[0, 5.1, 0]} material={material} />
      {/* Cornice cap on top of the lintel */}
      <Block args={[LEAF_W + 0.8, 0.1, 0.62]} position={[0, 5.25, 0.03]} material={material} />
      {/* Plinth blocks at the base of each post */}
      <Block args={[0.4, 0.45, 0.58]} position={[-postX, 0.225, 0.02]} material={material} />
      <Block args={[0.4, 0.45, 0.58]} position={[postX, 0.225, 0.02]} material={material} />

      {/* ---- Door leaf ---- */}
      <RoundedBox
        args={[LEAF_W, LEAF_H, LEAF_D]}
        radius={0.03}
        smoothness={3}
        position={[0, LEAF_H / 2, 0]}
        material={material}
        castShadow
        receiveShadow
      />

      {/* ---- Panels: one large on top, smaller ones below ---- */}
      <Panel y={TOP_PANEL.y} h={TOP_PANEL.h} material={material} />
      <Panel y={MID_PANEL.y} h={MID_PANEL.h} material={material} />
      <Panel y={BOTTOM_PANEL.y} h={BOTTOM_PANEL.h} material={material} />

      {/* ---- Lever handle (left side): rose + lever ---- */}
      <group position={[-1.0, 2.55, LEAF_FRONT]}>
        <mesh
          rotation={[Math.PI / 2, 0, 0]}
          position={[0, 0, 0.03]}
          material={material}
          castShadow
          receiveShadow
        >
          <cylinderGeometry args={[0.07, 0.07, 0.06, 32]} />
        </mesh>
        <mesh
          rotation={[0, 0, Math.PI / 2]}
          position={[0.17, 0, 0.1]}
          material={material}
          castShadow
          receiveShadow
        >
          <cylinderGeometry args={[0.022, 0.022, 0.4, 24]} />
        </mesh>
      </group>

      {/* ---- Neon number, centered in the top panel ---- */}
      <Text
        position={[0, TOP_PANEL.y, textZ]}
        fontSize={0.4}
        letterSpacing={0.12}
        anchorX="center"
        anchorY="middle"
      >
        {roomNumber}
        <meshStandardMaterial
          color={NEON_COLOR}
          emissive={NEON_COLOR}
          emissiveIntensity={10}
          toneMapped={false}
        />
      </Text>

      {/* Deep-violet light at the text. It casts shadows so the raised panel
          edges and the texture grain throw micro-shadows across the door and
          the rock wall behind. */}
      <pointLight
        position={[0, TOP_PANEL.y, textZ - 0.02]}
        color={NEON_LIGHT}
        intensity={60}
        distance={9}
        decay={1.5}
        castShadow
        shadow-mapSize={[512, 512]}
        shadow-camera-near={0.05}
        shadow-camera-far={9}
        shadow-bias={-0.0008}
        shadow-normalBias={0.02}
      />

      {/* Rim light: cold white spot above and behind the door, grazing the
          top and one side of the frame to separate it from the wall */}
      <primitive object={rimTarget} position={[0, 3.2, 0.1]} />
      <spotLight
        position={[2, 7.5, -0.6]}
        target={rimTarget}
        color={RIM_COLOR}
        intensity={120}
        angle={0.5}
        penumbra={0.6}
        distance={16}
        decay={2}
      />
    </group>
  );
}
