"use client";

import dynamic from "next/dynamic";
import { Suspense, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { useShuttleStore } from "@/lib/store";

// WebGL is client-only: never server-render the canvas.
const Scene = dynamic(() => import("@/components/Scene"), { ssr: false });

function QrDoorSync() {
  const params = useSearchParams();
  const setPickupId = useShuttleStore((s) => s.setPickupId);
  useEffect(() => {
    const id = params.get("door");
    if (id) setPickupId(id);
  }, [params, setPickupId]);
  return null;
}

export default function HomePage() {
  return (
    <main className="fixed inset-0 h-screen w-screen overflow-hidden bg-black">
      <Suspense fallback={null}>
        <QrDoorSync />
      </Suspense>
      <Scene />
    </main>
  );
}
