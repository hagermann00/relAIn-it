import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";

// relAIn-it: App.tsx - The Stealth Rail UI
// Role: Clerk (Interface Management)

function App() {
  const [width, setWidth] = useState(20);
  const [telemetry, setTelemetry] = useState({ cpu: 0, ram: 0 });
  const [isOpenClawActive, setIsOpenClawActive] = useState(false);

  // Listen for Rust Telemetry and OpenClaw Status
  useEffect(() => {
    const unlisten = listen("telemetry-update", (event: any) => {
      setTelemetry({ 
        cpu: event.payload.cpu_usage.toFixed(1), 
        ram: (event.payload.ram_usage / 1024 / 1024 / 1024).toFixed(1) // GB
      });
    });

    const unlistenClaw = listen("openclaw-status", (event: any) => {
      setIsOpenClawActive(event.payload.is_active);
    });

    return () => { 
      unlisten.then(f => f()); 
      unlistenClaw.then(f => f());
    };
  }, []);

  // Window Resize Logic (20px -> 100px -> 400px)
  const handleResize = (newWidth: number) => {
    setWidth(newWidth);
    invoke("set_rail_width", { width: newWidth });
  };

  return (
    <div 
      className={`h-screen bg-black/80 backdrop-blur-md text-white transition-all duration-300 border-l border-white/10 flex flex-col items-center py-4 overflow-hidden`}
      style={{ width: `${width}px` }}
      onClick={() => width === 20 && handleResize(100)}
      onDoubleClick={() => width === 100 && handleResize(400)}
      onContextMenu={(e) => { e.preventDefault(); handleResize(20); }} // Right-click to collapse
    >
      {/* 20px - THE STEALTH RAIL */}
      <div className="flex flex-col items-center gap-8 w-full">
        <div className="text-xs font-bold rotate-90 opacity-40 hover:opacity-100 transition-opacity cursor-pointer">
          relAIn-it
        </div>

        {/* SPARK-TELEM (Sparkline telemetry placeholders) */}
        <div className="flex flex-col gap-4 items-center">
          <div className="w-1 bg-white/10 h-12 rounded-full relative overflow-hidden">
            <div className="absolute bottom-0 left-0 w-full bg-blue-500 transition-all duration-500" style={{ height: `${telemetry.cpu}%` }} />
          </div>
          <div className="text-[8px] rotate-90 opacity-40">CPU</div>
        </div>
      </div>

      {/* 100px - THE DASHBOARD (revealed on click) */}
      {width >= 100 && (
        <div className="mt-12 flex flex-col items-center gap-8 w-full px-2 animate-in fade-in slide-in-from-right-4">
          <div className="text-center">
            <div className="text-[10px] opacity-40">BUDGET</div>
            <div className="text-sm font-mono text-green-400">$40.00</div>
          </div>
          
          <div className="text-center">
            <div className="text-[10px] opacity-40">MEMORY</div>
            <div className="text-sm font-mono">{telemetry.ram}G</div>
          </div>

          <button 
            className="w-12 h-12 rounded-full border border-white/20 flex items-center justify-center hover:bg-white/10 transition-colors"
            title="Dream Mode"
          >
            D
          </button>
        </div>
      )}

      {/* 400px - THE WORKBENCH (revealed on double-click) */}
      {width >= 400 && (
        <div className="mt-12 w-full px-6 flex flex-col gap-6 animate-in fade-in zoom-in-95">
          <h2 className="text-lg font-bold border-b border-white/10 pb-2">Active Mission</h2>
          
          <div className="bg-white/5 p-4 rounded-lg border border-white/10">
            <div className="text-xs opacity-40 mb-2">MICRO-PHASE</div>
            <div className="text-sm">Extraction: 9020 RAM Verification</div>
            <div className="w-full bg-white/10 h-1 mt-3 rounded-full overflow-hidden">
              <div className="bg-blue-500 h-full w-[65%]" />
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <div className="text-xs opacity-40">SUB-INPUT</div>
            <input 
              type="text" 
              placeholder="Inject command or tangent pulse..." 
              className="bg-black/50 border border-white/20 rounded p-2 text-sm focus:outline-none focus:border-blue-500 transition-colors"
              onKeyDown={(e) => e.key === 'Enter' && console.log("Pulse Sent")}
            />
          </div>

          <div className="mt-4 flex flex-col gap-2">
            <div className="text-xs opacity-40 uppercase tracking-widest">Stowage</div>
            <div className="text-[11px] bg-yellow-500/10 text-yellow-500/80 p-2 rounded border border-yellow-500/20 italic">
              "Leftover chassis gaming build potential"
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
