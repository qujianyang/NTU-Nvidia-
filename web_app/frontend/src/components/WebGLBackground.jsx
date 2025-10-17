import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Float, Stars, MeshDistortMaterial } from '@react-three/drei';
import * as THREE from 'three';

// Animated particle field with NVIDIA green glow
function ParticleField() {
  const points = useRef();
  const { viewport } = useThree();

  // Generate particle positions
  const particles = useMemo(() => {
    const temp = [];
    for (let i = 0; i < 2000; i++) {
      const x = (Math.random() - 0.5) * viewport.width * 2;
      const y = (Math.random() - 0.5) * viewport.height * 2;
      const z = (Math.random() - 0.5) * 10;
      temp.push(x, y, z);
    }
    return new Float32Array(temp);
  }, [viewport]);

  // Animate particles
  useFrame((state) => {
    if (points.current) {
      points.current.rotation.y = state.clock.elapsedTime * 0.02;
      points.current.rotation.x = state.clock.elapsedTime * 0.01;

      // Pulse effect
      const scale = 1 + Math.sin(state.clock.elapsedTime) * 0.1;
      points.current.scale.set(scale, scale, scale);
    }
  });

  return (
    <points ref={points}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particles.length / 3}
          array={particles}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.015}
        color="#76b900"
        transparent
        opacity={0.6}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

// Floating geometric shapes with distortion
function FloatingMesh({ position, scale = 1 }) {
  const mesh = useRef();

  useFrame((state) => {
    if (mesh.current) {
      mesh.current.rotation.x = state.clock.elapsedTime * 0.2;
      mesh.current.rotation.y = state.clock.elapsedTime * 0.3;
      mesh.current.position.y = position[1] + Math.sin(state.clock.elapsedTime) * 0.3;
    }
  });

  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
      <mesh ref={mesh} position={position} scale={scale}>
        <icosahedronGeometry args={[1, 4]} />
        <MeshDistortMaterial
          color="#76b900"
          attach="material"
          distort={0.3}
          speed={2}
          roughness={0.1}
          metalness={0.8}
          transparent
          opacity={0.2}
        />
      </mesh>
    </Float>
  );
}

// Ambient light rays
function LightRays() {
  const mesh = useRef();

  useFrame((state) => {
    if (mesh.current) {
      mesh.current.rotation.z = state.clock.elapsedTime * 0.1;
    }
  });

  return (
    <mesh ref={mesh} position={[0, 0, -5]}>
      <planeGeometry args={[30, 30]} />
      <shaderMaterial
        transparent
        uniforms={{
          time: { value: 0 },
        }}
        vertexShader={`
          varying vec2 vUv;
          void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `}
        fragmentShader={`
          uniform float time;
          varying vec2 vUv;

          void main() {
            vec2 center = vec2(0.5, 0.5);
            float dist = distance(vUv, center);

            float rays = sin(atan(vUv.y - center.y, vUv.x - center.x) * 10.0) * 0.5 + 0.5;
            rays *= 1.0 - dist;

            vec3 color = vec3(0.463, 0.725, 0.0); // NVIDIA green
            float alpha = rays * 0.1;

            gl_FragColor = vec4(color, alpha);
          }
        `}
        blending={THREE.AdditiveBlending}
      />
    </mesh>
  );
}

// Main WebGL Background Component
const WebGLBackground = ({ intensity = 1 }) => {
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      zIndex: -1,
      background: `linear-gradient(180deg,
        rgba(26, 26, 26, 1) 0%,
        rgba(13, 13, 13, 1) 50%,
        rgba(0, 0, 0, 1) 100%)`,
    }}>
      <Canvas
        camera={{ position: [0, 0, 5], fov: 75 }}
        style={{ position: 'absolute', top: 0, left: 0 }}
      >
        <fog attach="fog" args={['#000000', 5, 15]} />
        <ambientLight intensity={0.2} />
        <directionalLight position={[10, 10, 5]} intensity={0.5} color="#76b900" />

        {/* Particle effects */}
        <ParticleField />

        {/* Floating geometric shapes */}
        <FloatingMesh position={[-3, 2, -2]} scale={0.5} />
        <FloatingMesh position={[3, -1, -3]} scale={0.7} />
        <FloatingMesh position={[0, 0, -4]} scale={0.3} />

        {/* Light rays effect */}
        <LightRays />

        {/* Star field for depth */}
        <Stars
          radius={100}
          depth={50}
          count={5000}
          factor={4}
          saturation={0}
          fade
          speed={1}
        />
      </Canvas>

      {/* Gradient overlay for depth */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        background: `radial-gradient(circle at 50% 50%,
          transparent 0%,
          rgba(0, 0, 0, 0.4) 100%)`,
        pointerEvents: 'none',
      }} />
    </div>
  );
};

export default WebGLBackground;