import { useEffect, useState } from 'react';
import { Brain, ChevronDown, FileText, Folder, LoaderCircle, Plus, Search, Send, Settings2, Sparkles } from 'lucide-react';
import { getTask, listTasks, runTask, startTask, type Workspace } from './api';

export function App() {
  const [tasks, setTasks] = useState<Workspace[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [objective, setObjective] = useState('');
  const [message, setMessage] = useState('');
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [response, setResponse] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    listTasks().then((items) => {
      setTasks(items);
      if (items[0]) selectTask(items[0].id);
    }).catch((err) => setError(err instanceof Error ? err.message : 'Could not load workspaces'));
  }, []);

  async function selectTask(id: string) {
    setError('');
    try {
      const item = await getTask(id);
      setActiveId(id);
      setWorkspace(item);
      setObjective(item.objective);
      setResponse('');
    } catch (err) { setError(err instanceof Error ? err.message : 'Could not load workspace'); }
  }

  function newTask() {
    setActiveId(null); setWorkspace(null); setObjective(''); setMessage(''); setResponse(''); setError('');
  }

  async function createAndRun() {
    const text = message.trim() || objective.trim();
    if (!text || busy) return;
    setBusy(true); setError('');
    try {
      const created = workspace ?? (await startTask(text)).workspace;
      setWorkspace(created); setActiveId(created.id); setObjective(created.objective);
      const result = await runTask(created.id, message.trim() || text);
      setWorkspace(result.workspace); setResponse(result.response); setMessage('');
      setTasks((current) => [result.workspace, ...current.filter((item) => item.id !== result.workspace.id)]);
    } catch (err) { setError(err instanceof Error ? err.message : 'Something went wrong'); }
    finally { setBusy(false); }
  }

  const title = workspace?.objective || 'New task';

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark"><Sparkles size={16} /></div><span>NEXUS</span></div>
        <button className="new-task" onClick={newTask}><Plus size={17} /> New task</button>
        <div className="section-label">WORKSPACES</div>
        <nav className="task-list">
          {tasks.length === 0 && <div className="sidebar-empty">No workspaces yet.</div>}
          {tasks.map((task) => <button key={task.id} className={`task-item ${activeId === task.id ? 'active' : ''}`} onClick={() => selectTask(task.id)}><div><span>{task.objective}</span><small>{task.status}</small></div></button>)}
        </nav>
        <div className="sidebar-bottom"><button><Settings2 size={17} /> Settings</button></div>
      </aside>

      <section className="workspace">
        <header className="workspace-header">
          <div><div className="eyebrow">ACTIVE TASK</div><h1>{title}</h1></div>
          <button className="model-pill"><span className="status-dot" /> Ollama <ChevronDown size={14} /></button>
        </header>

        <div className="workspace-content">
          {workspace && <div className="task-objective"><div className="objective-icon"><Brain size={18} /></div><div><span className="eyebrow">OBJECTIVE</span><p>{objective}</p></div></div>}
          {workspace && <div className="plan-card"><div className="card-heading"><span>Execution</span><span className="badge">{workspace.verification_status === 'unverified' ? 'Unverified' : workspace.status}</span></div><div className="steps">
            <Step done label="Workspace created" />
            <Step done={workspace.status === 'completed'} running={busy} label={busy ? 'Running local model...' : workspace.status === 'completed' ? 'Execution completed' : 'Ready to execute'} />
            <Step done={workspace.verification_status === 'verified'} label={workspace.verification_status === 'unverified' ? 'Result requires independent verification' : 'Review result'} />
          </div></div>}
          {response && <article className="result-card"><div className="card-heading"><span>Result</span><span className="badge">{workspace?.verification_status ?? 'Unverified'}</span></div><p>{response}</p></article>}
          {!busy && !workspace && <div className="empty-result"><Sparkles size={20} /><h2>What should NEXUS work on?</h2><p>Give it an objective. NEXUS will create a persistent workspace and execute it locally.</p></div>}
          {error && <div className="error-card">{error}</div>}
        </div>

        <div className="composer-wrap"><div className="composer"><textarea value={message} onChange={(e) => setMessage(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); createAndRun(); } }} placeholder="Tell NEXUS what to do..." rows={1} /><button className="send" onClick={createAndRun} disabled={busy} aria-label="Send">{busy ? <LoaderCircle size={17} className="spin" /> : <Send size={17} />}</button></div><span className="composer-hint">Enter to run · Shift + Enter for a new line</span></div>
      </section>

      <aside className="context-panel"><div className="panel-header"><span>Context</span><button><Search size={16} /></button></div><ContextSection icon={<Brain size={15} />} title="Memory"><p>Task memory</p><small>Relevant memory for this workspace will appear here.</small></ContextSection><ContextSection icon={<Search size={15} />} title="Sources"><p>No sources yet</p><small>Research sources will be collected here.</small></ContextSection><ContextSection icon={<Folder size={15} />} title="Files"><p>No files</p><small>Task files and uploads will appear here.</small></ContextSection><ContextSection icon={<FileText size={15} />} title="Artifacts"><p>No artifacts</p><small>Generated work will appear here.</small></ContextSection></aside>
    </main>
  );
}

function Step({ label, done = false, running = false }: { label: string; done?: boolean; running?: boolean }) {
  return <div className={`step ${done ? 'done' : ''}`}><span>{running ? <LoaderCircle size={12} className="spin" /> : done ? '✓' : '·'}</span><p>{label}</p></div>;
}

function ContextSection({ icon, title, children }: { icon: React.ReactNode; title: string; children: React.ReactNode }) {
  return <section className="context-section"><div className="context-title">{icon}<span>{title}</span></div><div className="context-body">{children}</div></section>;
}
