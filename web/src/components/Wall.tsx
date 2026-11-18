"use client";

import { DOORS, WALL_Z } from "@/lib/hallway";

// Wall sits flush behind the door frames (frame depth is 0.5, centered on WALL_Z).
export const WALL_Z_BACK = WALL_Z - 0.25;
export const MIN_X = DOORS[0].x - 14;
export const MAX_X = DOORS[DOORS.length - 1].x + 14;
export const WALL_W = MAX_X - MIN_X;
const WALL_H = 30;

/** Plain matte dark wall that the doors are pinned to (no texture). */
export default function Wall() {
  return (
    <mesh
      position={[(MIN_X + MAX_X) / 2, WALL_H / 2, WALL_Z_BACK]}
      castShadow
      receiveShadow
    >
      <planeGeometry args={[WALL_W, WALL_H]} />
      <meshPhysicalMaterial color="#0a0a0a" roughness={1} metalness={0} />
    </mesh>
  );
}
