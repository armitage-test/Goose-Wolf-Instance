import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import TaskItem from './TaskItem';

const baseTask = { id: 1, title: 'Buy milk', completed: false };

describe('TaskItem', () => {
  let onToggle, onDelete, onEdit;

  beforeEach(() => {
    onToggle = vi.fn();
    onDelete = vi.fn();
    onEdit = vi.fn();
  });

  it('renders task title and buttons', () => {
    render(<TaskItem task={baseTask} onToggle={onToggle} onDelete={onDelete} onEdit={onEdit} />);
    expect(screen.getByText('Buy milk')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Edit' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Delete' })).toBeInTheDocument();
  });

  it('calls onToggle when checkbox clicked', async () => {
    render(<TaskItem task={baseTask} onToggle={onToggle} onDelete={onDelete} onEdit={onEdit} />);
    await userEvent.click(screen.getByRole('checkbox'));
    expect(onToggle).toHaveBeenCalledWith(1, true);
  });

  it('calls onDelete when delete button clicked', async () => {
    render(<TaskItem task={baseTask} onToggle={onToggle} onDelete={onDelete} onEdit={onEdit} />);
    await userEvent.click(screen.getByRole('button', { name: 'Delete' }));
    expect(onDelete).toHaveBeenCalledWith(1);
  });

  it('enters edit mode when edit button clicked', async () => {
    render(<TaskItem task={baseTask} onToggle={onToggle} onDelete={onDelete} onEdit={onEdit} />);
    await userEvent.click(screen.getByRole('button', { name: 'Edit' }));
    expect(screen.getByLabelText('Edit task title')).toBeInTheDocument();
  });

  it('calls onEdit with new title on save', async () => {
    render(<TaskItem task={baseTask} onToggle={onToggle} onDelete={onDelete} onEdit={onEdit} />);
    await userEvent.click(screen.getByRole('button', { name: 'Edit' }));
    const input = screen.getByLabelText('Edit task title');
    await userEvent.clear(input);
    await userEvent.type(input, 'Buy oat milk');
    await userEvent.click(screen.getByRole('button', { name: 'Save' }));
    expect(onEdit).toHaveBeenCalledWith(1, 'Buy oat milk');
  });

  it('cancels edit without calling onEdit', async () => {
    render(<TaskItem task={baseTask} onToggle={onToggle} onDelete={onDelete} onEdit={onEdit} />);
    await userEvent.click(screen.getByRole('button', { name: 'Edit' }));
    await userEvent.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(onEdit).not.toHaveBeenCalled();
    expect(screen.getByText('Buy milk')).toBeInTheDocument();
  });

  it('applies line-through style for completed tasks', () => {
    const completedTask = { ...baseTask, completed: true };
    render(<TaskItem task={completedTask} onToggle={onToggle} onDelete={onDelete} onEdit={onEdit} />);
    const span = screen.getByText('Buy milk');
    expect(span).toHaveStyle({ textDecoration: 'line-through' });
  });
});
