const BASE_URL = 'http://localhost:8000/api/v1';

export const WS_URL = 'ws://localhost:8000/ws/live-monitor';

export async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const url = `${BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  const token = localStorage.getItem('token');
  if (token) {
    defaultOptions.headers = {
      ...defaultOptions.headers,
      Authorization: `Bearer ${token}`
    };
  }

  // If we are sending FormData (like for audio upload), don't set Content-Type manually
  // so the browser can set the boundary automatically
  if (options.body instanceof FormData) {
    const headers = new Headers(options.headers || {});
    headers.delete('Content-Type');
    
    // Convert Headers object back to a plain object to merge with default headers
    const rawHeaders: Record<string, string> = {};
    headers.forEach((value, key) => {
      rawHeaders[key] = value;
    });
    
    defaultOptions.headers = { ...defaultOptions.headers, ...rawHeaders };
  }

  const response = await fetch(url, { ...defaultOptions, ...options });

  if (response.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
    throw new Error('Session expired. Please login again.');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.status}`);
  }

  return response.json();
}
