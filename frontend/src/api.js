const API_BASE_URL = 'http://localhost:8000/api';

async function handleResponse(response) {
  const contentType = response.headers.get('content-type');
  const hasJson = contentType && contentType.includes('application/json');
  const data = hasJson ? await response.json() : null;

  if (!response.ok) {
    const detail = data && data.message ? data.message : response.statusText;
    throw new Error(detail || 'Request failed');
  }

  return data;
}

export async function fetchUserByEmail(email) {
  const response = await fetch(`${API_BASE_URL}/users?email=${encodeURIComponent(email)}`);
  const data = await handleResponse(response);
  return data;
}

export async function logLogin(payload) {
  const response = await fetch(`${API_BASE_URL}/logins/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  return handleResponse(response);
}
