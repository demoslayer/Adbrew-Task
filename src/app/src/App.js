import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import { todoAPI, APIError } from './services/api';
import { MAX_DESCRIPTION_LENGTH } from './config';


 // Custom hook to manage API calls for todos
 
const useTodos = () => {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchTodos = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const todosData = await todoAPI.getAllTodos();
      setTodos(todosData);
    } catch (err) {
      const errorMessage = err instanceof APIError 
        ? err.message 
        : 'Failed to fetch todos. Please try again.';
      setError(errorMessage);
      console.error('Error fetching todos:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const createTodo = async (description) => {
    setError(null);
    try {
      const createdTodo = await todoAPI.createTodo(description);
      // Refresh the todo list after successful creation
      await fetchTodos();
      return createdTodo;
    } catch (err) {
      const errorMessage = err instanceof APIError 
        ? err.message 
        : 'Failed to create todo. Please try again.';
      setError(errorMessage);
      console.error('Error creating todo:', err);
      throw err;
    }
  };

  return { todos, loading, error, fetchTodos, createTodo };
};


 // Main App component using React Hooks
 
export function App() {
  const { todos, loading, error, fetchTodos, createTodo } = useTodos();
  const [todoInput, setTodoInput] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  // Fetch todos on component mount
  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]); // Include fetchTodos in dependency array


  //Handle form submission with validation
   
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const trimmedInput = todoInput.trim();
    
    // Client-side validation
    if (!trimmedInput) {
      setSubmitError('Please enter a todo description');
      return;
    }

    if (trimmedInput.length > MAX_DESCRIPTION_LENGTH) {
      setSubmitError(`Description cannot exceed ${MAX_DESCRIPTION_LENGTH} characters`);
      return;
    }

    setSubmitting(true);
    setSubmitError(null);

    try {
      await createTodo(trimmedInput);
      setTodoInput(''); // Clear input on success
    } catch (err) {
      // Error message is already set by createTodo hook
      // But we can provide more specific feedback here if needed
      const errorMessage = err instanceof APIError 
        ? err.message 
        : 'Failed to create todo. Please try again.';
      setSubmitError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="App">
      <div className="app-container">
        <div className="app-header">
          <h1> My TODO App</h1>
          <p>Stay organized and get things done</p>
        </div>

        
        <div className="todo-card">
          <h2> List of TODOs</h2>
          <div className="todo-list-container">
            {loading && (
              <div className="loading-state">
                <span className="loading-spinner"></span>
                Loading todos...
              </div>
            )}
            {error && (
              <div className="error-state">
                Error: {error}
              </div>
            )}
            {!loading && !error && (
              <ul className="todo-list">
                {todos.length === 0 ? (
                  <li className="empty-state">
                    No todos yet. Create one below!
                  </li>
                ) : (
                  todos.map((todo) => (
                    <li key={todo.id} className="todo-item">
                      <span className="todo-text">{todo.description}</span>
                    </li>
                  ))
                )}
              </ul>
            )}
          </div>
        </div>

        {/* Create Todo Card */}
        <div className="todo-card">
          <h2> Create a ToDo</h2>
          <form onSubmit={handleSubmit} className="todo-form">
            <div className="form-group">
              <label htmlFor="todo">What needs to be done?</label>
              <input
                type="text"
                id="todo"
                className="form-input"
                value={todoInput}
                onChange={(e) => {
                  const value = e.target.value;
                  // Prevent input if exceeds max length
                  if (value.length <= MAX_DESCRIPTION_LENGTH) {
                    setTodoInput(value);
                    setSubmitError(null); // Clear error when user types
                  }
                }}
                disabled={submitting}
                placeholder="Enter todo description..."
                maxLength={MAX_DESCRIPTION_LENGTH}
                aria-label="Todo description input"
              />
            </div>
            {submitError && (
              <div className="error-message">
                {submitError}
              </div>
            )}
            <button
              type="submit"
              className="submit-button"
              disabled={submitting || !todoInput.trim()}
            >
              {submitting ? (
                <>
                  <span className="loading-spinner"></span>
                  Adding...
                </>
              ) : (
                'Add ToDo! '
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
