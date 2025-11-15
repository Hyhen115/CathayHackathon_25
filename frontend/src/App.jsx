import React from "react";

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";

import Home from "./components/Home";
const App = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/Shopper/UI" element={<Home />} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;
