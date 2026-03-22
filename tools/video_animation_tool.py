"""Video Animation Tool — generate animated consulting deliverables.

Use cases:
  • Animated ERP transformation roadmaps (timeline fly-in)
  • Financial KPI dashboards with live chart animations
  • Process flow animations (R2R, O2C, P2P swim lanes)
  • EPM waterfall chart animations (budget vs actual)
  • Executive summary animations for client presentations

Engines supported:
  1. Matplotlib (built-in, no API key) — charts, timelines, flows
  2. Luma AI Dream Machine (requires LUMA_AI_KEY) — photorealistic videos
  3. Custom frame-by-frame rendering using Pillow + imageio
"""

from __future__ import annotations

import io
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class VideoResult:
    path: str
    duration_seconds: float
    fps: int
    resolution: tuple[int, int]
    format: str
    engine: str


class VideoAnimationTool:
    """Generate animated video deliverables for ERP/EPM consulting."""

    def __init__(
        self,
        output_dir: str = "./output/videos",
        default_fps: int = 30,
        default_resolution: tuple[int, int] = (1920, 1080),
        luma_api_key: str | None = None,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.fps = default_fps
        self.resolution = default_resolution
        self.luma_key = luma_api_key or os.environ.get("LUMA_AI_KEY", "")

    # ─── Public API ───────────────────────────────────────────────────────────

    def animate_erp_roadmap(
        self,
        project_name: str,
        phases: list[dict],
        output_filename: str | None = None,
        duration: float = 30.0,
    ) -> VideoResult:
        """Animate an ERP transformation roadmap as a Gantt-style timeline video."""
        fname = output_filename or f"{project_name.lower().replace(' ', '_')}_roadmap.mp4"
        out_path = str(self.output_dir / fname)
        return self._render_gantt_animation(
            title=f"{project_name} — ERP Transformation Roadmap",
            phases=phases,
            out_path=out_path,
            duration=duration,
        )

    def animate_kpi_dashboard(
        self,
        kpis: list[dict],
        title: str = "CFO Dashboard",
        output_filename: str | None = None,
        duration: float = 20.0,
    ) -> VideoResult:
        """Animate a CFO KPI dashboard with bar/line chart fly-ins."""
        fname = output_filename or "cfo_dashboard.mp4"
        out_path = str(self.output_dir / fname)
        return self._render_kpi_animation(
            title=title,
            kpis=kpis,
            out_path=out_path,
            duration=duration,
        )

    def animate_process_flow(
        self,
        process_name: str,
        steps: list[dict],
        output_filename: str | None = None,
        duration: float = 25.0,
    ) -> VideoResult:
        """Animate a finance process flow (R2R, O2C, P2P) with step-by-step reveal."""
        fname = output_filename or f"{process_name.lower().replace(' ', '_')}_flow.mp4"
        out_path = str(self.output_dir / fname)
        return self._render_process_animation(
            title=f"{process_name} Process Flow",
            steps=steps,
            out_path=out_path,
            duration=duration,
        )

    def animate_waterfall_chart(
        self,
        title: str,
        data: dict,
        output_filename: str | None = None,
        duration: float = 15.0,
    ) -> VideoResult:
        """Animate a budget vs actual waterfall chart (EPM variance analysis)."""
        fname = output_filename or "waterfall_analysis.mp4"
        out_path = str(self.output_dir / fname)
        return self._render_waterfall_animation(
            title=title,
            data=data,
            out_path=out_path,
            duration=duration,
        )

    def generate_luma_video(
        self,
        prompt: str,
        output_filename: str | None = None,
        duration: float = 5.0,
    ) -> VideoResult:
        """Generate a photorealistic video using Luma AI Dream Machine API."""
        if not self.luma_key:
            return self._fallback_text_animation(prompt, output_filename)

        try:
            import httpx

            resp = httpx.post(
                "https://api.lumalabs.ai/dream-machine/v1/generations",
                headers={"Authorization": f"Bearer {self.luma_key}"},
                json={"prompt": prompt, "duration": int(duration), "aspect_ratio": "16:9"},
                timeout=30,
            )
            resp.raise_for_status()
            gen_id = resp.json().get("id")

            # Poll for completion
            import time

            for _ in range(60):
                poll = httpx.get(
                    f"https://api.lumalabs.ai/dream-machine/v1/generations/{gen_id}",
                    headers={"Authorization": f"Bearer {self.luma_key}"},
                )
                data = poll.json()
                if data.get("state") == "completed":
                    video_url = data["assets"]["video"]
                    fname = output_filename or f"luma_{gen_id[:8]}.mp4"
                    out_path = str(self.output_dir / fname)
                    video_bytes = httpx.get(video_url).content
                    with open(out_path, "wb") as f:
                        f.write(video_bytes)
                    return VideoResult(
                        path=out_path,
                        duration_seconds=duration,
                        fps=24,
                        resolution=(1920, 1080),
                        format="mp4",
                        engine="luma_ai",
                    )
                time.sleep(2)
        except Exception:
            pass

        return self._fallback_text_animation(prompt, output_filename)

    # ─── Matplotlib Renderers ─────────────────────────────────────────────────

    def _render_gantt_animation(
        self,
        title: str,
        phases: list[dict],
        out_path: str,
        duration: float,
    ) -> VideoResult:
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            import matplotlib.animation as animation
            import numpy as np

            fig, ax = plt.subplots(figsize=(16, 9), facecolor="#0d1b2a")
            ax.set_facecolor("#0d1b2a")
            fig.patch.set_facecolor("#0d1b2a")

            colors = ["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6", "#1abc9c"]
            total_frames = int(self.fps * duration)
            frames_per_phase = total_frames // max(len(phases), 1)

            bars: list[mpatches.FancyBboxPatch] = []
            labels: list[Any] = []

            def init():
                ax.clear()
                ax.set_facecolor("#0d1b2a")
                ax.set_title(title, color="white", fontsize=18, fontweight="bold", pad=20)
                ax.set_xlabel("Week", color="#aaaaaa", fontsize=12)
                ax.set_ylabel("Phase", color="#aaaaaa", fontsize=12)
                ax.tick_params(colors="#aaaaaa")
                ax.spines[:].set_color("#333333")
                return []

            def animate(frame: int):
                ax.clear()
                ax.set_facecolor("#0d1b2a")
                ax.set_title(title, color="white", fontsize=18, fontweight="bold", pad=20)
                phase_idx = min(frame // frames_per_phase, len(phases) - 1)
                progress = (frame % frames_per_phase) / frames_per_phase

                for i, phase in enumerate(phases[: phase_idx + 1]):
                    start = phase.get("start_week", i)
                    end = phase.get("end_week", start + 2)
                    width = (end - start) * (progress if i == phase_idx else 1.0)
                    bar = ax.barh(
                        phase.get("name", f"Phase {i+1}"),
                        width,
                        left=start,
                        color=colors[i % len(colors)],
                        alpha=0.85,
                        height=0.6,
                    )

                ax.set_xlim(0, max(p.get("end_week", 8) for p in phases) + 1)
                ax.set_xlabel("Week", color="#aaaaaa")
                ax.tick_params(colors="#aaaaaa")
                ax.spines[:].set_color("#333333")
                return []

            anim = animation.FuncAnimation(
                fig, animate, init_func=init, frames=total_frames, interval=1000 / self.fps, blit=False
            )
            writer = animation.FFMpegWriter(fps=self.fps, bitrate=2000)
            anim.save(out_path, writer=writer, dpi=100)
            plt.close(fig)
            engine = "matplotlib"
        except Exception as exc:
            # Fallback: write a placeholder text file
            out_path = out_path.replace(".mp4", "_placeholder.txt")
            Path(out_path).write_text(f"Roadmap animation placeholder (ffmpeg required): {title}\nError: {exc}")
            engine = "placeholder"

        return VideoResult(
            path=out_path,
            duration_seconds=duration,
            fps=self.fps,
            resolution=self.resolution,
            format="mp4" if engine == "matplotlib" else "txt",
            engine=engine,
        )

    def _render_kpi_animation(
        self,
        title: str,
        kpis: list[dict],
        out_path: str,
        duration: float,
    ) -> VideoResult:
        try:
            import matplotlib.pyplot as plt
            import matplotlib.animation as animation

            fig, axes = plt.subplots(
                2, max(2, (len(kpis) + 1) // 2),
                figsize=(16, 9),
                facecolor="#1a1a2e",
            )
            fig.suptitle(title, color="white", fontsize=20, fontweight="bold")

            total_frames = int(self.fps * duration)

            def animate(frame: int):
                progress = frame / total_frames
                for ax in axes.flat:
                    ax.clear()
                    ax.set_facecolor("#16213e")
                for i, (ax, kpi) in enumerate(zip(axes.flat, kpis)):
                    val = kpi.get("value", 0) * progress
                    target = kpi.get("target", val)
                    color = "#2ecc71" if val >= target * 0.9 else "#e74c3c"
                    ax.bar([kpi.get("name", f"KPI {i+1}")], [val], color=color, alpha=0.85)
                    ax.axhline(y=target, color="#f39c12", linestyle="--", linewidth=1.5, label="Target")
                    ax.set_facecolor("#16213e")
                    ax.tick_params(colors="#aaaaaa")
                    ax.set_title(kpi.get("name", ""), color="white", fontsize=10)
                return []

            anim = animation.FuncAnimation(fig, animate, frames=total_frames, interval=1000 / self.fps)
            writer = animation.FFMpegWriter(fps=self.fps, bitrate=2000)
            anim.save(out_path, writer=writer, dpi=100)
            plt.close(fig)
            engine = "matplotlib"
        except Exception as exc:
            out_path = out_path.replace(".mp4", "_placeholder.txt")
            Path(out_path).write_text(f"KPI animation placeholder: {title}\nError: {exc}")
            engine = "placeholder"

        return VideoResult(
            path=out_path,
            duration_seconds=duration,
            fps=self.fps,
            resolution=self.resolution,
            format="mp4" if engine == "matplotlib" else "txt",
            engine=engine,
        )

    def _render_process_animation(
        self, title: str, steps: list[dict], out_path: str, duration: float
    ) -> VideoResult:
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            import matplotlib.animation as animation

            fig, ax = plt.subplots(figsize=(16, 9), facecolor="#1a1a2e")
            ax.set_facecolor("#1a1a2e")
            total_frames = int(self.fps * duration)
            frames_per_step = total_frames // max(len(steps), 1)

            def animate(frame: int):
                ax.clear()
                ax.set_facecolor("#1a1a2e")
                ax.set_title(title, color="white", fontsize=18, fontweight="bold")
                ax.axis("off")

                visible_steps = min(frame // frames_per_step + 1, len(steps))
                colors = ["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6"]
                x_start = 0.05
                step_width = 0.9 / max(len(steps), 1)

                for i in range(visible_steps):
                    step = steps[i]
                    x = x_start + i * (step_width + 0.02)
                    rect = mpatches.FancyBboxPatch(
                        (x, 0.35), step_width - 0.02, 0.3,
                        boxstyle="round,pad=0.02",
                        facecolor=colors[i % len(colors)],
                        alpha=0.85,
                        transform=ax.transAxes,
                    )
                    ax.add_patch(rect)
                    ax.text(
                        x + (step_width - 0.02) / 2, 0.5,
                        step.get("name", f"Step {i+1}"),
                        transform=ax.transAxes,
                        ha="center", va="center",
                        color="white", fontsize=9, fontweight="bold",
                    )
                    if i < visible_steps - 1:
                        ax.annotate(
                            "", xy=(x + step_width + 0.01, 0.5),
                            xytext=(x + step_width - 0.01, 0.5),
                            xycoords="axes fraction", textcoords="axes fraction",
                            arrowprops=dict(arrowstyle="->", color="#aaaaaa", lw=2),
                        )
                return []

            anim = animation.FuncAnimation(fig, animate, frames=total_frames, interval=1000 / self.fps)
            writer = animation.FFMpegWriter(fps=self.fps, bitrate=2000)
            anim.save(out_path, writer=writer, dpi=100)
            plt.close(fig)
            engine = "matplotlib"
        except Exception as exc:
            out_path = out_path.replace(".mp4", "_placeholder.txt")
            Path(out_path).write_text(f"Process animation placeholder: {title}\nError: {exc}")
            engine = "placeholder"

        return VideoResult(path=out_path, duration_seconds=duration, fps=self.fps,
                           resolution=self.resolution, format="mp4" if engine == "matplotlib" else "txt",
                           engine=engine)

    def _render_waterfall_animation(
        self, title: str, data: dict, out_path: str, duration: float
    ) -> VideoResult:
        try:
            import matplotlib.pyplot as plt
            import matplotlib.animation as animation
            import numpy as np

            categories = data.get("categories", ["Budget", "Volume", "Price", "Costs", "Actual"])
            values = data.get("values", [1000, 150, -80, -120, 950])
            total_frames = int(self.fps * duration)

            fig, ax = plt.subplots(figsize=(16, 9), facecolor="#1a1a2e")
            ax.set_facecolor("#1a1a2e")

            def animate(frame: int):
                progress = frame / total_frames
                ax.clear()
                ax.set_facecolor("#1a1a2e")
                ax.set_title(title, color="white", fontsize=18, fontweight="bold")
                ax.spines[:].set_color("#333333")
                ax.tick_params(colors="#aaaaaa")

                running = 0
                bottoms = []
                bar_vals = []
                colors = []
                for i, v in enumerate(values):
                    animated_v = v * min(progress * (len(values) / (i + 1)), 1.0)
                    bottoms.append(running if animated_v >= 0 else running + animated_v)
                    bar_vals.append(abs(animated_v))
                    colors.append("#2ecc71" if animated_v >= 0 else "#e74c3c")
                    running += animated_v

                ax.bar(categories, bar_vals, bottom=bottoms, color=colors, alpha=0.85)
                return []

            anim = animation.FuncAnimation(fig, animate, frames=total_frames, interval=1000 / self.fps)
            writer = animation.FFMpegWriter(fps=self.fps, bitrate=2000)
            anim.save(out_path, writer=writer, dpi=100)
            plt.close(fig)
            engine = "matplotlib"
        except Exception as exc:
            out_path = out_path.replace(".mp4", "_placeholder.txt")
            Path(out_path).write_text(f"Waterfall animation placeholder: {title}\nError: {exc}")
            engine = "placeholder"

        return VideoResult(path=out_path, duration_seconds=duration, fps=self.fps,
                           resolution=self.resolution, format="mp4" if engine == "matplotlib" else "txt",
                           engine=engine)

    def _fallback_text_animation(self, prompt: str, output_filename: str | None) -> VideoResult:
        fname = output_filename or "luma_fallback.txt"
        out_path = str(self.output_dir / fname.replace(".mp4", ".txt"))
        Path(out_path).write_text(f"[LUMA AI OFFLINE]\nPrompt: {prompt}\n\nSet LUMA_AI_KEY to enable photorealistic video generation.")
        return VideoResult(path=out_path, duration_seconds=0, fps=0,
                           resolution=(0, 0), format="txt", engine="fallback")

    @staticmethod
    def tool_definitions() -> list[dict]:
        return [
            {
                "name": "animate_erp_roadmap",
                "description": "Generate an animated ERP transformation roadmap video",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string"},
                        "phases": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "start_week": {"type": "integer"},
                                    "end_week": {"type": "integer"},
                                },
                            },
                        },
                        "duration": {"type": "number", "default": 30},
                    },
                    "required": ["project_name", "phases"],
                },
            },
            {
                "name": "animate_kpi_dashboard",
                "description": "Generate an animated CFO KPI dashboard video",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "kpis": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "value": {"type": "number"},
                                    "target": {"type": "number"},
                                },
                            },
                        },
                    },
                    "required": ["kpis"],
                },
            },
            {
                "name": "generate_luma_video",
                "description": "Generate a photorealistic video using Luma AI Dream Machine",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "Text description of the video to generate"},
                        "duration": {"type": "number", "default": 5},
                    },
                    "required": ["prompt"],
                },
            },
        ]
