import { React, useState } from "react";
import TextField from "@mui/material/TextField";

export default function App() {
  const [url, setUrl] = useState("");
  const [faq, setFaq] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const inputHandler = async () => {
    try {
      setLoading(true); // Set loading state to true while fetching data
      setError(""); // Clear any previous error
      const response = await fetch("http://127.0.0.1:5000/api/generate-faq", {
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
      setError("An error occurred while fetching FAQ. Please try again.");
    } finally {
      setLoading(false); // Set loading state back to false after fetching data
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault(); // Prevent the default form submission behavior
      inputHandler();
    }
  };

  return (
    <div className="main">
      <h1>FAQ GENERATOR</h1>
      <div className="search">
        <TextField
          id="outlined-basic"
          onChange={(e) => setUrl(e.target.value)} // Update URL state
          onKeyDown={handleKeyDown} // Call inputHandler when Enter key is pressed
          variant="outlined"
          fullWidth
          label="Enter URL and press Enter"
        />
      </div>
      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      <ul>
        {faq.map((item, index) => (
          <li key={index} style={{ marginBottom: index % 2 === 1 ? "20px" : "0" }}>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
