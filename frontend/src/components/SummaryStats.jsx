export default function SummaryStats({ attributeMetrics }) {
  const stats = [
    { label: 'Demographic Parity Diff', value: attributeMetrics.demographic_parity_difference },
    { label: 'Equalized Odds Diff', value: attributeMetrics.equalized_odds_difference },
    { label: 'Disparate Impact Ratio', value: attributeMetrics.disparate_impact_ratio, flagLow: true },
  ];

  return (
    <div className="grid grid-cols-3 gap-4 mb-4">
      {stats.map((s) => {
        const isFlagged = s.flagLow ? s.value < 0.8 : s.value > 0.1;
        return (
          <div
            key={s.label}
            className={`border rounded-lg p-4 ${isFlagged ? 'border-red-200 bg-red-50' : 'border-gray-200 bg-white'}`}
          >
            <p className="text-xs text-gray-500 mb-1">{s.label}</p>
            <p className={`text-2xl font-bold ${isFlagged ? 'text-red-700' : 'text-gray-900'}`}>
              {s.value.toFixed(3)}
            </p>
          </div>
        );
      })}
    </div>
  );
}