import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface ServiceNodesProps {
  status: string;
  activeWeights: Record<string, number>;
  predictiveState?: string;
  riskScore?: number;
}

export const ServiceNodes: React.FC<ServiceNodesProps> = ({
  status,
  activeWeights,
  predictiveState,
  riskScore = 0,
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const pulseRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);

  // Australia (Sydney), Singapore, US-West (Standby)
  const isNominal = status === 'HEALTHY' || status === 'RESOLVED' || predictiveState === 'HEALTHY';
  const isSurge = predictiveState === 'IMMINENT_RISK' || predictiveState === 'HIGH_RISK' || riskScore >= 0.75;
  const isWatch = predictiveState === 'WATCH' || predictiveState === 'ELEVATED_RISK';
  const isPrevented = predictiveState === 'PREVENTED';

  const isSydneyDegraded = !isNominal && (activeWeights['transcoder-us-01'] || 0) < 0.5;

  let sydneyColor = '#10B981'; // Default Emerald
  if (isSydneyDegraded) {
    sydneyColor = '#EF4444'; // Red failure
  } else if (isSurge) {
    sydneyColor = '#F43F5E'; // Rose/Red imminent stress
  } else if (isWatch) {
    sydneyColor = '#F59E0B'; // Amber warning
  } else if (isPrevented) {
    sydneyColor = '#06B6D4'; // Cyan/Emerald healthy scaled
  }

  const singaporeColor = isNominal ? '#10B981' : isSurge ? '#F59E0B' : '#10B981';
  const usStandbyColor = (activeWeights['transcoder-us-01'] || 0) > 0.5 ? '#10B981' : '#64748B';

  useFrame((state, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.15;
    }

    const t = state.clock.getElapsedTime();
    if (pulseRef.current) {
      // Rapid pulsation during load surge / imminent risk
      const speed = isSurge ? 8.0 : isWatch ? 3.5 : 1.5;
      const s = 1.0 + Math.sin(t * speed) * (isSurge ? 0.35 : 0.15);
      pulseRef.current.scale.set(s, s, s);
    }

    if (ringRef.current) {
      ringRef.current.rotation.z += delta * 0.5;
      const ringScale = isPrevented ? 1.5 + Math.sin(t * 2) * 0.1 : isSurge ? 1.3 : 1.0;
      ringRef.current.scale.set(ringScale, ringScale, ringScale);
    }
  });

  return (
    <group ref={groupRef}>
      {/* Sydney Transcoder Node */}
      <group position={[2.5, 0.4, 0]}>
        <mesh ref={pulseRef}>
          <sphereGeometry args={[0.26, 24, 24]} />
          <meshStandardMaterial
            color={sydneyColor}
            emissive={sydneyColor}
            emissiveIntensity={isSurge ? 1.2 : 0.6}
            roughness={0.2}
            metalness={0.8}
          />
        </mesh>

        {/* Dynamic Capacity Ring / Stress Ring */}
        {(isSurge || isPrevented) && (
          <mesh ref={ringRef} rotation={[Math.PI / 2, 0, 0]}>
            <ringGeometry args={[0.35, 0.42, 32]} />
            <meshBasicMaterial
              color={isPrevented ? '#06B6D4' : '#EF4444'}
              side={THREE.DoubleSide}
              transparent
              opacity={0.8}
            />
          </mesh>
        )}
      </group>

      {/* Singapore Node */}
      <group position={[-2.2, 0.8, 1.2]}>
        <mesh>
          <sphereGeometry args={[0.2, 16, 16]} />
          <meshStandardMaterial
            color={singaporeColor}
            emissive={singaporeColor}
            emissiveIntensity={0.4}
          />
        </mesh>
      </group>

      {/* US Warm Standby Cluster */}
      <group position={[0.5, -2.0, 1.5]}>
        <mesh>
          <sphereGeometry args={[0.28, 16, 16]} />
          <meshStandardMaterial
            color={usStandbyColor}
            emissive={usStandbyColor}
            emissiveIntensity={0.5}
          />
        </mesh>
      </group>
    </group>
  );
};
