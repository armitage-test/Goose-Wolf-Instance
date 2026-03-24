import { render, screen } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';
import TaskList from './TaskList';

const noop = vi.fn();

describe('TaskList', () => {
  it('shows empty state message when no tasks', () => {
    render(<TaskList tasks={[]} onToggle={noop} onDelete={noop} onEdit={noop} />);
    expect(screen.getByText(/no tasks yet/i)).toBeInTheDocument();
  });

  it('renders a task item for each task', () => {
    const tasks = [
      { id: 1, title: 'Task one', completed: false },
      { id: 2, title: 'Task two', completed: true },
    ];
    render(<TaskList tasks={tasks} onToggle={noop} onDelete={noop} onEdit={noop} />);
    expect(screen.getByText('Task one')).toBeInTheDocument();
    expect(screen.getByText('Task two')).toBeInTheDocument();
  });
});
