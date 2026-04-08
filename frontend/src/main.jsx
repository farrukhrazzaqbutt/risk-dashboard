import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { log } from "./logger";

log.info("Application bootstrap");

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
