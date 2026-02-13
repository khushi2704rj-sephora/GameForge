import { BrowserRouter, Routes, Route } from "react-router-dom";
import Nav from "./components/Nav";
import Landing from "./pages/Landing";
import Catalog from "./pages/Catalog";
import Simulator from "./pages/Simulator";
import "./index.css";

export default function App() {
  return (
    <BrowserRouter>
      <Nav />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/catalog" element={<Catalog />} />
        <Route path="/simulate/:gameId" element={<Simulator />} />
      </Routes>
    </BrowserRouter>
  );
}
