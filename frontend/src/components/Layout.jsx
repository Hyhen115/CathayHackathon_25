import React from "react";

import Navbar from "./Navbar";
import Footer from "./Footer";

const Layout = ({ children }) => {
  return (
    <>
      {/* Navbar Start */}
      <Navbar />

      {/* Navbar End */}
      {children}
      {/* Footer Start */}
      <Footer />
    </>
  );
};

export default Layout;
