import { useState } from 'react';

export default function Home() {
  const [url, setUrl] = useState('');
  const [faq, setFaq] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('http://127.0.0.1:5000/api/generate-faq', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ url })
});

      const data = await response.json();
      setFaq(data.faq);
    } catch (error) {
      console.error('Error:', error);
    }
  };
  return (
    <div>
      <h1>FAQ GENERATOR</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Enter URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button type="submit">Generate</button>
      </form>
      {faq && <div>{faq}</div>}
    </div>
  );
}
