// relAIn-it: main.rs - The Sovereign System Rail Core
// Role: Clerk & Bailiff (System Management)

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::sync::{Arc, Mutex};
use std::time::Duration;
use tauri::{Manager, Runtime, Window};
use window_vibrancy::{apply_blur, apply_vibrancy, NSVisualEffectMaterial};
use sysinfo::{CpuExt, System, SystemExt};
use serde::Serialize;

#[derive(Clone, Serialize)]
struct Telemetry {
    cpu_usage: f32,
    ram_usage: u64,
    vram_usage: u64, // Placeholder for GPU bridge
}

// Commands for Window Resizing Logic
#[tauri::command]
async fn set_rail_width(window: Window, width: f64) -> Result<(), String> {
    let mut size = window.outer_size().unwrap();
    size.width = (width * window.scale_factor().unwrap()) as u32;
    window.set_size(tauri::Size::Physical(size)).map_err(|e| e.to_string())
}

#[tauri::command]
fn play_bailiff_chime() {
    // Logic for rodio sound playback
    println!("Bailiff: Tangent detected. Pulsing chime.");
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let window = app.get_window("main").unwrap();

            // Apply Windows 11 Mica/Acrylic Effect
            #[cfg(target_os = "windows")]
            {
                use window_vibrancy::apply_mica;
                let _ = apply_mica(&window, None); // Mica is best for Win11
                window.set_always_on_top(true).unwrap();
                window.set_decorations(false).unwrap();
            }

            // Telemetry Loop (Node 1 Stats)
            let window_clone = window.clone();
            std::thread::spawn(move || {
                let mut sys = System::new_all();
                loop {
                    sys.refresh_all();
                    let stats = Telemetry {
                        cpu_usage: sys.global_cpu_info().cpu_usage(),
                        ram_usage: sys.used_memory(),
                        vram_usage: 0, // Requires GPU-specific crate or bridge
                    };
                    
                    window_clone.emit("telemetry-update", stats).unwrap();
                    std::thread::sleep(Duration::from_secs(2));
                }
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![set_rail_width, play_bailiff_chime])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
