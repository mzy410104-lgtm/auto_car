"use client";

import { useEffect } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import { useScroll } from "@react-three/drei";
import * as THREE from "three";
import {
  CAMERA_DISTANCE,
  DOORS,
  EYE_HEIGHT,
  WALL_Z,
  findDoor,
} from "@/lib/hallway";
import { useShuttleStore } from "@/lib/store";

const lookTarget = new THREE.Vector3();
const minX = DOORS[0].x;
const maxX = DOORS[DOORS.length - 1].x;

/**
 * Pans the camera along the hallway. The horizontal scroll offset (0..1) from
 * <ScrollControls> maps to the camera X; Y/Z are fixed at eye level.
 * Must be rendered inside <ScrollControls>.
 */
export default function CameraRig() {
  const { camera } = useThree();
  const scroll = useScroll();
  const pickupId = useShuttleStore((s) => s.pickupId);

  // Start the scroll position at the scanned pickup door.
  useEffect(() => {
    const t = (findDoor(pickupId).x - minX) / (maxX - minX);
    const el = scroll.el;
    el.scrollLeft = t * (el.scrollWidth - el.clientWidth);
  }, [pickupId, scroll]);

  useFrame(() => {
    const x = THREE.MathUtils.lerp(minX, maxX, scroll.offset);
    camera.position.x = x;
    camera.position.y = EYE_HEIGHT;
    camera.position.z = WALL_Z + CAMERA_DISTANCE;
    lookTarget.set(x, 2.1, WALL_Z);
    camera.lookAt(lookTarget);
  });

  return null;
}
