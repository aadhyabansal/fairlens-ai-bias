import { useEffect, useState } from 'react';
import { getHistory } from '../api/client';

export default function History() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getHistory()
      .then(setRuns)
      .catch(() => setError('Could not load audit history.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500">Loading history...</p>;
  if (error) return <p className="text-red-600">{error}</p>;
  if (runs.length === 0) return <p className="text-gray-500">No audits run yet.</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 text-gray-900">Audit History</h1>
      <div className="space-y-3">
        {runs.map((run) => (
          <div
            key={run.id}
            className="border border-gray-200 rounded-lg p-4 bg-white flex items-center justify-between"
          >
            <div>
              <p className="font-medium text-gray-900">{run.dataset_path}</p>
              <p className="text-sm text-gray-500">
                Target: {run.target_column} · Accuracy: {(run.overall_accuracy * 100).toFixed(1)}%
              </p>
            </div>
            <p className="text-xs text-gray-400">
              {new Date(run.created_at).toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}