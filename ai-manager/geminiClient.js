const apiKey = process.env.GEMINI_API_KEY;

if (!apiKey) {
  throw new Error('Missing GEMINI_API_KEY in environment');
}

console.log('Gemini connected');

async function createPlan(message) {
  const endpoint = 'https://gemini.googleapis.com/v1/models/gemini-1.5:predict';
  const body = {
    instances: [{ content: `You are an AI agent. Create a JSON-style executable command plan for this user task: ${message}` }],
  };

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Gemini request failed: ${response.status} ${response.statusText} - ${errorText}`);
  }

  const data = await response.json();
  return data;
}

module.exports = { createPlan };
