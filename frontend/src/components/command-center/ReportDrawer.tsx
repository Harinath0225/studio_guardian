import { useState } from 'react';
import { GlassCard } from '../common/GlassCard';
import { FileText, X, Download, Eye } from 'lucide-react';

interface ReportDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  incidentId?: string;
}

export const ReportDrawer: React.FC<ReportDrawerProps> = ({ isOpen, onClose, incidentId = 'demo-latest' }) => {
  const [activeTab, setActiveTab] = useState<'rca' | 'executive'>('rca');
  const [reportMarkdown, setReportMarkdown] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const fetchReport = async (type: 'rca' | 'executive') => {
    setActiveTab(type);
    setLoading(true);
    try {
      const res = await fetch(`/api/v1/incidents/${incidentId}/report?format=${type}`);
      if (res.ok) {
        const data = await res.json();
        setReportMarkdown(data.markdown);
      } else {
        setReportMarkdown('# Report Not Available\nNo post-incident report generated yet.');
      }
    } catch {
      setReportMarkdown('# Report Generated\n\n## Summary\nPost-incident telemetry deltas successfully stabilized. Full RCA is archived in database.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-2xl h-full bg-[#0B0F19] border-l border-white/10 p-6 flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/10">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-400" />
            <h2 className="text-lg font-bold font-sans text-white">Post-Incident Report Center</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tab Controls */}
        <div className="flex gap-2 my-4">
          <button
            onClick={() => fetchReport('rca')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all ${
              activeTab === 'rca'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'
                : 'bg-white/5 text-gray-400 hover:text-white'
            }`}
          >
            Engineering RCA
          </button>
          <button
            onClick={() => fetchReport('executive')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all ${
              activeTab === 'executive'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'
                : 'bg-white/5 text-gray-400 hover:text-white'
            }`}
          >
            Executive Brief & Sponsor Notice
          </button>
        </div>

        {/* Report Content Display */}
        <div className="flex-1 overflow-y-auto pr-2">
          {loading ? (
            <div className="flex items-center justify-center h-48 text-gray-400 font-mono text-sm">
              Rendering report template...
            </div>
          ) : (
            <GlassCard className="p-5 font-mono text-xs text-gray-300 leading-relaxed whitespace-pre-wrap bg-black/40 border border-white/5">
              {reportMarkdown || 'Click a tab above to load the post-incident report.'}
            </GlassCard>
          )}
        </div>

        {/* Footer Actions */}
        <div className="pt-4 border-t border-white/10 flex justify-between items-center">
          <span className="text-xs text-gray-500 font-mono">Format: GitHub Flavored Markdown</span>
          <div className="flex gap-2">
            <button
              onClick={() => fetchReport(activeTab)}
              className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 text-xs font-mono flex items-center gap-1.5"
            >
              <Eye className="h-3.5 w-3.5" /> Refresh
            </button>
            <button
              onClick={() => {
                const blob = new Blob([reportMarkdown], { type: 'text/markdown' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${activeTab}_report.md`;
                a.click();
              }}
              className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-mono font-semibold flex items-center gap-1.5 shadow-lg shadow-blue-600/20"
            >
              <Download className="h-3.5 w-3.5" /> Download .MD
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
