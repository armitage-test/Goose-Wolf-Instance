import { useState, useEffect, useCallback } from 'react';
import { fetchTasks, createTask, updateTask, deleteTask } from './api/tasks';
import TaskForm from './components/TaskForm';
import TaskList from './components/TaskList';
import TrendDashboard from './components/TrendDashboard';

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState(null);

  const loadTasks = useCallback(async () => {
    try {
      const data = await fetchTasks();
      setTasks(data);
    } catch (e) {
      setError(e.message);
    }
  }, []);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleCreate = async (title) => {
    try {
      const task = await createTask(title);
      setTasks((prev) => [task, ...prev]);
    } catch (e) {
      setError(e.message);
    }
  };

  const handleToggle = async (id, completed) => {
    try {
      const updated = await updateTask(id, { completed });
      setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)));
    } catch (e) {
      setError(e.message);
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteTask(id);
      setTasks((prev) => prev.filter((t) => t.id !== id));
    } catch (e) {
      setError(e.message);
    }
  };

  const handleEdit = async (id, title) => {
    try {
      const updated = await updateTask(id, { title });
      setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)));
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <main>
      <h1>Todo Manager</h1>
      {error && <p role="alert">{error}</p>}
      <TaskForm onSubmit={handleCreate} />
      <TaskList
        tasks={tasks}
        onToggle={handleToggle}
        onDelete={handleDelete}
        onEdit={handleEdit}
      />
      <hr />
      <TrendDashboard />
    </main>
  );
}
