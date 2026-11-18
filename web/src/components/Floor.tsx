"use client";

import { MeshReflectorMaterial } from "@react-three/drei";
import { MAX_X, MIN_X, WALL_W, WALL_Z_BACK } from "@/components/Wall";

const FLOOR_DEPTH = 40;

/** Polished dark floor meeting the wall at y = 0 so the doors stand on it. */
export default function Floor() {
  return (
    <mesh
      rotation={[-Math.PI / 2, 0, 0]}
      position={[(MIN_X + MAX_X) / 2, 0, WALL_Z_BACK + FLOOR_DEPTH / 2]}
      receiveShadow
    >
      <planeGeometry args={[WALL_W, FLOOR_DEPTH]} />
      <MeshReflectorMaterial
        blur={[300, 100]}
        resolution={512}
        mixBlur={1}
        mixStrength={6}
        roughness={0.35}
        depthScale={1}
        minDepthThreshold={0.4}
        maxDepthThreshold={1.4}
        color="#060606"
        metalness={0.4}
        mirror={0.6}
      />
    </mesh>
  );
}
