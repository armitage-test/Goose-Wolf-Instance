import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect } from 'vitest';
import TaskForm from './TaskForm';

describe('TaskForm', () => {
  it('renders input and button', () => {
    render(<TaskForm onSubmit={vi.fn()} />);
    expect(screen.getByLabelText('New task title')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Add' })).toBeInTheDocument();
  });

  it('calls onSubmit with trimmed title', async () => {
    const onSubmit = vi.fn();
    render(<TaskForm onSubmit={onSubmit} />);
    await userEvent.type(screen.getByLabelText('New task title'), '  Buy milk  ');
    await userEvent.click(screen.getByRole('button', { name: 'Add' }));
    expect(onSubmit).toHaveBeenCalledWith('Buy milk');
  });

  it('clears input after submit', async () => {
    render(<TaskForm onSubmit={vi.fn()} />);
    const input = screen.getByLabelText('New task title');
    await userEvent.type(input, 'Task');
    await userEvent.click(screen.getByRole('button', { name: 'Add' }));
    expect(input).toHaveValue('');
  });

  it('does not call onSubmit when input is empty', async () => {
    const onSubmit = vi.fn();
    render(<TaskForm onSubmit={onSubmit} />);
    await userEvent.click(screen.getByRole('button', { name: 'Add' }));
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('does not call onSubmit for whitespace-only input', async () => {
    const onSubmit = vi.fn();
    render(<TaskForm onSubmit={onSubmit} />);
    await userEvent.type(screen.getByLabelText('New task title'), '   ');
    await userEvent.click(screen.getByRole('button', { name: 'Add' }));
    expect(onSubmit).not.toHaveBeenCalled();
  });
});
