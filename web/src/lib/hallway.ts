/**
 * Hallway layout (meters). Step 1 builds Wing A only: a straight corridor
 * running along +X from the corner hub at the origin. Doors sit on the back
 * wall (z = WALL_Z) and face +Z toward the corridor centerline.
 * Wing B / the L-shaped corner is added in a later step.
 */
export interface DoorSpec {
  id: string;
  roomNumber: string;
  x: number;
}

export const WALL_Z = -2;
export const DOOR_SPACING = 4;
export const EYE_HEIGHT = 1.6;
export const CAMERA_DISTANCE = 6; // distance in front of the door wall

export const DOORS: DoorSpec[] = ["101", "102", "103", "104", "105", "106"].map(
  (roomNumber, i) => ({
    id: `ROOM_${roomNumber}`,
    roomNumber,
    x: 4 + i * DOOR_SPACING,
  })
);

export function findDoor(id: string | null | undefined): DoorSpec {
  return DOORS.find((d) => d.id === id) ?? DOORS[0];
}
