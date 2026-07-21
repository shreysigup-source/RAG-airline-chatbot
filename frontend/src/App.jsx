import React, { useState, useEffect, useRef } from 'react';
import { sendChatMessage, uploadPDF, uploadImage } from './services/api';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { id: '1', sender: 'ai', text: 'Hello! I am your AeroSupport assistant. How can I help you today?', timestamp: '' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [attachedFile, setAttachedFile] = useState(null);
  const [attachedFileType, setAttachedFileType] = useState(null); // 'pdf' | 'image'
  const [errorMsg, setErrorMsg] = useState(null);

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto Scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    if (ext === 'pdf') {
      setAttachedFile(file);
      setAttachedFileType('pdf');
      setErrorMsg(null);
    } else if (['jpg', 'jpeg', 'png', 'webp'].includes(ext)) {
      setAttachedFile(file);
      setAttachedFileType('image');
      setErrorMsg(null);
    } else {
      setErrorMsg('Unsupported file type. Please upload a PDF or an Image.');
      setAttachedFile(null);
      setAttachedFileType(null);
    }
  };

  const removeAttachment = () => {
    setAttachedFile(null);
    setAttachedFileType(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSend = async () => {
    const query = inputValue.trim();
    if (!query && !attachedFile) return;

    setLoading(true);
    setErrorMsg(null);

    let activeContext = '';

    try {
      // 1. If file is attached, upload it first
      if (attachedFile) {
        addMessage('system', `Uploading file: ${attachedFile.name}...`);
        
        if (attachedFileType === 'pdf') {
          const res = await uploadPDF(attachedFile);
          addMessage('system', `PDF content extracted successfully.`);
          activeContext = res.extracted_text || '';
        } else if (attachedFileType === 'image') {
          const res = await uploadImage(attachedFile);
          addMessage('ai', `Image Processed (Mock Result):\n• Status: ${res.result?.status}\n• Message: ${res.result?.message}`);
          removeAttachment();
          setLoading(false);
          return;
        }
      }

      // Add user message to UI
      const userDisplayMsg = query || `Attached file: ${attachedFile?.name}`;
      addMessage('user', userDisplayMsg);
      setInputValue(''); // Clear input box

      // Formulate query with context if available
      let finalQuery = query;
      if (activeContext) {
        finalQuery = `Context from uploaded PDF:\n\"\"\"\n${activeContext}\n\"\"\"\n\nUser Question: ${query}`;
      }

      // 2. Call chat API
      const res = await sendChatMessage(finalQuery);
      if (res.status === 'success') {
        addMessage('ai', res.response, res.sources);
      } else {
        setErrorMsg(res.response || 'An error occurred.');
      }

      removeAttachment();
    } catch (err) {
      console.error(err);
      const msg = err.response?.data?.message || err.message || 'Connection to server failed.';
      setErrorMsg(`Error: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  const addMessage = (sender, text, sources = null) => {
    setMessages(prev => [...prev, {
      id: Date.now() + Math.random().toString(),
      sender,
      text,
      sources,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }]);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      {/* Scrollable messages history */}
      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message-row ${msg.sender}`}>
            <div className="message-bubble">
              {msg.text.split('\n').map((line, idx) => (
                <div key={idx}>{line}</div>
              ))}
              
              {/* Citations/sources list */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="sources-list">
                  {msg.sources.map((src, sIdx) => {
                    const name = src.source || src.tool_name || 'Knowledge Base';
                    return (
                      <span key={sIdx} className="source-pill">
                        📎 {name.replace('Service Tool: ', '').replace('Knowledge Base Document', 'FAQ')}
                      </span>
                    );
                  })}
                </div>
              )}
            </div>
            {msg.timestamp && <span className="message-time">{msg.timestamp}</span>}
          </div>
        ))}
        {loading && (
          <div className="message-row system">
            <div className="loading-dots">Thinking...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Footer input workspace */}
      <div className="chat-footer">
        {errorMsg && <div className="error-message">⚠️ {errorMsg}</div>}
        
        {attachedFile && (
          <div className="attachment-bar">
            <span>📎 {attachedFile.name}</span>
            <button onClick={removeAttachment}>×</button>
          </div>
        )}

        <div className="input-row">
          {/* File selector input */}
          <input 
            type="file" 
            ref={fileInputRef} 
            style={{ display: 'none' }} 
            accept=".pdf, image/*" 
            onChange={handleFileChange}
          />
          <button 
            className="attach-button"
            onClick={() => fileInputRef.current?.click()}
            disabled={loading}
            title="Attach PDF or Image"
          >
            📎
          </button>

          <textarea
            className="text-input"
            placeholder={attachedFile ? "Ask a question about this file..." : "Type a message..."}
            rows="1"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />

          <button 
            className="send-button"
            onClick={handleSend}
            disabled={loading || (!inputValue.trim() && !attachedFile)}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
