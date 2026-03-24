import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import App from './App';
import * as api from './api/tasks';

vi.mock('./api/tasks');

const mockTasks = [
  { id: 1, title: 'Buy milk', completed: false, description: null, created_at: '', updated_at: '' },
];

beforeEach(() => {
  vi.clearAllMocks();
  api.fetchTasks.mockResolvedValue(mockTasks);
});

describe('App', () => {
  it('renders heading', async () => {
    render(<App />);
    expect(screen.getByText('Todo Manager')).toBeInTheDocument();
  });

  it('loads and displays tasks on mount', async () => {
    render(<App />);
    await waitFor(() => screen.getByText('Buy milk'));
    expect(api.fetchTasks).toHaveBeenCalledOnce();
  });

  it('shows error message when fetchTasks fails', async () => {
    api.fetchTasks.mockRejectedValue(new Error('Network error'));
    render(<App />);
    await waitFor(() => screen.getByRole('alert'));
    expect(screen.getByRole('alert')).toHaveTextContent('Network error');
  });

  it('adds a new task via the form', async () => {
    const newTask = { id: 2, title: 'Walk dog', completed: false, description: null, created_at: '', updated_at: '' };
    api.createTask.mockResolvedValue(newTask);
    render(<App />);
    await waitFor(() => screen.getByText('Buy milk'));

    await userEvent.type(screen.getByLabelText('New task title'), 'Walk dog');
    await userEvent.click(screen.getByRole('button', { name: 'Add' }));

    await waitFor(() => screen.getByText('Walk dog'));
    expect(api.createTask).toHaveBeenCalledWith('Walk dog');
  });

  it('deletes a task', async () => {
    api.deleteTask.mockResolvedValue(undefined);
    render(<App />);
    await waitFor(() => screen.getByText('Buy milk'));

    await userEvent.click(screen.getByRole('button', { name: 'Delete' }));

    await waitFor(() => expect(screen.queryByText('Buy milk')).not.toBeInTheDocument());
    expect(api.deleteTask).toHaveBeenCalledWith(1);
  });
});
