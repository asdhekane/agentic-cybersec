import React, { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';

const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';


const FeedItem = ({ message }) => (
  <div className="text-sm text-green-400 font-mono border-b border-gray-700 py-1 px-2 hover:bg-gray-800 transition">
    {message}
  </div>
);

const LogEntry = ({ log, index }) => {
  const [isOpen, setIsOpen] = useState(false);
  const timestamp = new Date(log.timestamp * 1000).toLocaleString();

  return (
    <div className="bg-gray-850 rounded-lg mb-3 border border-gray-700">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full text-left px-4 py-3 flex justify-between items-center hover:bg-gray-800 transition"
      >
        <div className="flex items-center space-x-4">
          <span className="font-mono bg-gray-700 text-gray-300 text-xs px-2 py-1 rounded">{index}</span>
          <span className="font-semibold text-white">{log.threat_type}</span>
          <span className="text-sm text-gray-400">{log.action_taken}</span>
        </div>
        <span className="text-sm text-gray-500">{timestamp}</span>
      </button>
      {isOpen && (
        <div className="p-4 bg-gray-900 rounded-b-lg border-t border-gray-700">
          <pre className="text-xs text-white whitespace-pre-wrap">
            {JSON.stringify(log, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default function App() {
  const [latestStatus, setLatestStatus] = useState(null);
  const [actionLog, setActionLog] = useState([]);
  const [liveFeed, setLiveFeed] = useState([]);
  const feedEndRef = useRef(null);

  useEffect(() => {
    const socket = io(backendUrl);

    socket.on('initial_data', (data) => {
      setLiveFeed(data.live_feed || []);
      setActionLog(data.action_log || []);
      setLatestStatus(data.latest_status);
    });

    socket.on('new_feed_event', (event) => {
      setLiveFeed(prev => [...prev, event].slice(-100));
    });

    socket.on('new_action_log', (log) => {
      setActionLog(prev => [log, ...prev]);
      setLatestStatus(log);
    });

    return () => socket.disconnect();
  }, []);

  useEffect(() => {
    feedEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [liveFeed]);

  const simulateAttack = async (attackType) => {
    try {
      await fetch('http://localhost:5000/simulate_attack', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ attack_type: attackType }),
      });
    } catch (error) {
      console.error("Failed to simulate attack:", error);
    }
  };

  return (
    <div className="bg-gray-950 text-white min-h-screen font-sans p-4 sm:p-6 lg:p-10">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-extrabold tracking-tight text-blue-400">🛡️ Agentic AI Cybersecurity System</h1>
          <p className="text-gray-400 mt-2 text-lg">Real-time Autonomous Threat Detection & Response</p>
        </div>

        {/* Main Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Left Column */}
          <div className="flex flex-col gap-6">
            {/* Simulate Attack */}
            <div className="bg-gray-850 border border-gray-700 p-5 rounded-xl shadow-md">
              <h2 className="text-xl font-bold mb-4 text-white">⚔️ Simulate an Attack</h2>
              <div className="flex flex-col gap-3">
                <button
                  onClick={() => simulateAttack('port_scan')}
                  className="bg-blue-600 hover:bg-blue-700 font-bold py-2 px-4 rounded-md transition text-white"
                >
                  🔍 Port Scan
                </button>
                <button
                  onClick={() => simulateAttack('sql_injection')}
                  className="bg-yellow-600 hover:bg-yellow-700 font-bold py-2 px-4 rounded-md transition text-white"
                >
                  💉 SQL Injection
                </button>
                <button
                  onClick={() => simulateAttack('ddos')}
                  className="bg-red-600 hover:bg-red-700 font-bold py-2 px-4 rounded-md transition text-white"
                >
                  🌊 DDoS Attack
                </button>
              </div>
            </div>

            {/* Live Feed */}
            <div className="bg-gray-850 border border-gray-700 p-5 rounded-xl shadow-md flex-grow flex flex-col">
              <h2 className="text-xl font-bold mb-4 text-white">📡 Live Event Feed</h2>
              <div className="bg-black rounded-md p-2 h-96 overflow-y-auto">
                {liveFeed.map((msg, i) => <FeedItem key={i} message={msg} />)}
                <div ref={feedEndRef} />
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            {/* Latest Threat */}
            <div className="bg-gray-850 border border-gray-700 p-5 rounded-xl shadow-md">
              <h2 className="text-xl font-bold mb-4 text-white">🚨 Latest Threat Response</h2>
              {latestStatus && latestStatus.threat_type ? (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
                  <div>
                    <p className="text-sm text-gray-400">Threat Type</p>
                    <p className="text-2xl font-extrabold text-red-400">{latestStatus.threat_type}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Action Taken</p>
                    <p className="text-xl font-bold">{latestStatus.action_taken}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Effectiveness</p>
                    <p className="text-xl font-bold text-green-400">{latestStatus.effectiveness}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Time</p>
                    <p className="text-xl font-bold">{new Date(latestStatus.timestamp * 1000).toLocaleTimeString()}</p>
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-500 py-10">System is monitoring... No active threats.</div>
              )}
            </div>

            {/* Historical Logs */}
            <div className="bg-gray-850 border border-gray-700 p-5 rounded-xl shadow-md flex-grow">
              <h2 className="text-xl font-bold mb-4 text-white">📜 Historical Action Log</h2>
              <div className="h-[32rem] overflow-y-auto pr-2">
                {(actionLog || []).length > 0 ? (
                  actionLog.map((log, i) => (
                    <LogEntry key={log.timestamp} log={log} index={actionLog.length - i} />
                  ))
                ) : (
                  <div className="text-center text-gray-500 pt-16">No actions logged yet.</div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
