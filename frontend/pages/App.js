import React, { useState } from "react";
import TextField from "@mui/material/TextField";

export default function App() {
  const [url, setUrl] = useState("");
  const [faq, setFaq] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const BASE_URL = "http://127.0.0.1:5000";

  const inputHandler = async () => {
    try {
      setLoading(true);
      setError("");
      setFaq([]);
      
      const response = await fetch(BASE_URL + "/generate-faq", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });
      const data = await response.json();
      setFaq(data.faq);
    } catch (error) {
      console.error("Error:", error);
      setError("An error occurred while fetching FAQ. Please check the url and github repository.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      inputHandler();
    }
  };

  return (
    <div className="main">
      <h1>FAQ GENERATOR</h1>
      <div className="search">
        <TextField
          id="outlined-basic"
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={handleKeyDown}
          variant="filled"
          fullWidth
          label="Insert the URL and press Enter"
        />
      </div>
      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      <ul>
        {faq.map((item, index) => (
          <li
            key={index}
            style={{
              marginBottom: (faq[index + 1] && faq[index + 1].match(/^\d+\./)) ? "20px" : "0",
              fontWeight: item.match(/^\d+\./) ? "bold" : "normal",
            }}
          >
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
