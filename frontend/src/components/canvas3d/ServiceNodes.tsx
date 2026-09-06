import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface ServiceNodesProps {
  status: string;
  activeWeights: Record<string, number>;
}

export const ServiceNodes: React.FC<ServiceNodesProps> = ({ status, activeWeights }) => {
  const groupRef = useRef<THREE.Group>(null);

  // Australia (Sydney), Singapore, US-West (Standby)
  const isNominal = status === 'HEALTHY' || status === 'RESOLVED';
  const isSydneyDegraded = !isNominal && (activeWeights['transcoder-us-01'] || 0) < 0.5;
  const sydneyColor = isSydneyDegraded ? '#EF4444' : '#10B981';
  const singaporeColor = isNominal ? '#10B981' : '#F59E0B';
  const usStandbyColor = (activeWeights['transcoder-us-01'] || 0) > 0.5 ? '#10B981' : '#64748B';

  useFrame((_, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.15;
    }
  });

  return (
    <group ref={groupRef}>
      {/* Sydney Transcoder Node */}
      <group position={[2.5, 0.4, 0]}>
        <mesh>
          <sphereGeometry args={[0.25, 16, 16]} />
          <meshStandardMaterial color={sydneyColor} emissive={sydneyColor} emissiveIntensity={0.6} />
        </mesh>
      </group>

      {/* Singapore Node */}
      <group position={[-2.2, 0.8, 1.2]}>
        <mesh>
          <sphereGeometry args={[0.2, 16, 16]} />
          <meshStandardMaterial color={singaporeColor} emissive={singaporeColor} emissiveIntensity={0.4} />
        </mesh>
      </group>

      {/* US Warm Standby Cluster */}
      <group position={[0.5, -2.0, 1.5]}>
        <mesh>
          <sphereGeometry args={[0.28, 16, 16]} />
          <meshStandardMaterial color={usStandbyColor} emissive={usStandbyColor} emissiveIntensity={0.5} />
        </mesh>
      </group>
    </group>
  );
};
