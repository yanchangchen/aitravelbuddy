import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import DeskPage from './pages/DeskPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/desk" element={<DeskPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
