import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function MetricsChart({ attributeMetrics }) {
  const data = attributeMetrics.subgroups.map((sg) => ({
    group: sg.group_name,
    'Selection Rate': +(sg.selection_rate * 100).toFixed(1),
    'False Negative Rate': +(sg.false_negative_rate * 100).toFixed(1),
  }));

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <h3 className="font-semibold text-gray-900 mb-1">
        {attributeMetrics.sensitive_attribute} — Selection & Error Rates by Group
      </h3>
      <p className="text-sm text-gray-500 mb-4">All values shown as percentages</p>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <XAxis dataKey="group" />
          <YAxis unit="%" />
          <Tooltip />
          <Legend />
          <Bar dataKey="Selection Rate" fill="#2563eb" />
          <Bar dataKey="False Negative Rate" fill="#dc2626" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}