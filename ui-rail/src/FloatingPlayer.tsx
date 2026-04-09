import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";

export default function FloatingPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1.0);
  const [text, setText] = useState("Loading text...");

  useEffect(() => {
    // Listen for text update from backend
    const unlisten = listen("update-tts-text", (event: any) => {
      setText(event.payload);
      setIsPlaying(true);
    });

    return () => {
      unlisten.then(f => f());
    };
  }, []);

  const handlePlayPause = () => {
    if (isPlaying) {
      invoke("pause_tts");
      setIsPlaying(false);
    } else {
      invoke("play_tts");
      setIsPlaying(true);
    }
  };

  const handleStop = () => {
    invoke("stop_tts");
    setIsPlaying(false);
    // Optionally close the window, or just leave it floating
  };

  const handleSpeed = () => {
    const nextSpeed = speed === 1.0 ? 1.5 : speed === 1.5 ? 2.0 : speed === 2.0 ? 0.5 : 1.0;
    setSpeed(nextSpeed);
    invoke("set_tts_speed", { speed: nextSpeed });
  };

  const handleClose = () => {
    invoke("close_floating_player");
  };

  return (
    <div 
      className="w-full h-screen bg-black/90 backdrop-blur-xl border border-white/20 rounded-xl flex flex-col p-4 text-white hover:border-white/40 transition-colors shadow-2xl relative"
      data-tauri-drag-region
    >
      <div className="absolute top-2 right-2 flex gap-2">
        <button onClick={handleClose} className="w-5 h-5 rounded-full bg-red-500/20 hover:bg-red-500/50 flex items-center justify-center text-[10px]">✕</button>
      </div>
      
      <div className="flex-1 flex flex-col justify-center gap-4 mt-2" data-tauri-drag-region>
        <div className="text-xs text-white/50 bg-white/5 p-2 rounded max-h-16 overflow-hidden text-ellipsis pointer-events-none">
          {text}
        </div>
        
        <div className="flex items-center justify-between mt-2">
          <button 
            onClick={handlePlayPause}
            className="w-10 h-10 rounded-full bg-blue-500/20 hover:bg-blue-500/40 border border-blue-500/50 flex items-center justify-center transition-all"
          >
            {isPlaying ? "⏸" : "▶"}
          </button>
          
          <button 
            onClick={handleStop}
            className="w-10 h-10 rounded-full bg-red-500/20 hover:bg-red-500/40 border border-red-500/50 flex items-center justify-center transition-all"
          >
            ⏹
          </button>
          
          <button 
            onClick={handleSpeed}
            className="h-8 px-3 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 flex items-center justify-center text-xs font-mono transition-all"
          >
            {speed}x
          </button>
        </div>
      </div>
    </div>
  );
}
