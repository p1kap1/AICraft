"""
AI 视频剪辑工作流 - 本地版
功能：素材筛选 → 文案生成 → 剪辑指令 → 报告输出
调用 DeepSeek API 做决策，生成 FFmpeg 指令做执行
"""

import json
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv("/home/chen/agent/.env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

MODEL = os.getenv("OPENAI_MODEL", "deepseek-chat")


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """调用 DeepSeek API"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )
    return resp.choices[0].message.content


def extract_json(text: str) -> dict:
    """从 LLM 回复中提取 JSON"""
    # 去掉 markdown 代码块标记
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    return json.loads(text.strip())


# ============ 节点1: 素材筛选 ============
def step_material_filter(topic: str, materials: list[dict]) -> dict:
    print("🔍 [节点1] 素材筛选中...")

    material_text = "\n".join(
        f"{m['file']} | {m['duration']}秒 | {m['resolution']} | {m.get('note', '')}"
        for m in materials
    )

    result = call_llm(
        system_prompt="你是视频剪辑师。只输出 JSON，不要其他文字。",
        user_prompt=f"""分析以下素材，根据时长(3-15秒为佳)、分辨率(1080p优先)、与主题契合度打分(1-10)。

选题：{topic}

素材列表：
{material_text}

输出 JSON：
{{
  "selected": [
    {{"file": "文件名", "score": 8, "keep_from": "0", "keep_to": "8", "reason": "理由"}}
  ],
  "rejected": [
    {{"file": "文件名", "score": 3, "reason": "理由"}}
  ]
}}""",
    )
    return extract_json(result)


# ============ 节点2: 文案生成 ============
def step_script_generation(topic: str, selected: list[dict]) -> str:
    print("✍️  [节点2] 文案生成中...")

    clip_info = "\n".join(
        f"片段{i+1}: {s['file']} ({s['keep_from']}s-{s['keep_to']}s, {s['reason']})"
        for i, s in enumerate(selected)
    )

    return call_llm(
        system_prompt="你是短视频文案专家。每句文案用 [片段N] 标注对应的画面。口语化、有节奏、适合口播。",
        user_prompt=f"""选题：{topic}

可用画面片段：
{clip_info}

请写口播脚本，格式：
[片段1] 开场引入，提出观众痛点
[片段2] 展开讲解核心内容
...
结束前总结金句。总时长控制在30-60秒。

直接输出脚本，不要 JSON。""",
    )


# ============ 节点3: 剪辑指令生成 ============
def step_clip_commands(selected: list[dict], script: str) -> dict:
    print("🎬 [节点3] 生成剪辑指令...")

    # 解析 [片段N] 标注
    segments = re.findall(
        r"\[片段(\d+)\]\s*(.+?)(?=\[片段|\Z)", script, re.DOTALL
    )

    clips = []
    for seg_id, narration in segments:
        idx = int(seg_id) - 1
        if idx < len(selected):
            s = selected[idx]
            clips.append(
                {
                    "clip_id": int(seg_id),
                    "source_file": s["file"],
                    "trim_start": s["keep_from"],
                    "trim_end": s["keep_to"],
                    "narration": narration.strip(),
                }
            )

    # 生成 FFmpeg 命令
    ffmpeg_cmds = []
    filelist = []
    for c in clips:
        dur = float(c["trim_end"]) - float(c["trim_start"])
        out = f"clip_{c['clip_id']}.mp4"
        ffmpeg_cmds.append(
            f"ffmpeg -ss {c['trim_start']} -i {c['source_file']} "
            f"-t {dur} -c copy {out}"
        )
        filelist.append(out)

    # concat
    concat_input = "|".join(filelist)
    ffmpeg_cmds.append(f"ffmpeg -i 'concat:{concat_input}' -c copy final_output.mp4")

    return {"clips": clips, "ffmpeg_commands": ffmpeg_cmds}


# ============ 节点4: 报告生成 ============
def step_report(
    topic: str, selected: list, rejected: list, clips: list
) -> dict:
    print("📊 [节点4] 生成剪辑报告...")

    return {
        "title": topic,
        "generated_at": datetime.now().isoformat(),
        "material_summary": {
            "total": len(selected) + len(rejected),
            "selected": len(selected),
            "rejected": len(rejected),
            "total_duration": sum(
                float(c["trim_end"]) - float(c["trim_start"]) for c in clips
            ),
        },
        "clips": [
            {
                "序号": c["clip_id"],
                "源文件": c["source_file"],
                "时间段": f"{c['trim_start']}s-{c['trim_end']}s",
                "口播文案": c["narration"],
            }
            for c in clips
        ],
        "rejected": [
            {"文件": r["file"], "原因": r.get("reason", "")} for r in rejected
        ],
    }


# ============ 主流程 ============
def main():
    topic = "DeepSeek使用技巧"
    materials = [
        {"file": "intro.mp4", "duration": 12, "resolution": "1920x1080", "note": "开场动画"},
        {"file": "tutorial_1.mp4", "duration": 45, "resolution": "1920x1080", "note": "注册教程"},
        {"file": "tutorial_2.mp4", "duration": 30, "resolution": "1280x720", "note": "对话演示"},
        {"file": "tutorial_3.mp4", "duration": 20, "resolution": "1920x1080", "note": "高级功能"},
        {"file": "ending.mp4", "duration": 8, "resolution": "1920x1080", "note": "结尾引导关注"},
        {"file": "bad_shot.mp4", "duration": 2, "resolution": "640x480", "note": "晃动严重"},
        {"file": "too_long.mp4", "duration": 120, "resolution": "1920x1080", "note": "完整录屏"},
    ]

    print("=" * 60)
    print(f"  🎥 AI 视频剪辑工作流")
    print(f"  选题：{topic}")
    print(f"  素材：{len(materials)} 个视频")
    print("=" * 60)

    # Step 1: 素材筛选
    filter_result = step_material_filter(topic, materials)
    selected = filter_result["selected"]
    rejected = filter_result.get("rejected", [])
    print(f"  ✅ 选中 {len(selected)} 个，淘汰 {len(rejected)} 个\n")

    # Step 2: 文案生成
    script = step_script_generation(topic, selected)
    print(f"  ✅ 文案生成完成\n")
    print("  📝 口播脚本：")
    print("  " + script[:200] + "...\n")

    # Step 3: 剪辑指令
    clip_result = step_clip_commands(selected, script)
    print(f"  ✅ 生成 {len(clip_result['clips'])} 个剪辑片段\n")
    print("  🎬 FFmpeg 指令：")
    for cmd in clip_result["ffmpeg_commands"][:-1]:
        print(f"  $ {cmd}")
    print(f"  $ {clip_result['ffmpeg_commands'][-1]}")
    print()

    # Step 4: 报告
    report = step_report(topic, selected, rejected, clip_result["clips"])

    # 输出完整报告
    print("=" * 60)
    print("  📊 剪辑报告")
    print("=" * 60)
    print(f"  主题：{report['title']}")
    print(f"  时间：{report['generated_at']}")
    print(f"  素材：{report['material_summary']['total']}个 → 选中{report['material_summary']['selected']}个")
    print(f"  总时长：{report['material_summary']['total_duration']}秒")
    print()
    for c in report["clips"]:
        print(f"  [{c['序号']}] {c['源文件']} @ {c['时间段']}")
        print(f"      {c['口播文案'][:80]}")
        print()
    if report["rejected"]:
        print(f"  淘汰素材：")
        for r in report["rejected"]:
            print(f"  ✗ {r['文件']} — {r['原因']}")

    # 保存文件
    output_dir = "/home/chen/AICraft/output"
    os.makedirs(output_dir, exist_ok=True)

    with open(f"{output_dir}/clip_instructions.json", "w", encoding="utf-8") as f:
        json.dump(clip_result, f, ensure_ascii=False, indent=2)

    with open(f"{output_dir}/script.txt", "w", encoding="utf-8") as f:
        f.write(script)

    with open(f"{output_dir}/report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n  📁 文件已保存到 {output_dir}/")


if __name__ == "__main__":
    main()
