import React from "react";
import Search from "./components/Search.tsx";

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <Search />
    </div>
  );
};

export default App;