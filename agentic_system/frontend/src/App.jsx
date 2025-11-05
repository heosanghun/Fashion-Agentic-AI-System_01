import { useState } from 'react';
import axios from 'axios';
import './App.css';
import ImageUpload from './components/ImageUpload';
import StatusBar from './components/StatusBar';
import ResultViewer from './components/ResultViewer';

function App() {
  const [image, setImage] = useState(null);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [sessionId] = useState(`session_${Date.now()}`);

  const handleImageChange = (file) => {
    setImage(file);
    setError(null);
  };

  const handleSubmit = async () => {
    if (!text && !image) {
      setError('이미지 또는 텍스트 입력이 필요합니다.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      if (text) {
        formData.append('text', text);
      }
      if (image) {
        formData.append('image', image);
      }
      formData.append('session_id', sessionId);

      console.log('요청 전송:', {
        text: text || '(없음)',
        image: image ? image.name : '(없음)',
        session_id: sessionId
      });

      const response = await axios.post('http://localhost:8000/api/v1/request', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30초 타임아웃
      });

      console.log('응답 수신:', response.data);
      setResult(response.data);
    } catch (err) {
      console.error('요청 오류:', err);
      if (err.response) {
        setError(`서버 오류: ${err.response.status} - ${err.response.data?.detail || err.response.data?.message || '알 수 없는 오류'}`);
      } else if (err.request) {
        setError('서버에 연결할 수 없습니다. API 서버가 실행 중인지 확인하세요.');
      } else {
        setError(`오류 발생: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setImage(null);
    setText('');
    setResult(null);
    setError(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Fashion Agentic AI System</h1>
        <p>패션 Agentic AI 가상 피팅 POC</p>
      </header>

      <div className="app-container">
        <div className="input-section">
          <div className="input-group">
            <label htmlFor="text-input">텍스트 입력:</label>
            <textarea
              id="text-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="예: 빨간색 원피스 추천해줘 또는 이 옷을 입혀줘"
              rows={4}
              disabled={loading}
            />
          </div>

          <div className="input-group">
            <label>이미지 업로드:</label>
            <ImageUpload
              onImageChange={handleImageChange}
              disabled={loading}
            />
            {image && (
              <div className="image-preview">
                <p>선택된 이미지: {image.name}</p>
                <img
                  src={URL.createObjectURL(image)}
                  alt="미리보기"
                  style={{ maxWidth: '200px', maxHeight: '200px', marginTop: '10px' }}
                />
              </div>
            )}
          </div>

          <div className="button-group">
            <button
              onClick={handleSubmit}
              disabled={loading || (!text && !image)}
              className="submit-button"
            >
              {loading ? '처리 중...' : '요청 전송'}
            </button>
            <button
              onClick={handleClear}
              disabled={loading}
              className="clear-button"
            >
              초기화
            </button>
          </div>
        </div>

        <div className="status-section">
          <StatusBar loading={loading} status={result?.status} />
        </div>

        {error && (
          <div className="error-section">
            <h3>오류 발생</h3>
            <p>{error}</p>
          </div>
        )}

        <div className="result-section">
          <ResultViewer result={result} image={image} />
        </div>
      </div>

      <footer className="app-footer">
        <div className="footer-logo">
          <img src="/simsreality-logo.png" alt="SIMSREALITY" className="logo-image" />
        </div>
        <div className="footer-divider"></div>
        <p>Fashion Agentic AI System - PoC 단계</p>
      </footer>
    </div>
  );
}

export default App;
