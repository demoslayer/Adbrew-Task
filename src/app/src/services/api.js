
 // API service layer
 
import { API_BASE_URL, API_ENDPOINTS, REQUEST_TIMEOUT } from '../config';


 // Custom error class for API errors
 
export class APIError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}


 // Create a fetch request with timeout
 
const fetchWithTimeout = (url, options = {}, timeout = REQUEST_TIMEOUT) => {
  return Promise.race([
    fetch(url, options),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Request timeout')), timeout)
    ),
  ]);
};

 // Handle API response and extract JSON data
 
const handleResponse = async (response) => {
  const contentType = response.headers.get('content-type');
  
  if (!contentType || !contentType.includes('application/json')) {
    throw new APIError(
      'Invalid response format',
      response.status,
      { message: 'Server returned non-JSON response' }
    );
  }

  const data = await response.json();

  if (!response.ok) {
    throw new APIError(
      data.error || data.detail || `HTTP error! status: ${response.status}`,
      response.status,
      data
    );
  }

  return data;
};


 // API service for TODO operations
 
export const todoAPI = {
  /**
   // Fetch all todos
   * @returns {Promise<Array>} Array of todo objects
   * @throws {APIError} If request fails
   */
  async getAllTodos() {
    try {
      const response = await fetchWithTimeout(`${API_BASE_URL}${API_ENDPOINTS.TODOS}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await handleResponse(response);
      return data.todos || [];
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      
      // Handle network errors, timeouts, etc.
      if (error.message === 'Request timeout') {
        throw new APIError(
          'Request timed out. Please check your connection and try again.',
          408
        );
      }
      
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new APIError(
          'Network error. Please check your connection.',
          0
        );
      }
      
      throw new APIError(
        error.message || 'An unexpected error occurred',
        500,
        { originalError: error.message }
      );
    }
  },

  /**
   * Create a new todo
   * @param {string} description - Todo description
   * @returns {Promise<Object>} Created todo object
   * @throws {APIError} If request fails
   */
  async createTodo(description) {
    try {
      const response = await fetchWithTimeout(
        `${API_BASE_URL}${API_ENDPOINTS.TODOS}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ description }),
        }
      );

      const data = await handleResponse(response);
      return data.todo || data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      
      // Handle network errors, timeouts, etc.
      if (error.message === 'Request timeout') {
        throw new APIError(
          'Request timed out. Please check your connection and try again.',
          408
        );
      }
      
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new APIError(
          'Network error. Please check your connection.',
          0
        );
      }
      
      throw new APIError(
        error.message || 'An unexpected error occurred',
        500,
        { originalError: error.message }
      );
    }
  },
};

