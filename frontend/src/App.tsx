import { useState } from 'react';
import { Brain, ChevronDown, FileText, Folder, Plus, Search, Send, Settings2, Sparkles, LoaderCircle } from 'lucide-react';
import { runTask, startTask, type Workspace } from './api';

const demoTasks = [
  { id: 'research', title: 'Market research', meta: 'Today' },
  { id: 'interview', title: 'Interview preparation', meta: 'Yesterday' },
  { id: 'business', title: 'Business ideas', meta: 'Aug 28' },
];

export function App() {
  const [activeTask, setActiveTask] = useState('research');
  const [objective, setObjective] = useState('');
  const [message, setMessage] = useState('');
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [response, setResponse] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function createAndRun() {
    const text = message.trim() || objective.trim();
    if (!text || busy) return;
    setBusy(true); setError('');
    try {
      const created = workspace ?? (await startTask(text)).workspace;
      setWorkspace(created);
      if (!workspace) setObjective(created.objective);
      const result = await runTask(created.id, text);
      setWorkspace(result.workspace);
      setResponse(result.response);
      setMessage('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally { setBusy(false); }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark"><Sparkles size={16} /></div><span>NEXUS</span></div>
        <button className="new-task" onClick={() => { setWorkspace(null); setResponse(''); setObjective(''); setMessage(''); setError(''); }}><Plus size={17} /> New task</button>
        <div className="section-label">WORKSPACES</div>
        <nav className="task-list">{demoTasks.map((task) => <button key={task.id} className={`task-item ${activeTask === task.id ? 'active' : ''}`} onClick={() => setActiveTask(task.id)}><div><span>{task.title}</span><small>{task.meta}</small></div></button>)}</nav>
        <div className="sidebar-bottom"><button><Settings2 size={17} /> Settings</button></div>
      </aside>

      <section className="workspace">
        <header className="workspace-header">
          <div><div className="eyebrow">ACTIVE TASK</div><h1>{workspace?.objective || demoTasks.find((t) => t.id === activeTask)?.title}</h1></div>
          <button className="model-pill"><span className="status-dot" /> Ollama <ChevronDown size={14} /></button>
        </header>

        <div className="workspace-content">
          {objective && <div className="task-objective"><div className="objective-icon"><Brain size={18} /></div><div><span className="eyebrow">OBJECTIVE</span><p>{objective}</p></div></div>}
          {workspace && <div className="plan-card"><div className="card-heading"><span>Execution</span><span className="badge">{workspace.status}</span></div><div className="steps"><div className="step done"><span>✓</span><p>Workspace created</p></div><div className={`step ${busy ? 'running' : response ? 'done' : ''}`}><span>{busy ? <LoaderCircle size={12} className="spin" /> : response ? '✓' : '2'}</span><p>{busy ? 'Running local model...' : response ? 'Execution completed' : 'Ready to execute'}</p></div><div className="step"><span>3</span><p>{workspace.verification_status === 'unverified' ? 'Result requires independent verification' : 'Review result'}</p></div></div></div>}
          {response ? <article className="result-card"><div className="card-heading"><span>Result</span><span className="badge">{workspace?.verification_status ?? 'Unverified'}</span></div><p>{response}</p></article> : !busy && !workspace && <div className="empty-result"><Sparkles size={20} /><h2>What should NEXUS work on?</h2><p>Give it an objective. NEXUS will create a workspace and execute it locally.</p></div>}
          {error && <div className="error-card">{error}</div>}
        </div>

        <div className="composer-wrap"><div className="composer"><textarea value={message} onChange={(e) => setMessage(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); createAndRun(); } }} placeholder="Tell NEXUS what to do..." rows={1} /><button className="send" onClick={createAndRun} disabled={busy} aria-label="Send">{busy ? <LoaderCircle size={17} className="spin" /> : <Send size={17} />}</button></div><span className="composer-hint">Enter to run · Shift + Enter for a new line</span></div>
      </section>

      <aside className="context-panel"><div className="panel-header"><span>Context</span><button><Search size={16} /></button></div><ContextSection icon={<Brain size={15} />} title="Memory"><p>Task memory</p><small>Relevant memory for this workspace will appear here.</small></ContextSection><ContextSection icon={<Search size={15} />} title="Sources"><p>No sources yet</p><small>Research sources will be collected here.</small></ContextSection><ContextSection icon={<Folder size={15} />} title="Files"><p>No files</p><small>Task files and uploads will appear here.</small></ContextSection><ContextSection icon={<FileText size={15} />} title="Artifacts"><p>No artifacts</p><small>Generated work will appear here.</small></ContextSection></aside>
    </main>
  );
}

function ContextSection({ icon, title, children }: { icon: React.ReactNode; title: string; children: React.ReactNode }) { return <section className="context-section"><div className="context-title">{icon}<span>{title}</span></div><div className="context-body">{children}</div></section>; }
