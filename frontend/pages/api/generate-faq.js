export default async function handler(req, res) {
    if (req.method === 'POST') {
      try {
        const { url } = req.body;
  
        // Send URL to Flask backend
        const response = await fetch('/api/generate-faq', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ url })
        });
  
        // Parse JSON response
        const data = await response.json();
  
        // Return generated FAQ to client
        res.status(200).json(data);
      } catch (error) {
        res.status(500).json({ error: 'Internal server error' });
      }
    } else {
      res.status(405).json({ error: 'Method not allowed' });
    }
  }
  