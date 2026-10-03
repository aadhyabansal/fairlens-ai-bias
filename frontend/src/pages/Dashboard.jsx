import { useState } from 'react';
import { useAudit } from '../context/AuditContext';
import { generateReport } from '../api/client';
import MetricsChart from '../components/MetricsChart';
import SummaryStats from '../components/SummaryStats';

export default function Dashboard() {
  const { currentAudit, currentReport, setCurrentReport } = useAudit();
  const [loadingReport, setLoadingReport] = useState(false);

  if (!currentAudit) {
    return (
      <p className="text-gray-500">
        No audit run yet — head to <strong>New Audit</strong> to get started.
      </p>
    );
  }

  const handleGenerateReport = async () => {
    setLoadingReport(true);
    try {
      const report = await generateReport({
        audit_json: currentAudit,
        context: '',
      });
      setCurrentReport(report);
    } finally {
      setLoadingReport(false);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2 text-gray-900">Audit Results</h1>
      <p className="text-sm text-gray-500 mb-6">
        Overall model accuracy: <strong>{(currentAudit.overall_accuracy * 100).toFixed(1)}%</strong>
      </p>

      {currentAudit.metrics_by_attribute.map((attrMetrics) => (
        <div key={attrMetrics.sensitive_attribute} className="mb-8">
          <SummaryStats attributeMetrics={attrMetrics} />
          <MetricsChart attributeMetrics={attrMetrics} />
        </div>
      ))}

      {!currentReport && (
        <button
          onClick={handleGenerateReport}
          disabled={loadingReport}
          className="bg-blue-600 text-white px-5 py-2 rounded-md text-sm font-medium
                     hover:bg-blue-700 disabled:opacity-50"
        >
          {loadingReport ? 'Generating report...' : 'Generate AI Report'}
        </button>
      )}

      {currentReport && (
        <div className="mt-6 border border-gray-200 rounded-lg p-5 bg-white">
          <h2 className="font-bold text-lg mb-3 text-gray-900">Audit Report</h2>
          <p className="text-gray-700 mb-4">{currentReport.summary}</p>

          {currentReport.findings.map((f, i) => (
            <div key={i} className="border-l-4 border-blue-500 pl-4 mb-4">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-bold uppercase text-blue-700">{f.severity}</span>
                <h3 className="font-semibold text-gray-900">{f.title}</h3>
              </div>
              <p className="text-sm text-gray-600 mb-1">{f.explanation}</p>
              <p className="text-sm text-gray-900">
                <strong>Recommendation:</strong> {f.recommendation}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}