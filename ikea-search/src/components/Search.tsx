import React, { useState } from "react";
import API from "../api/api.ts";
import { FaThumbsUp, FaThumbsDown } from "react-icons/fa";

const highlightQuery = (text: string, query: string) => {
  if (!query) return text;
  const regex = new RegExp(`(${query})`, "gi");
  return text.replace(regex, `<span class="font-bold">$1</span>`);
};

const Search: React.FC = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [feedback, setFeedback] = useState<Record<string, "relevant" | "irrelevant" | undefined>>({});
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
      setFeedback({});
      const response = await API.post("/search/", {
        query,
        feedback: Object.keys(feedback).length > 0 ? feedback : undefined,
      });
      setResults(response.data);
      setCurrentPage(1);
    } catch (err) {
      setError("Failed to fetch search results.");
    } finally {
      setLoading(false);
    }
  };

  const toggleFeedback = async (docno: string, relevance: "relevant" | "irrelevant") => {
    const newFeedback = feedback[docno] === relevance ? undefined : relevance;

    // Update feedback state locally
    const updatedFeedback = {
      ...feedback,
      [docno]: newFeedback,
    };
    setFeedback(updatedFeedback);

    try {
      // Send updated feedback to backend
      const response = await API.post("/search/", {
        query,
        feedback: updatedFeedback, // Include updated feedback
      });

      // Update results with the backend response
      if (response.data) {
        setResults(response.data); // Replace results with backend-validated reordering
        setFeedback({});
      }
    } catch (err) {
      console.error("Failed to update results with feedback:", err);
    }
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
          placeholder="Search for IKEA hacks and reviews..."
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
            {paginatedResults.map((result) => {
              const isTrustpilot = result.link?.includes("trustpilot");
              const relevance = feedback[result.docno];

              return (
                <li
                  key={result.docno}
                  className={`p-4 border rounded mb-4 bg-white shadow hover:shadow-lg transition-shadow duration-200 relative ${relevance === "relevant" ? "border-green-500" : relevance === "irrelevant" ? "border-red-500" : ""
                    }`}
                >
                  {/* Trustpilot Reviews */}
                  {isTrustpilot ? (
                    <>
                      <h3
                        className="font-bold text-lg mb-2 text-gray-700"
                        dangerouslySetInnerHTML={{
                          __html: highlightQuery(result.raw_title, query),
                        }}
                      ></h3>
                      <p
                        className="text-gray-700 mt-2"
                        dangerouslySetInnerHTML={{
                          __html: highlightQuery(result.raw_text, query),
                        }}
                      ></p>
                      <div className="absolute bottom-2 right-2">
                        <a
                          href="https://www.trustpilot.com/review/www.ikea.com"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-500 italic hover:underline pr-2"
                        >
                          Trustpilot Review
                        </a>
                      </div>
                    </>
                  ) : (
                    // Other Documents
                    <>
                      <a
                        href={result.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline text-lg font-bold"
                        dangerouslySetInnerHTML={{
                          __html: highlightQuery(result.raw_title, query),
                        }}
                      ></a>
                      <p
                        className="line-clamp-3 text-gray-700 mt-2"
                        dangerouslySetInnerHTML={{
                          __html: highlightQuery(
                            result.raw_text
                              .split(" ")
                              .slice(0, 30)
                              .join(" ") + "...",
                            query
                          ),
                        }}
                      ></p>
                    </>
                  )}

                  {/* Relevance Score */}
                  <p className="text-sm text-gray-500 mt-2">
                    Relevance Score: {result.score?.toFixed(2)}
                  </p>

                  {/* Relevance Feedback (Thumbs) */}
                  <div className="flex space-x-4 mt-4">
                    <FaThumbsUp
                      onClick={() => toggleFeedback(result.docno, "relevant")}
                      className={`cursor-pointer text-xl ${relevance === "relevant"
                        ? "text-green-500"
                        : "text-gray-400 hover:text-green-500"
                        }`}
                    />
                    <FaThumbsDown
                      onClick={() => toggleFeedback(result.docno, "irrelevant")}
                      className={`cursor-pointer text-xl ${relevance === "irrelevant"
                        ? "text-red-500"
                        : "text-gray-400 hover:text-red-500"
                        }`}
                    />
                  </div>
                </li>
              );
            })}
          </ul>
        )}
        {!loading && hasSearched && results.length === 0 && (
          <p className="mt-4 text-gray-500">No results found.</p>
        )}
      </div>

      {/* Pagination */}
      {!loading && results.length > 0 && (
        <div className="mt-6 flex justify-center space-x-2 items-center">
          {/* Previous */}
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

          {/* Pages */}
          {visiblePages.map((page) => (
            <button
              key={page}
              onClick={() => {
                setCurrentPage(page);
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              className={`px-4 py-2 rounded ${currentPage === page ? "bg-blue-500 text-white" : "bg-gray-300"
                }`}
            >
              {page}
            </button>
          ))}

          {/* Next */}
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
