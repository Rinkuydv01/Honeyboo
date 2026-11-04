import React, { useRef, useEffect, useState, useCallback } from 'react';
import { LineConfig } from '../types';
import { Compass, RotateCw } from 'lucide-react';

interface Props {
  previewUrl?: string;
  lineConfig: LineConfig;
  onChange: (config: LineConfig) => void;
  width?: number;
  height?: number;
}

export const EntranceLineCanvas: React.FC<Props> = ({
  previewUrl,
  lineConfig,
  onChange,
  width = 720,
  height = 405
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [draggingPoint, setDraggingPoint] = useState<'p1' | 'p2' | null>(null);
  const [imageLoaded, setImageLoaded] = useState(false);
  const imgRef = useRef<HTMLImageElement | null>(null);

  // Load preview image
  useEffect(() => {
    if (!previewUrl) return;
    const img = new Image();
    img.src = previewUrl;
    img.onload = () => {
      imgRef.current = img;
      setImageLoaded(true);
    };
  }, [previewUrl]);

  // Draw line, endpoints, and normal vector indicating inside/outside
  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw background image if available, else dark textured background
    if (imgRef.current && imageLoaded) {
      ctx.drawImage(imgRef.current, 0, 0, canvas.width, canvas.height);
    } else {
      ctx.fillStyle = '#1b1f24';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#495057';
      ctx.font = '14px Plus Jakarta Sans';
      ctx.textAlign = 'center';
      ctx.fillText('Video Preview Not Loaded (Drag handles to set coordinates)', canvas.width / 2, canvas.height / 2);
    }

    const p1x = lineConfig.p1[0] * canvas.width;
    const p1y = lineConfig.p1[1] * canvas.height;
    const p2x = lineConfig.p2[0] * canvas.width;
    const p2y = lineConfig.p2[1] * canvas.height;

    // 1. Draw virtual entrance line
    ctx.beginPath();
    ctx.moveTo(p1x, p1y);
    ctx.lineTo(p2x, p2y);
    ctx.strokeStyle = '#f59e0b'; // Amber-500
    ctx.lineWidth = 4;
    ctx.shadowColor = 'rgba(245, 158, 11, 0.6)';
    ctx.shadowBlur = 8;
    ctx.stroke();
    ctx.shadowBlur = 0;

    // 2. Draw Inside / Outside direction arrow
    const midX = (p1x + p2x) / 2;
    const midY = (p1y + p2y) / 2;

    let arrowDx = 0;
    let arrowDy = 0;
    const arrowLen = 45;

    if (lineConfig.inside_direction === 'bottom') arrowDy = arrowLen;
    else if (lineConfig.inside_direction === 'top') arrowDy = -arrowLen;
    else if (lineConfig.inside_direction === 'right') arrowDx = arrowLen;
    else if (lineConfig.inside_direction === 'left') arrowDx = -arrowLen;

    ctx.beginPath();
    ctx.moveTo(midX, midY);
    ctx.lineTo(midX + arrowDx, midY + arrowDy);
    ctx.strokeStyle = '#10b981'; // Emerald
    ctx.lineWidth = 3;
    ctx.stroke();

    // Arrowhead
    const angle = Math.atan2(arrowDy, arrowDx);
    ctx.beginPath();
    ctx.moveTo(midX + arrowDx, midY + arrowDy);
    ctx.lineTo(
      midX + arrowDx - 12 * Math.cos(angle - Math.PI / 6),
      midY + arrowDy - 12 * Math.sin(angle - Math.PI / 6)
    );
    ctx.lineTo(
      midX + arrowDx - 12 * Math.cos(angle + Math.PI / 6),
      midY + arrowDy - 12 * Math.sin(angle + Math.PI / 6)
    );
    ctx.fillStyle = '#10b981';
    ctx.fill();

    // Labels
    ctx.font = 'bold 12px JetBrains Mono, monospace';
    ctx.fillStyle = '#10b981';
    ctx.fillText('INSIDE (HIVE)', midX + arrowDx + 10, midY + arrowDy + 5);

    ctx.fillStyle = '#f97316';
    ctx.fillText('OUTSIDE (FORAGING)', midX - arrowDx - 10, midY - arrowDy - 5);

    // 3. Draw Endpoint handles
    const drawHandle = (x: number, y: number, label: string, isDragging: boolean) => {
      ctx.beginPath();
      ctx.arc(x, y, isDragging ? 12 : 9, 0, Math.PI * 2);
      ctx.fillStyle = isDragging ? '#fbbf24' : '#f59e0b';
      ctx.fill();
      ctx.lineWidth = 3;
      ctx.strokeStyle = '#ffffff';
      ctx.stroke();

      ctx.font = 'bold 11px JetBrains Mono';
      ctx.fillStyle = '#ffffff';
      ctx.fillText(label, x - 7, y - 14);
    };

    drawHandle(p1x, p1y, 'P1', draggingPoint === 'p1');
    drawHandle(p2x, p2y, 'P2', draggingPoint === 'p2');
  }, [lineConfig, draggingPoint, imageLoaded]);

  useEffect(() => {
    draw();
  }, [draw]);

  // Mouse interaction for moving endpoints
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const p1x = lineConfig.p1[0] * canvas.width;
    const p1y = lineConfig.p1[1] * canvas.height;
    const p2x = lineConfig.p2[0] * canvas.width;
    const p2y = lineConfig.p2[1] * canvas.height;

    const distP1 = Math.hypot(mouseX - p1x, mouseY - p1y);
    const distP2 = Math.hypot(mouseX - p2x, mouseY - p2y);

    if (distP1 < 25) {
      setDraggingPoint('p1');
    } else if (distP2 < 25) {
      setDraggingPoint('p2');
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!draggingPoint) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();

    const mouseX = Math.max(0, Math.min(canvas.width, e.clientX - rect.left));
    const mouseY = Math.max(0, Math.min(canvas.height, e.clientY - rect.top));

    const normX = Math.round((mouseX / canvas.width) * 100) / 100;
    const normY = Math.round((mouseY / canvas.height) * 100) / 100;

    if (draggingPoint === 'p1') {
      onChange({
        ...lineConfig,
        p1: [normX, normY]
      });
    } else if (draggingPoint === 'p2') {
      onChange({
        ...lineConfig,
        p2: [normX, normY]
      });
    }
  };

  const handleMouseUp = () => {
    setDraggingPoint(null);
  };

  // Preset Configurations
  const applyPreset = (preset: 'horizontal_bottom' | 'horizontal_center' | 'vertical_right') => {
    if (preset === 'horizontal_bottom') {
      onChange({
        p1: [0.05, 0.75],
        p2: [0.95, 0.75],
        inside_direction: 'bottom'
      });
    } else if (preset === 'horizontal_center') {
      onChange({
        p1: [0.1, 0.5],
        p2: [0.9, 0.5],
        inside_direction: 'bottom'
      });
    } else if (preset === 'vertical_right') {
      onChange({
        p1: [0.65, 0.1],
        p2: [0.65, 0.9],
        inside_direction: 'right'
      });
    }
  };

  return (
    <div className="space-y-4">
      {/* Canvas container */}
      <div className="relative rounded-2xl overflow-hidden border border-charcoal-700 bg-charcoal-900 shadow-2xl flex justify-center items-center">
        <canvas
          ref={canvasRef}
          width={width}
          height={height}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          className="cursor-crosshair max-w-full h-auto"
        />
        <div className="absolute top-3 left-3 bg-charcoal-900/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-charcoal-700 text-xs font-mono text-charcoal-300">
          Line: P1 ({lineConfig.p1[0]}, {lineConfig.p1[1]}) → P2 ({lineConfig.p2[0]}, {lineConfig.p2[1]})
        </div>
      </div>

      {/* Configuration Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Inside Side Selector */}
        <div className="p-4 rounded-xl bg-charcoal-900/90 border border-charcoal-800 space-y-2">
          <label className="text-xs font-semibold uppercase tracking-wider text-charcoal-400 flex items-center space-x-1.5">
            <Compass className="w-4 h-4 text-honey-400" />
            <span>Hive Interior (Inside Side)</span>
          </label>
          <div className="grid grid-cols-4 gap-2">
            {(['bottom', 'top', 'left', 'right'] as const).map((dir) => (
              <button
                key={dir}
                type="button"
                onClick={() => onChange({ ...lineConfig, inside_direction: dir })}
                className={`py-2 px-3 text-xs font-semibold rounded-lg capitalize border transition-all ${
                  lineConfig.inside_direction === dir
                    ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50 shadow-sm'
                    : 'bg-charcoal-800 text-charcoal-300 border-charcoal-700 hover:bg-charcoal-700'
                }`}
              >
                {dir}
              </button>
            ))}
          </div>
          <p className="text-[11px] text-charcoal-400">
            Green arrow points to the inside of the beehive. Crossing from outside to inside counts as INCOMING.
          </p>
        </div>

        {/* Quick Presets */}
        <div className="p-4 rounded-xl bg-charcoal-900/90 border border-charcoal-800 space-y-2">
          <label className="text-xs font-semibold uppercase tracking-wider text-charcoal-400 flex items-center space-x-1.5">
            <RotateCw className="w-4 h-4 text-honey-400" />
            <span>Quick Presets</span>
          </label>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => applyPreset('horizontal_bottom')}
              className="py-2 px-2 text-xs font-medium rounded-lg bg-charcoal-800 text-charcoal-300 border border-charcoal-700 hover:border-honey-500/50 hover:text-white"
            >
              Bottom Slot
            </button>
            <button
              type="button"
              onClick={() => applyPreset('horizontal_center')}
              className="py-2 px-2 text-xs font-medium rounded-lg bg-charcoal-800 text-charcoal-300 border border-charcoal-700 hover:border-honey-500/50 hover:text-white"
            >
              Center Line
            </button>
            <button
              type="button"
              onClick={() => applyPreset('vertical_right')}
              className="py-2 px-2 text-xs font-medium rounded-lg bg-charcoal-800 text-charcoal-300 border border-charcoal-700 hover:border-honey-500/50 hover:text-white"
            >
              Right Entrance
            </button>
          </div>
          <p className="text-[11px] text-charcoal-400">
            Click and drag amber circles P1 and P2 on the video canvas to adjust the angle to your hive entrance.
          </p>
        </div>
      </div>
    </div>
  );
};
