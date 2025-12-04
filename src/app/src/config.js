
 // Application configuration
 

// API base URL - can be overridden via environment variable
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// API endpoints
export const API_ENDPOINTS = {
  TODOS: '/todos/',
};

// Request timeout in milliseconds
export const REQUEST_TIMEOUT = 10000;

// Maximum description length
export const MAX_DESCRIPTION_LENGTH = 1000;

