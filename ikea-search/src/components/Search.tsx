import React, { useState } from "react";
import API from "../api/api.ts";

const Search: React.FC = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await API.get("/search/", { params: { query } });
      setResults(response.data);
    } catch (err) {
      setError("Failed to fetch search results.");
    }
    setLoading(false);
  };

  return (
    <div className="container mx-auto p-6">
      <form onSubmit={handleSearch} className="flex space-x-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for IKEA hacks..."
          className="border rounded px-4 py-2 w-full"
        />
        <button className="bg-blue-500 text-white px-4 py-2 rounded" type="submit">
          Search
        </button>
      </form>

      {loading && <p className="mt-4 text-blue-500">Loading...</p>}
      {error && <p className="mt-4 text-red-500">{error}</p>}

      <div className="mt-6">
        {results.length > 0 && (
          <ul>
            {results.map((result) => (
              <li key={result.docno} className="p-4 border rounded mb-4 bg-white">
                <h3 className="font-bold">{result.raw_title}</h3>
                <p>{result.raw_text}</p>
                <p className="text-sm text-gray-500">Relevance Score: {result.score.toFixed(2)}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Search;