import { useState } from 'react';

const suggestions = ['Summarize this repo', 'Analyze a CSV file', 'Write a Python script', 'Explain a math problem'];

export default function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I can help with research, coding, file work, data analysis, and math. Ask me anything.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async (text = input) => {
    if (!text.trim()) return;
    const userMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply || 'No reply returned.' }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'The agent is unavailable right now. Please check your server and API key.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <div className="glass-panel hero">
        <div className="status-row">
          <span className="status-pill">● Online</span>
          <span className="status-pill muted">OpenAI + LangChain</span>
        </div>
        <h1>LangChain AI Agent</h1>
        <p>Research, code, analyze files, and solve problems with a polished conversational interface.</p>
        <div className="suggestions">
          {suggestions.map(item => (
            <button key={item} onClick={() => sendMessage(item)}>{item}</button>
          ))}
        </div>
      </div>

      <div className="glass-panel chat-panel">
        <div className="message-list">
          {messages.map((m, idx) => (
            <div key={idx} className={`bubble ${m.role}`}>{m.content}</div>
          ))}
          {loading && <div className="bubble assistant typing">Thinking<span /></div>}
        </div>

        <div className="composer">
          <button className="icon-btn">🎙️</button>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask for analysis, code, research, or planning..."
          />
          <button className="send-btn" onClick={() => sendMessage()}>Send</button>
        </div>
      </div>
    </div>
  );
}
