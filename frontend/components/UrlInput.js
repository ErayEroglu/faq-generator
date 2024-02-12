import React, { useState } from 'react';

const UrlInput = ({ onSubmit }) => {
  const [url, setUrl] = useState('');

  const handleChange = (e) => {
    setUrl(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(url);
    setUrl(''); // Clear input field after submission
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={url}
        onChange={handleChange}
        placeholder="Enter URL"
      />
      <button type="submit">Submit</button>
    </form>
  );
};

export default UrlInput;
