# AI Video Synthesis System (Manim + Edge-TTS)

This system is a hybrid engine designed to transform technical topics into high-quality, bi-directional animated explainer videos. It mimics professional system design visualization styles (like "ByteMonk").

## 🛠️ System Architecture
1. **Planning (LLM):** Uses Llama 3.3 70B via Groq to analyze the topic and generate a 30s+ technical script and visual blueprint.
2. **Narration (Neural TTS):** Converts the script into a professional male voice using `edge-tts` with a -15% speed rate for clarity.
3. **Synthesis ffmpeg (Manim):** A robust Python engine reads the AI-generated JSON and renders a 1080p MP4.

## 🚀 Key Features
- **Bi-Directional Traffic:** Visualizes "Ping-Pong" (Request-Response) cycles or continuous streams.
- **Pill-Packet Animation:** Data packets are rendered as labeled pills (e.g., REQ, RES) for technical accuracy.
- **Auto-Sync Subtitles:** Text overlays are automatically split and synchronized with the audio duration.
- **Aesthetic Design:** Dark-mode grid with glassmorphism cards and smooth pop-in animations.

## 🏃 Setup & Execution
1. **Environment:** Add your `GROQ_API_KEY` to a `.env` file.
2. **Install Deps:** `pip install manim langchain-groq edge-tts mutagen python-dotenv`
3. **Run:** `python generate_video.py`
