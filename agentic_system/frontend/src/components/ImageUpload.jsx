import React from 'react'
import './ImageUpload.css'

function ImageUpload({ onImageChange, disabled }) {
  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      if (file.type.startsWith('image/')) {
        onImageChange(file)
      } else {
        alert('이미지 파일만 업로드 가능합니다.')
      }
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    if (disabled) return
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      onImageChange(file)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  const handleClick = () => {
    if (!disabled) {
      document.getElementById('image-input').click()
    }
  }

  return (
    <div className="image-upload">
      <div
        className={`upload-area ${disabled ? 'disabled' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={handleClick}
      >
        <div className="upload-icon">
          ✨
        </div>
        <p>
          이미지를 드래그하거나 클릭하여 업로드
        </p>
        <p className="upload-hint">
          PNG, JPG, JPEG 지원
        </p>
      </div>
      <input
        id="image-input"
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        disabled={disabled}
        style={{ display: 'none' }}
      />
    </div>
  )
}

export default ImageUpload
