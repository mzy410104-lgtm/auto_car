import { create } from "zustand";

export type Phase = "landing" | "selection" | "tracking";

interface ShuttleState {
  phase: Phase;
  /** Door the user scanned (their pickup door). */
  pickupId: string;
  setPhase: (phase: Phase) => void;
  setPickupId: (id: string) => void;
}

export const useShuttleStore = create<ShuttleState>((set) => ({
  phase: "landing",
  pickupId: "ROOM_101",
  setPhase: (phase) => set({ phase }),
  setPickupId: (pickupId) => set({ pickupId }),
}));
