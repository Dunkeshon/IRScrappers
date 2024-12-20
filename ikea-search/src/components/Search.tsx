/* eslint-disable react-hooks/exhaustive-deps */
import React, { useState, useEffect, useCallback } from "react";
import API from "../api/api";
import { FaThumbsUp, FaThumbsDown } from "react-icons/fa";
import ikeaLogo from "../png-transparent-forniture-ikea-logo-orange-famous-logos-in-orange-icon-removebg-preview.png";
import { useLocation } from "react-router-dom";

const highlightQuery = (text: string, query: string) => {
  if (!query) return text;
  const regex = new RegExp(`(${query})`, "gi");
  return text.replace(regex, `<span class="font-bold text-blue-700">$1</span>`);
};

const Search: React.FC = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [feedback, setFeedback] = useState<Record<string, "relevant" | "irrelevant" | undefined>>({});
  const [visualFeedback, setVisualFeedback] = useState<Record<string, "relevant" | "irrelevant" | undefined>>({});
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);
  const [tabCounts, setTabCounts] = useState({ all: 0, articles: 0, reviews: 0 });
  const [activeTab, setActiveTab] = useState<"all" | "articles" | "reviews">("all");
  const [isResetting, setIsResetting] = useState(false);

  const resultsPerPage = 5;
  const pagesToShow = 10;

  const location = useLocation();

  const updateUrlWithQuery = (query: string) => {
    const params = new URLSearchParams();
    if (query) {
      params.set("query", query);
      window.history.replaceState({}, "", `?${params.toString()}`);
    } else {
      window.history.replaceState({}, "", "/");
    }
  };

  const handleSearch = useCallback(
    async (e?: React.FormEvent, queryParam?: string) => {
      if (e) e.preventDefault();
      const searchQuery = queryParam || query;
      if (!searchQuery.trim()) return;

      setResults([]);
      setLoading(true);
      setError("");
      setHasSearched(true);
      setActiveTab("all");

      try {
        updateUrlWithQuery(searchQuery);
        setFeedback({});
        setVisualFeedback({});
        const response = await API.post("/search/", {
          query: searchQuery,
          feedback: undefined,
        });
        setResults(response.data);
        setCurrentPage(1);
        calculateTabCounts(response.data);
      } catch (err) {
        setError("Failed to fetch search results.");
      } finally {
        setLoading(false);
      }
    },
    [query]
  );

  

  

  useEffect(() => {
    if (isResetting) return;

    const params = new URLSearchParams(location.search);
    const queryFromUrl = params.get("query");
  
    // Only set query if it's from the URL and query state is empty
    if (queryFromUrl && query === "") {
      setQuery(queryFromUrl);
      handleSearch(undefined, queryFromUrl);
    }
  }, [location.search]);

  const resetPage = () => {
    setIsResetting(true);
    setQuery("");
    setResults([]);
    setHasSearched(false);
    setActiveTab("all");
    updateUrlWithQuery("");
  };



  const toggleFeedback = async (docno: string, relevance: "relevant" | "irrelevant") => {
    const newFeedback = feedback[docno] === relevance ? undefined : relevance;
    const updatedVisualFeedback = {
      ...visualFeedback,
      [docno]: newFeedback,
    };
    setVisualFeedback(updatedVisualFeedback);
    const updatedFeedback = {
      ...feedback,
      [docno]: newFeedback,
    };
    if (newFeedback === undefined) {
      delete updatedFeedback[docno];
    }
    setFeedback(updatedFeedback);
    if (newFeedback !== undefined) {
      try {
        const response = await API.post("/search/", {
          query,
          feedback: { [docno]: newFeedback },
        });
        if (response.data) {
          setResults(response.data);
          calculateTabCounts(response.data);
        }
      } catch (err) {
        console.error("Failed to update results with feedback:", err);
      }
    }
  };



  const calculateTabCounts = (data: any[]) => {
    const counts = { all: data.length, articles: 0, reviews: 0 };
    data.forEach((result) => {
      if (result.link?.includes("trustpilot")) {
        counts.reviews++;
      } else {
        counts.articles++;
      }
    });
    setTabCounts(counts);
  };

  const filteredResults = results.filter((result) => {
    if (activeTab === "all") return true;
    if (activeTab === "articles") return !result.link?.includes("trustpilot");
    if (activeTab === "reviews") return result.link?.includes("trustpilot");
    return false;
  });

  const paginatedResults = filteredResults.slice(
    (currentPage - 1) * resultsPerPage,
    currentPage * resultsPerPage
  );

  const totalPages = Math.ceil(filteredResults.length / resultsPerPage);
  const half = Math.floor(pagesToShow / 2);
  const startPage = Math.max(1, currentPage - half);
  const endPage = Math.min(totalPages, startPage + pagesToShow - 1);
  const visiblePages = Array.from(
    { length: endPage - startPage + 1 },
    (_, index) => startPage + index
  );

  const sortedTabs = ["all", "articles", "reviews"].sort(
    (a, b) => tabCounts[b as keyof typeof tabCounts] - tabCounts[a as keyof typeof tabCounts]
  );

  return (
    <>
    <div
        className={`background-image ${results.length > 0 ? "blur" : ""}`}
      ></div>
    <div className="container mx-auto p-6 font-sans">
      {/* Title Section */}
      <div className="text-center mb-10">
        <div
          className="flex flex-col items-center cursor-pointer"
          onClick={resetPage}
        >
          {/* Modern IKEA-inspired SVG */}
          <img
            src={ikeaLogo}
            alt="IKEA Hacks Logo"
            className="w-40 h-40"
          />
          {/* Title */}
          <h1 className="text-5xl font-extrabold text-yellow-400 drop-shadow-lg">
            IKEA Hacks
          </h1>
        </div>
        {/* Subtext */}
        <p className="text-lg text-gray-200 mt-2 max-w-xl mx-auto">
          Search for smart IKEA ideas to upgrade and customize your space.
        </p>
      </div>


      {/* Search Form */}
      <form onSubmit={handleSearch} className="flex space-x-2 justify-center">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for IKEA hacks and reviews..."
          className="border rounded px-4 py-2 w-1/2 focus:ring-2 focus:ring-yellow-400 focus:outline-none"
        />
        <button
          className="bg-yellow-500 text-white px-6 py-2 rounded hover:bg-yellow-600 transition-all duration-200"
          type="submit"
        >
          Search
        </button>
      </form>

      {/* Tabs */}
      {hasSearched && !loading && (
        <div className="mt-6 flex justify-center space-x-6 border-b">
          {sortedTabs.map((tab) => (
            <button
              key={tab}
              className={`pb-2 px-4 text-lg transition-all duration-200 ${activeTab === tab
                ? "text-yellow-500 border-b-2 border-yellow-500"
                : "text-white hover:text-yellow-500"
                }`}
              onClick={() => {
                setActiveTab(tab as "all" | "articles" | "reviews");
                setCurrentPage(1);
              }}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)} ({tabCounts[tab as keyof typeof tabCounts]})
            </button>
          ))}
        </div>
      )}

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
              const relevance = visualFeedback[result.docno];

              return (
                <li
                  key={result.docno}
                  className={`p-4 border rounded mb-4 bg-white shadow transition-shadow duration-200 relative 
                      ${relevance === "relevant"
                      ? "shadow-[0_0_12px_4px_#22c55e] hover:shadow-[0_0_12px_4px_#22c55e]"
                      : relevance === "irrelevant"
                        ? "shadow-[0_0_12px_4px_#ef4444] hover:shadow-[0_0_12px_4px_#ef4444]"
                        : "hover:shadow-[0_0_12px_4px_#facc15] transition-shadow duration-200"
                    }`}
                >

                  {/* Content */}
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
                          className="text-lg text-blue-500 italic hover:underline pr-2"
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

                  <p className="text-sm text-gray-500 mt-2">
                    Relevance Score: {result.score?.toFixed(2)}
                  </p>

                  <div className="flex space-x-4 mt-4">
                    <FaThumbsUp
                      onClick={() => toggleFeedback(result.docno, "relevant")}
                      className={`cursor-pointer text-2xl ${relevance === "relevant"
                        ? "text-green-500 hover:text-green-500"
                        : "text-gray-400 hover:text-gray-500"
                        }`}
                    />
                    <FaThumbsDown
                      onClick={() => toggleFeedback(result.docno, "irrelevant")}
                      className={`cursor-pointer text-2xl ${relevance === "irrelevant"
                        ? "text-red-500 hover:text-red-500"
                        : "text-gray-400 hover:text-gray-500"
                        }`}
                    />
                  </div>
                </li>
              );
            })}
          </ul>
        )}
        {!loading && hasSearched && filteredResults.length === 0 && (
          <p className="mt-4 text-white flex justify-center">No results found for this tab.</p>
        )}
      </div>

      {/* Pagination */}
      {!loading && filteredResults.length > 0 && (
        <div className="mt-6 flex justify-center space-x-2 items-center">
          {currentPage > 1 && (
            <button
              onClick={() => {
                setCurrentPage(currentPage - 1);
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              className="w-24 px-4 py-2 rounded bg-yellow-500 text-white hover:bg-yellow-600 transition-all duration-200 text-center"
              >
              Previous
            </button>
          )}
          {visiblePages.map((page) => (
            <button
              key={page}
              onClick={() => {
                setCurrentPage(page);
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              className={`px-4 py-2 rounded ${currentPage === page
                ? "bg-yellow-500 text-white"
                : "bg-gray-300 hover:bg-gray-400"
                }`}
            >
              {page}
            </button>
          ))}
          {currentPage < totalPages && (
            <button
              onClick={() => {
                setCurrentPage(currentPage + 1);
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              className="w-24 px-4 py-2 rounded bg-yellow-500 text-white hover:bg-yellow-600 transition-all duration-200 text-center"
              >
              Next
            </button>
          )}
        </div>
      )}
    </div>
    </>
  );
};

export default Search;
