import { useState } from 'react';
import { Brain, ChevronDown, FileText, Folder, Plus, Search, Send, Settings2, Sparkles } from 'lucide-react';

const tasks = [
  { id: 'research', title: 'Market research', meta: 'Today' },
  { id: 'interview', title: 'Interview preparation', meta: 'Yesterday' },
  { id: 'business', title: 'Business ideas', meta: 'Aug 28' },
];

export function App() {
  const [activeTask, setActiveTask] = useState('research');
  const [message, setMessage] = useState('');

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark"><Sparkles size={16} /></div><span>NEXUS</span></div>
        <button className="new-task"><Plus size={17} /> New task</button>
        <div className="section-label">WORKSPACES</div>
        <nav className="task-list">
          {tasks.map((task) => (
            <button key={task.id} className={`task-item ${activeTask === task.id ? 'active' : ''}`} onClick={() => setActiveTask(task.id)}>
              <div><span>{task.title}</span><small>{task.meta}</small></div>
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <button><Settings2 size={17} /> Settings</button>
        </div>
      </aside>

      <section className="workspace">
        <header className="workspace-header">
          <div><div className="eyebrow">ACTIVE TASK</div><h1>{tasks.find((t) => t.id === activeTask)?.title}</h1></div>
          <button className="model-pill"><span className="status-dot" /> Ollama <ChevronDown size={14} /></button>
        </header>

        <div className="workspace-content">
          <div className="task-objective">
            <div className="objective-icon"><Brain size={18} /></div>
            <div><span className="eyebrow">OBJECTIVE</span><p>Research the Pakistani convenience-store market and identify the biggest opportunities.</p></div>
          </div>

          <div className="plan-card">
            <div className="card-heading"><span>Plan</span><span className="badge">Ready</span></div>
            <div className="steps">
              <div className="step done"><span>✓</span><p>Understand the objective</p></div>
              <div className="step"><span>2</span><p>Research market and competitors</p></div>
              <div className="step"><span>3</span><p>Compare opportunities and assumptions</p></div>
              <div className="step"><span>4</span><p>Review findings and evidence</p></div>
            </div>
          </div>

          <div className="empty-result">
            <Sparkles size={20} />
            <h2>Ready to work</h2>
            <p>Ask NEXUS to continue this task or change its objective.</p>
          </div>
        </div>

        <div className="composer-wrap">
          <div className="composer">
            <textarea value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Tell NEXUS what to do next..." rows={1} />
            <button className="send" aria-label="Send"><Send size={17} /></button>
          </div>
          <span className="composer-hint">NEXUS can plan, research, analyze, create, and execute approved actions.</span>
        </div>
      </section>

      <aside className="context-panel">
        <div className="panel-header"><span>Context</span><button><Search size={16} /></button></div>
        <ContextSection icon={<Brain size={15} />} title="Memory"><p>Core memory</p><small>Relevant memories will appear here for the active task.</small></ContextSection>
        <ContextSection icon={<Search size={15} />} title="Sources"><p>No sources yet</p><small>Research sources will be collected here.</small></ContextSection>
        <ContextSection icon={<Folder size={15} />} title="Files"><p>No files</p><small>Task files and uploads will appear here.</small></ContextSection>
        <ContextSection icon={<FileText size={15} />} title="Artifacts"><p>No artifacts</p><small>Generated work will appear here.</small></ContextSection>
      </aside>
    </main>
  );
}

function ContextSection({ icon, title, children }: { icon: React.ReactNode; title: string; children: React.ReactNode }) {
  return <section className="context-section"><div className="context-title">{icon}<span>{title}</span></div><div className="context-body">{children}</div></section>;
}
