import React from 'react';
import { ShieldAlert } from 'lucide-react';

interface Props {
  compact?: boolean;
}

export const ScientificDisclaimer: React.FC<Props> = ({ compact = false }) => {
  return (
    <div className={`rounded-xl border border-honey-500/30 bg-honey-500/5 ${compact ? 'p-3' : 'p-4'}`}>
      <div className="flex items-start space-x-3">
        <ShieldAlert className="w-5 h-5 text-honey-400 flex-shrink-0 mt-0.5" />
        <div className="text-xs leading-relaxed text-charcoal-300">
          <span className="font-semibold text-honey-400 mr-1.5 uppercase tracking-wide">
            Scientific Limitation Notice:
          </span>
          HoneyBoo detects and counts honeybee entrance movements using computer vision counters.
          Detected traffic fluctuations and statistical anomaly alerts represent behavioral observations,
          <strong> not medical diagnoses, colony disease determinations, or comprehensive colony health assessments</strong>.
          Entrance traffic data should be combined with physical internal hive inspections by qualified beekeepers.
        </div>
      </div>
    </div>
  );
};
