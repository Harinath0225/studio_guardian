import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface BroadcastCoreProps {
  status: string;
}

export const BroadcastCore: React.FC<BroadcastCoreProps> = ({ status }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const wireframeRef = useRef<THREE.Mesh>(null);

  const isNominal = status === 'HEALTHY' || status === 'RESOLVED';
  const isMitigating = status === 'REMEDIATING' || status === 'VERIFYING' || status === 'WAITING_HUMAN_APPROVAL';

  // Visual state: Emerald when nominal/resolved, Amber when remediating/verifying, Red during active incident/investigation
  const coreColor = isNominal ? '#10B981' : isMitigating ? '#F59E0B' : '#EF4444';

  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.4;
      meshRef.current.rotation.x += delta * 0.15;
    }
    if (wireframeRef.current) {
      wireframeRef.current.rotation.y -= delta * 0.25;
    }
  });

  return (
    <group>
      {/* Central Media Globe */}
      <mesh ref={meshRef}>
        <sphereGeometry args={[1.2, 32, 32]} />
        <meshStandardMaterial
          color={coreColor}
          emissive={coreColor}
          emissiveIntensity={!isNominal ? 0.8 : 0.4}
          roughness={0.2}
          metalness={0.8}
        />
      </mesh>

      {/* Outer Hologram Wireframe Shell */}
      <mesh ref={wireframeRef}>
        <sphereGeometry args={[1.5, 16, 16]} />
        <meshBasicMaterial
          color={coreColor}
          wireframe
          transparent
          opacity={!isNominal ? 0.5 : 0.25}
        />
      </mesh>
    </group>
  );
};
