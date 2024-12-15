import React, { useState } from "react";
import API from "../api/api.ts";

const Search: React.FC = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  const resultsPerPage = 5;
  const pagesToShow = 10;

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setHasSearched(true);
    try {
      const response = await API.get("/search/", { params: { query } });
      setResults(response.data);
      setCurrentPage(1);
    } catch (err) {
      setError("Failed to fetch search results.");
    }
    setLoading(false);
  };

  const paginatedResults = results.slice(
    (currentPage - 1) * resultsPerPage,
    currentPage * resultsPerPage
  );

  const totalPages = Math.ceil(results.length / resultsPerPage);

  const half = Math.floor(pagesToShow / 2);
  const startPage = Math.max(1, currentPage - half);
  const endPage = Math.min(totalPages, startPage + pagesToShow - 1);

  const visiblePages = Array.from(
    { length: endPage - startPage + 1 },
    (_, index) => startPage + index
  );

  return (
    <div className="container mx-auto p-6">
      {/* Search Form */}
      <form onSubmit={handleSearch} className="flex space-x-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for IKEA hacks..."
          className="border rounded px-4 py-2 w-full"
        />
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded"
          type="submit"
        >
          Search
        </button>
      </form>

      {/* Loading Spinner */}
      {loading && !results.length && (
        <div className="mt-6 flex justify-center">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}

      {/* Skeleton Loader */}
      {loading && results.length === 0 && (
        <div className="mt-6 space-y-4">
          {[1, 2, 3, 4, 5].map((_, index) => (
            <div key={index} className="animate-pulse p-4 border rounded bg-white">
              <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      )}

      {/* Error Message */}
      {error && <p className="mt-4 text-red-500">{error}</p>}

      {/* Results */}
      <div className="mt-6">
        {paginatedResults.length > 0 && !loading && (
          <ul>
            {paginatedResults.map((result) => (
              <li
                key={`${result.docno}-${Math.random()}`}
                className="p-4 border rounded mb-4 bg-white"
              >
                <h3 className="font-bold">{result.raw_title}</h3>
                <p>{result.raw_text}</p>
                <p className="text-sm text-gray-500">
                  Relevance Score: {result.score.toFixed(2)}
                </p>
              </li>
            ))}
          </ul>
        )}
        {!loading && hasSearched && results.length === 0 && (
          <p className="mt-4 text-gray-500">No results found.</p>
        )}
      </div>

      {/* Google-Style Pagination */}
      {!loading && results.length > 0 && (
        <div className="mt-6 flex justify-center space-x-2 items-center">
          {/* Previous Button */}
          {currentPage > 1 && (
            <button
              onClick={() => {
                setCurrentPage(currentPage - 1);
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              className="px-4 py-2 rounded bg-gray-300"
            >
              Previous
            </button>
          )}

          {/* Page Buttons */}
          {visiblePages.map((page) => (
            <button
              key={page}
              onClick={() => {
                setCurrentPage(page);
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              className={`px-4 py-2 rounded ${
                currentPage === page ? "bg-blue-500 text-white" : "bg-gray-300"
              }`}
            >
              {page}
            </button>
          ))}

          {/* Next Button */}
          {currentPage < totalPages && (
            <button
              onClick={() => {
                setCurrentPage(currentPage + 1);
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              className="px-4 py-2 rounded bg-gray-300"
            >
              Next
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default Search;