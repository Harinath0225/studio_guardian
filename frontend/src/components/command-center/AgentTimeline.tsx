import React from 'react';
import { GlassCard } from '../common/GlassCard';
import { StatusBadge } from '../common/StatusBadge';
import { Bot, CheckCircle, Clock, ShieldAlert, Cpu } from 'lucide-react';

interface AgentTimelineProps {
  currentState: string;
  timelineEvents: any[];
}

interface SpecialistAgentInfo {
  name: string;
  role: string;
  triggerStates: string[];
  icon: React.ReactNode;
}

const SPECIALIST_AGENTS: SpecialistAgentInfo[] = [
  {
    name: 'Incident Commander',
    role: 'Supervisor Orchestrator',
    triggerStates: ['TRIGGERED', 'INVESTIGATING', 'CORRELATING', 'ASSESSING_IMPACT', 'EVALUATING_POLICY', 'REMEDIATING', 'VERIFYING', 'RESOLVED', 'ESCALATED_HUMAN_TAKEOVER'],
    icon: <Bot className="h-4 w-4 text-blue-400" />
  },
  {
    name: 'Observability Investigator',
    role: 'Grafana MCP Multi-Signal Correlation',
    triggerStates: ['INVESTIGATING', 'CORRELATING'],
    icon: <Cpu className="h-4 w-4 text-cyan-400" />
  },
  {
    name: 'Business Impact Agent',
    role: 'Audience & Ad Burn Calculations',
    triggerStates: ['ASSESSING_IMPACT'],
    icon: <Clock className="h-4 w-4 text-amber-400" />
  },
  {
    name: 'Safety Director',
    role: 'Deterministic Policy Engine',
    triggerStates: ['EVALUATING_POLICY', 'WAITING_HUMAN_APPROVAL'],
    icon: <ShieldAlert className="h-4 w-4 text-purple-400" />
  },
  {
    name: 'Remediation Agent',
    role: 'Controlled Video Proxy Shifting',
    triggerStates: ['REMEDIATING'],
    icon: <CheckCircle className="h-4 w-4 text-emerald-400" />
  },
  {
    name: 'Verification Agent',
    role: 'Independent Telemetry Verdict',
    triggerStates: ['VERIFYING'],
    icon: <CheckCircle className="h-4 w-4 text-teal-400" />
  }
];

export const AgentTimeline: React.FC<AgentTimelineProps> = ({ currentState, timelineEvents }) => {
  return (
    <GlassCard title="Specialist Agent Hierarchy & Live Timeline">
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 mb-4">
        {SPECIALIST_AGENTS.map((agent) => {
          const isActive = agent.triggerStates.includes(currentState);
          return (
            <div
              key={agent.name}
              className={`p-2.5 rounded-lg border transition-all ${
                isActive
                  ? 'bg-blue-500/10 border-blue-500/40 shadow-lg shadow-blue-500/10'
                  : 'bg-white/5 border-white/5 opacity-60'
              }`}
            >
              <div className="flex items-center gap-1.5 mb-1">
                {agent.icon}
                <span className="text-[11px] font-bold font-mono text-gray-200 truncate">{agent.name}</span>
              </div>
              <p className="text-[9px] text-gray-400 leading-tight line-clamp-2">{agent.role}</p>
              <div className="mt-2 flex items-center justify-between">
                <span className={`text-[9px] font-mono uppercase ${isActive ? 'text-blue-400 font-semibold' : 'text-gray-500'}`}>
                  {isActive ? 'ACTIVE' : 'IDLE'}
                </span>
                {isActive && <span className="h-1.5 w-1.5 rounded-full bg-blue-400 animate-ping" />}
              </div>
            </div>
          );
        })}
      </div>

      <div className="border-t border-white/5 pt-3">
        <h4 className="text-[11px] font-mono text-gray-400 uppercase tracking-wider mb-2">Live Orchestration Audit Log</h4>
        <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
          {timelineEvents.length === 0 ? (
            <p className="text-xs text-gray-500 font-mono italic">Waiting for incident trigger event...</p>
          ) : (
            timelineEvents.map((evt, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs font-mono py-1 px-2 rounded bg-black/20 border border-white/5">
                <div className="flex items-center gap-2">
                  <span className="text-gray-500">[{new Date(evt.timestamp * 1000).toLocaleTimeString()}]</span>
                  <span className="text-gray-300">Transition:</span>
                  <span className="text-cyan-400">{evt.from}</span>
                  <span className="text-gray-500">→</span>
                  <span className="text-emerald-400 font-semibold">{evt.to}</span>
                </div>
                <StatusBadge status={evt.to} size="sm" />
              </div>
            ))
          )}
        </div>
      </div>
    </GlassCard>
  );
};
