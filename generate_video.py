import os
import json
import subprocess
import asyncio
import edge_tts
from mutagen.mp3 import MP3
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY: raise ValueError("CRITICAL: GROQ_API_KEY missing!")

llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.3-70b-versatile", temperature=0.1)

async def generate_voice(text, filename="narrator.mp3"):
    print(f"   [Audio] Generating Narration...")
    # Slower rate (-15%) = Longer video + Clearer voice
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural", rate="-15%")
    await communicate.save(filename)
    return MP3(filename).info.length

def get_video_plan(topic):
    print(f"\n--- 1. Planning Video for: {topic} ---")
    prompt = f"""
    You are a Technical Director. Plan a 30-second animation.
    
    TOPIC: "{topic}"
    
    INSTRUCTIONS:
    1. Script: Write a DETAILED 6-sentence technical script (approx 90-110 words). 
       - It MUST take 30 seconds to read. Do not write short summaries.
    2. Actors: Identify Source (Left) and Destination (Right).
    3. Logic: 
       - If "Request-Response" (Client-Server), use mode: "ping_pong".
       - If "Continuous" (Streaming/Nature), use mode: "stream".
    4. Labels: VERY SHORT labels (Max 4 chars) for bubbles (e.g. "REQ", "RES", "ACK", "DATA").
    
    OUTPUT JSON ONLY:
    {{
      "script": "Full script text here...",
      "left_text": "Name (e.g. Client)",
      "left_icon": "Emoji (e.g. 💻)",
      "left_color": "#33C4FF",
      "right_text": "Name (e.g. Server)",
      "right_icon": "Emoji (e.g. 🗄️)",
      "right_color": "#33FF57",
      "packet_color": "#FFFF00",
      "animation_mode": "ping_pong", 
      "packet_label_to": "REQ",
      "packet_label_fro": "RES"
    }}
    """
    res = llm.invoke(prompt)
    content = res.content.strip()
    if "```json" in content: content = content.split("```json")[1].split("```")[0].strip()
    elif "{" in content: content = content[content.find("{"):content.rfind("}")+1]
        
    try: return json.loads(content)
    except: return {"script": "Error parsing.", "animation_mode": "ping_pong"}

def main():
    topic = input("Enter Topic (e.g. Explain Client Server Architecture): ")
    
    data = get_video_plan(topic)
    
    # Force long duration check
    duration = asyncio.run(generate_voice(data['script']))
    data["duration"] = duration
    print(f"   [Sync] Duration: {duration:.2f}s | Mode: {data.get('animation_mode')}")
    
    with open("scene_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    print("\n--- Rendering Video (1080p) ---")
    subprocess.run("manim -p -ql render_engine.py GenScene", shell=True)

if __name__ == "__main__":
    main()