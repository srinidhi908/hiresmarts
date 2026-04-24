import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { useEffect } from "react";

import Home from "./pages/Home";
import Applicant from "./pages/Applicant";
import Recruiter from "./pages/Recruiter";

/* 🔹 Scroll to top on page change */
function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

/* 🔹 Main App */
function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/applicant" element={<Applicant />} />
        <Route path="/recruiter" element={<Recruiter />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;