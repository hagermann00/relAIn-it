// relAIn-it: main.rs - The Sovereign System Rail Core
// Role: Clerk & Bailiff (System Management)

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::sync::Mutex;
use std::time::Duration;
use tauri::{Emitter, Manager, WebviewWindow};
use sysinfo::System;
use serde::Serialize;
use tts::Tts;
use arboard::Clipboard;
use global_hotkey::{GlobalHotKeyManager, hotkey::{HotKey, Modifiers, Code}, GlobalHotKeyEvent};
use enigo::{Enigo, Key, Keyboard, Settings};

lazy_static::lazy_static! {
    static ref TTS_APP: Mutex<Option<Tts>> = Mutex::new(None);
}

#[derive(Clone, Serialize)]
struct Telemetry {
    cpu_usage: f32,
    ram_usage: u64,
    vram_usage: u64, // Placeholder for GPU bridge
}

// Commands for Window Resizing Logic
#[tauri::command]
async fn set_rail_width(window: WebviewWindow, width: f64) -> Result<(), String> {
    let mut size = window.outer_size().unwrap();
    size.width = (width * window.scale_factor().unwrap()) as u32;
    window.set_size(tauri::Size::Physical(size)).map_err(|e| e.to_string())
}

#[tauri::command]
fn play_tts(text: Option<String>) {
    if let Some(t) = text {
        if let Ok(mut tts) = TTS_APP.lock() {
            if let Some(ref mut engine) = *tts {
                let _ = engine.speak(t, true);
            }
        }
    }
}

#[tauri::command]
fn pause_tts() {
    if let Ok(mut tts) = TTS_APP.lock() {
        if let Some(ref mut engine) = *tts {
            let _ = engine.stop();
        }
    }
}

#[tauri::command]
fn stop_tts() {
    if let Ok(mut tts) = TTS_APP.lock() {
        if let Some(ref mut engine) = *tts {
            let _ = engine.stop();
        }
    }
}

#[tauri::command]
fn set_tts_speed(speed: f32) {
    if let Ok(mut tts) = TTS_APP.lock() {
        if let Some(ref mut engine) = *tts {
            let rate = match speed {
                s if s <= 0.5 => 0.5,
                s if s >= 2.0 => 2.0,
                _ => speed
            };
            let _ = engine.set_rate(rate);
        }
    }
}

#[tauri::command]
fn close_floating_player(app: tauri::AppHandle) {
    if let Some(window) = app.get_webview_window("floating-player") {
        let _ = window.close();
    }
    stop_tts();
}

#[tauri::command]
fn play_bailiff_chime() {
    println!("Bailiff: Tangent detected. Pulsing chime.");
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let window = app.get_webview_window("main").unwrap();

            // Apply Windows 11 Mica/Acrylic Effect
            #[cfg(target_os = "windows")]
            {
                use window_vibrancy::apply_mica;
                let _ = apply_mica(&window, None);
                window.set_always_on_top(true).unwrap();
                window.set_decorations(false).unwrap();
            }

            // Telemetry Loop (Node 1 Stats — 2s refresh)
            // NOTE: Sentinel V5 process-killing is handled externally by sentinel.js via PM2.
            let window_clone = window.clone();
            std::thread::spawn(move || {
                let mut sys = System::new_all();
                loop {
                    sys.refresh_all();

                    let stats = Telemetry {
                        cpu_usage: sys.global_cpu_info().cpu_usage(),
                        ram_usage: sys.used_memory(),
                        vram_usage: 0,
                    };

                    let _ = window_clone.emit("telemetry-update", stats);
                    std::thread::sleep(Duration::from_secs(2));
                }
            });

            // Initialize TTS
            if let Ok(tts) = Tts::default() {
                let _ = TTS_APP.lock().unwrap().insert(tts);
            }

            // Global Hotkey Thread for "Read Aloud" (Ctrl+Alt+R)
            let app_handle = app.handle().clone();
            std::thread::spawn(move || {
                let manager = GlobalHotKeyManager::new().unwrap();
                let hotkey = HotKey::new(Some(Modifiers::CONTROL | Modifiers::ALT), Code::KeyR);
                let _ = manager.register(hotkey);
                let receiver = GlobalHotKeyEvent::receiver();

                loop {
                    if let Ok(event) = receiver.recv() {
                        if event.id == hotkey.id() && event.state == global_hotkey::HotKeyState::Pressed {
                            // Simulate Ctrl+C to copy selected text
                            if let Ok(mut enigo) = Enigo::new(&Settings::default()) {
                                let _ = enigo.key(Key::Control, enigo::Direction::Press);
                                let _ = enigo.key(Key::Unicode('c'), enigo::Direction::Click);
                                let _ = enigo.key(Key::Control, enigo::Direction::Release);
                            }

                            std::thread::sleep(Duration::from_millis(150));

                            if let Ok(mut clipboard) = Clipboard::new() {
                                if let Ok(text) = clipboard.get_text() {
                                    let app_h = app_handle.clone();
                                    tauri::async_runtime::spawn(async move {
                                        if let Some(w) = app_h.get_webview_window("floating-player") {
                                            let _ = w.set_focus();
                                            let _ = w.emit("update-tts-text", text.clone());
                                            if let Ok(mut tts_lk) = TTS_APP.lock() {
                                                if let Some(ref mut engine) = *tts_lk {
                                                    let _ = engine.speak(text, true);
                                                }
                                            }
                                        } else {
                                            // Spawn the floating player window (Tauri 2 API)
                                            let result = tauri::WebviewWindowBuilder::new(
                                                &app_h,
                                                "floating-player",
                                                tauri::WebviewUrl::App("index.html?floating-player=true".into())
                                            )
                                            .title("Floating Player")
                                            .inner_size(300.0, 150.0)
                                            .decorations(false)
                                            .transparent(true)
                                            .always_on_top(true)
                                            .build();

                                            if let Ok(w) = result {
                                                std::thread::sleep(Duration::from_millis(500));
                                                let _ = w.emit("update-tts-text", text.clone());
                                                if let Ok(mut tts_lk) = TTS_APP.lock() {
                                                    if let Some(ref mut engine) = *tts_lk {
                                                        let _ = engine.speak(text, true);
                                                    }
                                                }
                                            }
                                        }
                                    });
                                }
                            }
                        }
                    }
                }
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            set_rail_width,
            play_bailiff_chime,
            play_tts,
            pause_tts,
            stop_tts,
            set_tts_speed,
            close_floating_player
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
