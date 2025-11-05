import React from 'react'
import './StatusBar.css'

function StatusBar({ progress, loading }) {
  if (!progress && !loading) {
    return null
  }

  return (
    <div className="status-bar">
      <div className="status-content">
        {loading && <div className="spinner"></div>}
        <span>{progress || '처리 중...'}</span>
      </div>
      {loading && <div className="progress-bar">
        <div className="progress-fill"></div>
      </div>}
    </div>
  )
}

export default StatusBar

