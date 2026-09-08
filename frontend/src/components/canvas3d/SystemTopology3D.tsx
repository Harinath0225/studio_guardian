import React, { useState, useEffect } from 'react';
import { SceneCanvas } from './SceneCanvas';
import { Fallback2DTopology } from './Fallback2DTopology';

interface SystemTopology3DProps {
  status: string;
  activeWeights: Record<string, number>;
  predictiveState?: string;
  riskScore?: number;
}

export const SystemTopology3D: React.FC<SystemTopology3DProps> = ({
  status,
  activeWeights,
  predictiveState = 'HEALTHY',
  riskScore = 0.18,
}) => {
  const [hasWebGLError, setHasWebGLError] = useState<boolean>(false);

  useEffect(() => {
    try {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      if (!gl) {
        setHasWebGLError(true);
      }
    } catch (e) {
      setHasWebGLError(true);
    }
  }, []);

  if (hasWebGLError) {
    return (
      <Fallback2DTopology
        status={status}
        activeWeights={activeWeights}
        riskScore={riskScore}
      />
    );
  }

  return (
    <div className="relative w-full h-full min-h-[220px]">
      <SceneCanvas
        status={status}
        activeWeights={activeWeights}
        predictiveState={predictiveState}
        riskScore={riskScore}
      />
    </div>
  );
};