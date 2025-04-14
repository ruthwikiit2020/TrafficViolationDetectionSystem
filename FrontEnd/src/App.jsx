import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './component/Navbar';
import Home from './component/Home/Home';
import Echallan from './component/Echallan/echallan';
import EducationSection from './component/EducationSection/EducationSection';
import './index.css'

function App() {
  return (
    <div>
      <Router>
        <Navbar/>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/echallan" element={<Echallan />} />
          <Route path="/road-safety" element={<EducationSection />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
