import { useState, useEffect } from 'react';
import axios from 'axios';
import { ShieldAlert, Activity, FileText } from 'lucide-react';

interface Anomaly {
  id: string;
  title: string;
  description: string;
  severity: string;
  detection_method: string;
  status: string;
  confidence_score: number;
  source_ip: string | null;
  affected_endpoint: string;
  event_count: number;
  created_at: string;
}

export default function App() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [investigating, setInvestigating] = useState<string | null>(null);
  const [report, setReport] = useState<string | null>(null);

  useEffect(() => {
    fetchAnomalies();
  }, []);

  const fetchAnomalies = async () => {
    try {
      // Assuming Vite proxy or same domain
      const response = await axios.get('http://localhost:8000/api/v1/anomalies');
      setAnomalies(response.data.data || []);
    } catch (error) {
      console.error("Failed to fetch anomalies:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleInvestigate = async (id: string) => {
    setInvestigating(id);
    setReport(null);
    try {
      const response = await axios.post(`http://localhost:8000/api/v1/anomalies/${id}/investigate`);
      setReport(response.data.report);
    } catch (error) {
      console.error("Failed to investigate anomaly:", error);
      setReport("Error generating investigation report.");
    } finally {
      setInvestigating(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-8">
      <header className="mb-10 border-b border-gray-800 pb-6 flex items-center gap-4">
        <div className="p-3 bg-indigo-600/20 rounded-lg">
          <Activity className="w-8 h-8 text-indigo-400" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">AI Traffic Analysis Platform</h1>
          <p className="text-gray-400 mt-1">Real-time Anomaly Detection & LLM Investigation</p>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Anomalies List */}
        <section className="bg-gray-800/50 rounded-xl border border-gray-700/50 p-6 backdrop-blur-sm">
          <div className="flex items-center gap-2 mb-6">
            <ShieldAlert className="w-6 h-6 text-red-400" />
            <h2 className="text-xl font-semibold text-white">Detected Anomalies</h2>
          </div>
          
          {loading ? (
            <div className="animate-pulse flex flex-col gap-4">
              {[1, 2, 3].map(i => <div key={i} className="h-24 bg-gray-700/50 rounded-lg"></div>)}
            </div>
          ) : anomalies.length === 0 ? (
            <p className="text-gray-400 text-center py-8">No anomalies detected in the current window.</p>
          ) : (
            <div className="space-y-4 max-h-[700px] overflow-y-auto pr-2 custom-scrollbar">
              {anomalies.map((anomaly) => (
                <div key={anomaly.id} className="bg-gray-800 rounded-lg p-5 border border-gray-700 hover:border-gray-600 transition-colors">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-medium text-lg text-white">{anomaly.title}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium uppercase tracking-wider
                      ${anomaly.severity === 'critical' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 
                        anomaly.severity === 'high' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' : 
                        'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'}`}>
                      {anomaly.severity}
                    </span>
                  </div>
                  
                  <p className="text-gray-400 text-sm mb-4 leading-relaxed">{anomaly.description}</p>
                  
                  <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-700/50">
                    <div className="text-xs text-gray-500">
                      Method: <span className="text-gray-300 font-medium">{anomaly.detection_method}</span>
                      <span className="mx-2">•</span>
                      Score: <span className="text-gray-300 font-medium">{(anomaly.confidence_score * 100).toFixed(0)}%</span>
                    </div>
                    
                    <button 
                      onClick={() => handleInvestigate(anomaly.id)}
                      disabled={investigating === anomaly.id}
                      className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
                    >
                      {investigating === anomaly.id ? (
                        <><span className="animate-spin rounded-full h-4 w-4 border-2 border-white/20 border-t-white"></span> Investigating...</>
                      ) : (
                        'Generate Report'
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* LLM Investigation Panel */}
        <section className="bg-gray-800/50 rounded-xl border border-gray-700/50 p-6 backdrop-blur-sm flex flex-col h-full">
          <div className="flex items-center gap-2 mb-6">
            <FileText className="w-6 h-6 text-blue-400" />
            <h2 className="text-xl font-semibold text-white">LangChain Incident Report</h2>
          </div>
          
          <div className="flex-1 bg-gray-900 rounded-lg border border-gray-700 p-6 overflow-y-auto">
            {!report && !investigating ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-500">
                <FileText className="w-16 h-16 mb-4 opacity-20" />
                <p>Select an anomaly to generate an AI investigation report.</p>
              </div>
            ) : investigating ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-400 space-y-6">
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-indigo-500/20 rounded-full animate-pulse"></div>
                  <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin absolute top-0 left-0"></div>
                </div>
                <div className="text-center space-y-2">
                  <p className="text-lg font-medium text-white">AI Agent Investigating...</p>
                  <p className="text-sm">Analyzing behavioral signatures and heuristics.</p>
                </div>
              </div>
            ) : (
              <div className="prose prose-invert prose-blue max-w-none">
                <pre className="whitespace-pre-wrap font-sans text-gray-300 leading-relaxed bg-transparent p-0">
                  {report}
                </pre>
              </div>
            )}
          </div>
        </section>

      </main>
    </div>
  );
}
