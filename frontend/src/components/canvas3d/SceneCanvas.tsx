import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { BroadcastCore } from './BroadcastCore';
import { ServiceNodes } from './ServiceNodes';

interface SceneCanvasProps {
  status: string;
  activeWeights: Record<string, number>;
  predictiveState?: string;
  riskScore?: number;
}

export const SceneCanvas: React.FC<SceneCanvasProps> = ({
  status,
  activeWeights,
  predictiveState,
  riskScore = 0,
}) => {
  return (
    <div className="relative h-64 sm:h-72 w-full rounded-xl overflow-hidden glass-panel border border-white/10 flex items-center justify-center">
      <div className="absolute top-3 left-4 z-10 font-mono text-xs text-gray-400 uppercase tracking-wider flex items-center gap-2">
        <span className="h-2 w-2 rounded-full bg-blue-400 animate-pulse" />
        Live Mesh Topology • Spatial Event Core
      </div>

      <div className="absolute bottom-3 left-4 z-10 font-mono text-[10px] text-gray-500 flex gap-3">
        <span className="flex items-center gap-1">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> Healthy
        </span>
        <span className="flex items-center gap-1">
          <span className="h-1.5 w-1.5 rounded-full bg-red-400" /> Stress/Degraded
        </span>
        <span className="flex items-center gap-1">
          <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" /> Prevented
        </span>
        <span className="flex items-center gap-1">
          <span className="h-1.5 w-1.5 rounded-full bg-gray-400" /> Standby
        </span>
      </div>

      <Suspense fallback={<div className="text-xs text-gray-400 font-mono">Initializing 3D Pipeline...</div>}>
        <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
          <ambientLight intensity={0.6} />
          <pointLight position={[10, 10, 10]} intensity={1.5} />
          <pointLight position={[-10, -10, -10]} intensity={0.5} color="#3B82F6" />
          <BroadcastCore status={status} />
          <ServiceNodes
            status={status}
            activeWeights={activeWeights}
            predictiveState={predictiveState}
            riskScore={riskScore}
          />
          <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
        </Canvas>
      </Suspense>
    </div>
  );
};

