import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadDataset, runAudit } from '../api/client';
import { useAudit } from '../context/AuditContext';

export default function NewAudit() {
  const [file, setFile] = useState(null);
  const [targetColumn, setTargetColumn] = useState('');
  const [sensitiveAttrs, setSensitiveAttrs] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { setCurrentAudit } = useAudit();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const { dataset_path } = await uploadDataset(file);

      const result = await runAudit({
        dataset_path,
        target_column: targetColumn,
        sensitive_attributes: sensitiveAttrs.split(',').map((s) => s.trim()),
      });

      setCurrentAudit(result);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong running the audit.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl">
      <h1 className="text-2xl font-bold mb-6 text-gray-900">Run a New Audit</h1>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Dataset (CSV)
          </label>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
            required
            className="block w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4
                       file:rounded-md file:border-0 file:bg-blue-50 file:text-blue-700
                       hover:file:bg-blue-100"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Target Column
          </label>
          <input
            type="text"
            value={targetColumn}
            onChange={(e) => setTargetColumn(e.target.value)}
            placeholder="e.g. income"
            required
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Sensitive Attributes (comma-separated)
          </label>
          <input
            type="text"
            value={sensitiveAttrs}
            onChange={(e) => setSensitiveAttrs(e.target.value)}
            placeholder="e.g. sex, race"
            required
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {error && (
          <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-5 py-2 rounded-md text-sm font-medium
                     hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Running audit...' : 'Run Audit'}
        </button>
      </form>
    </div>
  );
}