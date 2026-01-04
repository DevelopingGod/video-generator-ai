from manim import *
import json
import os

config.pixel_width = 1920
config.pixel_height = 1080
config.frame_height = 8.0
config.frame_width = 14.2
config.background_color = "#111111"

class DarkGrid(NumberPlane):
    def __init__(self):
        super().__init__(
            x_range=(-8, 8, 1), y_range=(-5, 5, 1),
            background_line_style={"stroke_color": "#444444", "stroke_width": 1, "stroke_opacity": 0.3},
            axis_config={"stroke_opacity": 0}
        )

class CleanNode(VGroup):
    def __init__(self, text, icon, color_hex):
        super().__init__()
        self.box = RoundedRectangle(
            corner_radius=0.4, height=3.5, width=3.5,
            fill_color="#1E1E1E", fill_opacity=1.0,
            stroke_color=color_hex, stroke_width=6
        )
        self.box.set_shadow(0.8)
        self.icon_mob = Text(icon, font_size=80).move_to(self.box.get_center() + UP*0.4)
        self.label = Paragraph(text, alignment="center", font="Arial", font_size=24, color=WHITE).next_to(self.icon_mob, DOWN, buff=0.3)
        if self.label.width > 3.2: self.label.scale_to_fit_width(3.2)
        self.add(self.box, self.icon_mob, self.label)
    def get_right(self): return self.box.get_right()
    def get_left(self): return self.box.get_left()

class ProArrow(Arrow):
    def __init__(self, start, end):
        super().__init__(start, end, color=GREY_A, stroke_width=5, buff=0.1, max_tip_length_to_length_ratio=0.15)

class PillPacket(VGroup):
    def __init__(self, label, color_hex):
        super().__init__()
        self.body = RoundedRectangle(corner_radius=0.3, height=0.6, width=1.4, fill_color=color_hex, fill_opacity=1, stroke_width=2, stroke_color=WHITE)
        self.body.set_shadow(0.5)
        self.text = Text(label, font="Arial", font_size=20, weight=BOLD, color=BLACK)
        if self.text.width > 1.2: self.text.scale_to_fit_width(1.2)
        self.text.move_to(self.body.get_center())
        self.add(self.body, self.text)
        self.set_z_index(10)

class SubtitleBar(VGroup):
    def __init__(self, text):
        super().__init__()
        self.bg = Rectangle(height=1.2, width=12, fill_color=BLACK, fill_opacity=0.8, stroke_width=0)
        self.text = Paragraph(text, font="Arial", font_size=32, color=WHITE, alignment="center")
        if self.text.width > 11: self.text.scale_to_fit_width(11)
        self.text.move_to(self.bg.get_center())
        self.add(self.bg, self.text)
        self.to_edge(DOWN, buff=0.5)

class GenScene(Scene):
    def construct(self):
        # 1. LOAD DATA
        if not os.path.exists("scene_data.json"): return
        with open("scene_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # 2. SETUP
        self.add_sound("narrator.mp3")
        total_duration = data["duration"]
        self.add(DarkGrid())

        # 3. SUBTITLES
        words = data["script"].split()
        mid = len(words) // 2
        sub1_txt = " ".join(words[:mid]) + "..."
        sub2_txt = "..." + " ".join(words[mid:])
        
        subtitle = SubtitleBar(sub1_txt)
        self.add(subtitle)

        # 4. ACTORS
        left = CleanNode(data["left_text"], data["left_icon"], data["left_color"]).move_to(LEFT * 4)
        right = CleanNode(data["right_text"], data["right_icon"], data["right_color"]).move_to(RIGHT * 4)
        
        self.play(FadeIn(left, shift=UP, scale=0.5), FadeIn(right, shift=UP, scale=0.5), run_time=1.5)
        self.play(Indicate(left.box), Indicate(right.box), run_time=0.5)
        
        # 5. ARROWS
        start_top = left.get_right() + UP*0.4
        end_top = right.get_left() + UP*0.4
        start_bot = right.get_left() + DOWN*0.4
        end_bot = left.get_right() + DOWN*0.4
        
        arrow_to = ProArrow(start_top, end_top)
        arrow_fro = ProArrow(start_bot, end_bot)
        self.play(GrowArrow(arrow_to), GrowArrow(arrow_fro), run_time=1.0)

        # 6. CALCULATE TIMING
        setup_time = 3.0
        # Ensure we run until audio ends
        remaining_time = max(total_duration - setup_time - 1.0, 5.0) 
        phase_time = remaining_time / 2
        
        mode = data.get("animation_mode", "ping_pong")
        label_to = data.get("packet_label_to", "DAT")
        label_fro = data.get("packet_label_fro", "ACK")

        # --- PHASE 1 ---
        self.run_dynamic_loop(mode, phase_time, arrow_to, arrow_fro, data["packet_color"], label_to, label_fro)
        
        # --- SWAP SUBTITLE ---
        self.remove(subtitle)
        subtitle = SubtitleBar(sub2_txt)
        self.add(subtitle)
        
        # --- PHASE 2 ---
        self.run_dynamic_loop(mode, phase_time, arrow_to, arrow_fro, data["packet_color"], label_to, label_fro)

        self.wait(1)

    def run_dynamic_loop(self, mode, duration, arrow_to, arrow_fro, color_to, label_to, label_fro):
        """Runs animations until 'duration' time has passed"""
        start_time = self.renderer.time
        
        if mode == "ping_pong":
            # Keep ping-ponging until time is up
            while (self.renderer.time - start_time) < duration:
                # To
                p1 = PillPacket(label_to, color_to)
                self.play(MoveAlongPath(p1, arrow_to, rate_func=linear), run_time=0.8)
                self.remove(p1)
                
                # Check if time is up before starting return trip
                if (self.renderer.time - start_time) >= duration: break
                
                # Fro
                p2 = PillPacket(label_fro, "#00FFFF")
                self.play(MoveAlongPath(p2, arrow_fro, rate_func=linear), run_time=0.8)
                self.remove(p2)
                
        else: # Stream mode
            self.play(
                LaggedStart(
                    *[MoveAlongPath(PillPacket(label_to, color_to), arrow_to, run_time=1.5, rate_func=linear) for _ in range(4)],
                    lag_ratio=0.4
                ),
                run_time=duration
            )