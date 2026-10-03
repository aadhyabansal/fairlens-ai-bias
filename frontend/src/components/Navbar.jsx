import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
  const location = useLocation();

  const linkClass = (path) =>
    `px-4 py-2 rounded-md text-sm font-medium ${
      location.pathname === path
        ? 'bg-blue-600 text-white'
        : 'text-gray-600 hover:bg-gray-100'
    }`;

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <span className="font-bold text-lg text-gray-900">FairLens</span>
        <div className="flex gap-2">
          <Link to="/" className={linkClass('/')}>New Audit</Link>
          <Link to="/dashboard" className={linkClass('/dashboard')}>Dashboard</Link>
          <Link to="/history" className={linkClass('/history')}>History</Link>
        </div>
      </div>
    </nav>
  );
}