import React, { Suspense, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { BroadcastCore } from './BroadcastCore';
import { ServiceNodes, TopologyNodeInfo } from './ServiceNodes';

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
  const [hoveredNode, setHoveredNode] = useState<TopologyNodeInfo | null>(null);

  return (
    <div className="relative h-64 sm:h-72 w-full rounded-xl overflow-hidden glass-panel border border-white/10 flex items-center justify-center">
      {/* Topology Header */}
      <div className="absolute top-3 left-4 z-10 font-mono text-xs text-slate-300 uppercase tracking-wider flex items-center gap-2">
        <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
        Live Mesh Topology
      </div>

      {/* Node Inspection Tooltip Overlay */}
      {hoveredNode ? (
        <div className="absolute top-3 right-3 z-20 glass-panel p-2.5 rounded-lg border border-cyan-500/40 font-mono text-xs max-w-[210px] space-y-1 shadow-xl backdrop-blur-xl transition-all">
          <div className="flex items-center justify-between gap-2">
            <span className="font-bold text-slate-100 truncate text-[11px]">{hoveredNode.id}</span>
            <span
              className="text-[9px] px-1.5 py-0.2 rounded font-bold"
              style={{ backgroundColor: `${hoveredNode.statusColor}25`, color: hoveredNode.statusColor }}
            >
              {hoveredNode.health}
            </span>
          </div>
          <div className="text-[10px] text-slate-400 truncate">{hoveredNode.label}</div>
          <div className="text-[10px] text-slate-300 font-sans">{hoveredNode.region}</div>
          <div className="flex justify-between items-center text-[10px] pt-1 border-t border-white/10 text-slate-400">
            <span>Route Weight:</span>
            <span className="text-cyan-300 font-bold">{hoveredNode.trafficWeight}</span>
          </div>
        </div>
      ) : (
        <div className="absolute top-3 right-3 z-10 font-mono text-[10px] text-slate-400 px-2 py-1 rounded bg-black/40 border border-white/5 flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 rounded-full bg-cyan-400/60 animate-pulse" />
          <span>Hover node to inspect</span>
        </div>
      )}

      {/* Topology Legend */}
      <div className="absolute bottom-3 left-4 z-10 font-mono text-[10px] text-slate-400 flex flex-wrap gap-3">
        <span className="flex items-center gap-1">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> Nominal
        </span>
        <span className="flex items-center gap-1">
          <span className="h-1.5 w-1.5 rounded-full bg-red-400" /> Stress/Degraded
        </span>
        <span className="flex items-center gap-1">
          <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" /> Mitigated
        </span>
        <span className="flex items-center gap-1">
          <span className="h-1.5 w-1.5 rounded-full bg-slate-400" /> Standby
        </span>
      </div>

      <Suspense fallback={<div className="text-xs text-slate-400 font-mono">Initializing 3D Pipeline...</div>}>
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
            onHoverNode={setHoveredNode}
          />
          <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
        </Canvas>
      </Suspense>
    </div>
  );
};

