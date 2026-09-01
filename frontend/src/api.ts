const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000';

export type Workspace = {
  id: string;
  objective: string;
  task_type: string;
  status: string;
  verification_status?: string;
};

export async function startTask(objective: string, taskType = 'general') {
  const response = await fetch(`${API_BASE}/api/tasks/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ objective, task_type: taskType }),
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function runTask(workspaceId: string, message: string, approved = false) {
  const response = await fetch(`${API_BASE}/api/tasks/${workspaceId}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, approved }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail ?? 'Task execution failed');
  return data;
}

export async function getTask(workspaceId: string): Promise<Workspace> {
  const response = await fetch(`${API_BASE}/api/tasks/${workspaceId}`);
  if (!response.ok) throw new Error('Workspace not found');
  return response.json();
}

export async function listTasks(): Promise<Workspace[]> {
  const response = await fetch(`${API_BASE}/api/tasks`);
  if (!response.ok) throw new Error('Could not load workspaces');
  const data = await response.json();
  return data.workspaces ?? data.tasks ?? data;
}
