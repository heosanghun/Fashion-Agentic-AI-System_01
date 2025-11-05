import React, { useRef, useEffect } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera } from '@react-three/drei'
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader'
import * as THREE from 'three'
import './ModelViewer.css'

function Model({ meshPath }) {
  const meshRef = useRef()

  useEffect(() => {
    if (!meshPath) return

    const loader = new OBJLoader()
    loader.load(
      meshPath,
      (object) => {
        // 메시 스케일 및 위치 조정
        object.traverse((child) => {
          if (child.isMesh) {
            child.material = new THREE.MeshStandardMaterial({
              color: 0x888888,
              metalness: 0.3,
              roughness: 0.7,
            })
          }
        })

        // 바운딩 박스 계산
        const box = new THREE.Box3().setFromObject(object)
        const center = box.getCenter(new THREE.Vector3())
        const size = box.getSize(new THREE.Vector3())
        const maxDim = Math.max(size.x, size.y, size.z)
        const scale = 2 / maxDim

        object.scale.multiplyScalar(scale)
        object.position.sub(center.multiplyScalar(scale))

        if (meshRef.current) {
          meshRef.current.clear()
          meshRef.current.add(object)
        }
      },
      undefined,
      (error) => {
        console.error('3D 모델 로딩 오류:', error)
      }
    )
  }, [meshPath])

  return <group ref={meshRef} />
}

function ModelViewer({ meshPath }) {
  if (!meshPath) {
    return (
      <div className="model-viewer-placeholder">
        <p>3D 모델을 준비 중입니다...</p>
      </div>
    )
  }

  return (
    <div className="model-viewer">
      <Canvas>
        <PerspectiveCamera makeDefault position={[0, 0, 5]} />
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <pointLight position={[-10, -10, -5]} intensity={0.5} />
        <Model meshPath={meshPath} />
        <OrbitControls enableDamping dampingFactor={0.05} />
      </Canvas>
    </div>
  )
}

export default ModelViewer

