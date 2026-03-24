import { useState } from 'react';

export default function TaskItem({ task, onToggle, onDelete, onEdit }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(task.title);

  const handleEditSubmit = (e) => {
    e.preventDefault();
    const trimmed = draft.trim();
    if (!trimmed || trimmed === task.title) {
      setEditing(false);
      setDraft(task.title);
      return;
    }
    onEdit(task.id, trimmed);
    setEditing(false);
  };

  const handleEditCancel = () => {
    setEditing(false);
    setDraft(task.title);
  };

  return (
    <li>
      <input
        type="checkbox"
        checked={task.completed}
        onChange={(e) => onToggle(task.id, e.target.checked)}
        aria-label={`Mark "${task.title}" as ${task.completed ? 'incomplete' : 'complete'}`}
      />
      {editing ? (
        <form onSubmit={handleEditSubmit}>
          <input
            type="text"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            aria-label="Edit task title"
            autoFocus
          />
          <button type="submit">Save</button>
          <button type="button" onClick={handleEditCancel}>Cancel</button>
        </form>
      ) : (
        <>
          <span
            style={{ textDecoration: task.completed ? 'line-through' : 'none' }}
          >
            {task.title}
          </span>
          <button onClick={() => setEditing(true)}>Edit</button>
          <button onClick={() => onDelete(task.id)}>Delete</button>
        </>
      )}
    </li>
  );
}
