import React, { useState } from 'react';
import { FileText, Download, X, CheckCircle2, FileSpreadsheet, FileCode } from 'lucide-react';

export default function ReportGeneratorModal({ onClose }) {
  const [reportType, setReportType] = useState('OPERATIONAL'); // OPERATIONAL, INCIDENT, FINANCIAL, AI_PERFORMANCE, SLA
  const [format, setFormat] = useState('PDF'); // PDF, EXCEL, CSV
  const [downloading, setDownloading] = useState(false);
  const [downloadNotice, setDownloadNotice] = useState(null);

  const handleDownload = () => {
    setDownloading(true);
    setTimeout(() => {
      setDownloading(false);
      setDownloadNotice(`✅ Generated and downloaded ${reportType}_REPORT.${format.toLowerCase()} successfully!`);
      setTimeout(() => setDownloadNotice(null), 4000);
    }, 1200);
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-md rounded-2xl border dark:border-slate-800 border-slate-200 p-6 shadow-2xl space-y-4 text-xs">
        <div className="flex items-center justify-between border-b dark:border-slate-800 border-slate-200 pb-3">
          <div className="flex items-center space-x-2 font-bold text-sm text-slate-100">
            <FileText className="w-5 h-5 text-brand-400" />
            <span>Generate Executive Reports</span>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-800 text-slate-400">
            <X className="w-5 h-5" />
          </button>
        </div>

        {downloadNotice && (
          <div className="p-3 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 font-semibold flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{downloadNotice}</span>
          </div>
        )}

        <div className="space-y-3">
          <div>
            <label className="text-[11px] font-bold text-slate-400 block mb-1">SELECT REPORT TYPE</label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="w-full bg-slate-950 text-slate-100 rounded-xl px-3 py-2 border border-slate-800 focus:outline-none focus:border-brand-500"
            >
              <option value="OPERATIONAL">Operational Summary Report</option>
              <option value="INCIDENT">Incident & Recovery Triage Report</option>
              <option value="FINANCIAL">Financial Savings & Claims Report</option>
              <option value="AI_PERFORMANCE">LangGraph AI Agents Execution Report</option>
              <option value="SLA">Customer SLA Compliance Report</option>
            </select>
          </div>

          <div>
            <label className="text-[11px] font-bold text-slate-400 block mb-1">EXPORT FORMAT</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'PDF', label: 'PDF Document', icon: FileText, color: 'text-red-400' },
                { id: 'EXCEL', label: 'Excel Sheet', icon: FileSpreadsheet, color: 'text-emerald-400' },
                { id: 'CSV', label: 'Raw CSV', icon: FileCode, color: 'text-brand-400' }
              ].map((f) => {
                const Icon = f.icon;
                const isSelected = format === f.id;
                return (
                  <button
                    key={f.id}
                    onClick={() => setFormat(f.id)}
                    className={`p-2.5 rounded-xl border flex flex-col items-center justify-center space-y-1 transition-all ${
                      isSelected
                        ? 'bg-slate-800 border-brand-500 text-slate-100 font-bold ring-2 ring-brand-500/30'
                        : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${f.color}`} />
                    <span className="text-[11px]">{f.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        <button
          disabled={downloading}
          onClick={handleDownload}
          className="w-full py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-extrabold text-xs shadow-lg shadow-brand-600/30 flex items-center justify-center space-x-2 transition-all mt-4"
        >
          <Download className="w-4 h-4" />
          <span>{downloading ? 'Exporting File...' : `Download ${reportType} Report (${format})`}</span>
        </button>
      </div>
    </div>
  );
}
