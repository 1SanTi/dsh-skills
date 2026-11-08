#!/usr/bin/env python3
"""ASR 1.4.0: local first, consistent outputs, isolated run directories."""
import argparse
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import wave

VERSION = "1.4.0"
WATERMARK = "[机器转写，未经人工校对；专名、数字、承诺和结论须回听原音频核实]"
FORMATS = {"txt", "md", "srt", "vtt", "json"}


def configure_console():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def available(name):
    try:
        return importlib.util.find_spec(name) is not None
    except (ValueError, ImportError, AttributeError):
        return False


def field(obj, name, default=None):
    return obj.get(name, default) if isinstance(obj, dict) else getattr(obj, name, default)


def normalize(segments):
    result, previous = [], -1.0
    for s in segments:
        text = str(field(s, "text", "") or "").strip()
        if not text:
            continue
        start, end = float(field(s, "start")), float(field(s, "end"))
        if not math.isfinite(start) or not math.isfinite(end) or start < 0 or end < start or start < previous:
            raise ValueError("引擎返回无效时间戳或片段顺序，未生成正式转写文件。")
        previous = start
        speaker = field(s, "speaker")
        result.append(dict(start=start, end=end, text=text, speaker=str(speaker) if speaker else None))
    return result


def fmt_ts(t, vtt=False):
    if not math.isfinite(t) or t < 0:
        raise ValueError("无效时间戳")
    seconds, ms = divmod(round(t * 1000), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}{'.' if vtt else ','}{ms:03d}"


def write_outputs(segments, out_dir, stem, formats):
    """Preflight collisions; never overwrite a transcript or delete sibling files."""
    segments = normalize(segments)
    if not formats or set(formats) - FORMATS:
        raise ValueError("输出格式仅支持 txt,md,srt,vtt,json")
    paths = [Path(out_dir) / (stem + "." + fmt) for fmt in formats]
    if any(p.exists() for p in paths):
        raise FileExistsError("目标文件已存在，请使用新的输出目录。")
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for fmt, path in zip(formats, paths):
        with path.open("x", encoding="utf-8", newline="\n") as f:
            if fmt == "json":
                json.dump(dict(notice=WATERMARK, segments=segments), f, ensure_ascii=False, indent=2)
            elif fmt in {"txt", "md"}:
                f.write(("# 录音文字稿\n\n" if fmt == "md" else "") + WATERMARK + "\n\n")
                for s in segments:
                    label = f"[{s['speaker']}] " if s['speaker'] else ""
                    f.write(f"[{fmt_ts(s['start'], True)}–{fmt_ts(s['end'], True)}] {label}{s['text']}\n\n")
            else:
                if fmt == "vtt":
                    f.write("WEBVTT\n\nNOTE 机器转写，未经人工校对\n\n")
                for i, s in enumerate(segments, 1):
                    label = f"[{s['speaker']}] " if s['speaker'] else ""
                    if fmt == "srt":
                        f.write(f"{i}\n")
                    f.write(f"{fmt_ts(s['start'], fmt == 'vtt')} --> {fmt_ts(s['end'], fmt == 'vtt')}\n{label}{s['text']}\n\n")
    return [str(p.resolve()) for p in paths]


def ffmpeg(args):
    if not shutil.which("ffmpeg"):
        raise RuntimeError("本操作需要 ffmpeg；普通 faster-whisper 全文转写可不装系统 ffmpeg。见 references/install.md。")
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", *args],
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if r.returncode:
        raise RuntimeError("ffmpeg 解码/切分失败，请检查文件能否正常播放。")


def run_faster(audio, args):
    from faster_whisper import WhisperModel
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type,
                         local_files_only=args.offline)
    segs, info = model.transcribe(str(audio), language=None if args.lang == "auto" else args.lang,
                                 initial_prompt=args.hint_words or None, vad_filter=True)
    return normalize(segs), dict(engine="faster-whisper", language=info.language,
                                duration_seconds=info.duration, diarization=False)


def run_whisperx(audio, args):
    if args.offline:
        raise ValueError("--offline 当前仅用于普通 faster-whisper 转写；WhisperX 多模型离线部署见官方文档。")
    token = args.hf_token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if args.diarize and not token:
        raise RuntimeError("区分说话人需要 HF_TOKEN 及模型权限；未改为普通转写。见 references/install.md。")
    if not shutil.which("whisperx"):
        raise RuntimeError("当前环境没有 whisperx 命令；请在同一 Python 环境安装并激活环境。")
    with tempfile.TemporaryDirectory(prefix="asr_whisperx_") as tmp:
        cmd = ["whisperx", str(audio), "--model", args.model, "--output_dir", tmp,
               "--output_format", "json", "--device", args.device, "--compute_type", args.compute_type,
               "--batch_size", str(args.batch_size)]
        if args.lang != "auto":
            cmd += ["--language", args.lang]
        if args.hint_words:
            cmd += ["--initial_prompt", args.hint_words]
        if args.diarize:
            cmd += ["--diarize", "--hf_token", token]
            if args.speakers:
                cmd += ["--min_speakers", str(args.speakers), "--max_speakers", str(args.speakers)]
            else:
                if args.min_speakers:
                    cmd += ["--min_speakers", str(args.min_speakers)]
                if args.max_speakers:
                    cmd += ["--max_speakers", str(args.max_speakers)]
        # Never echo token-bearing argv or raw third-party transcript/error logs.
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if r.returncode:
            raise RuntimeError("WhisperX 运行失败，请核对模型权限、ffmpeg、版本及内存；未静默降级。")
        path = Path(tmp) / (Path(audio).stem + ".json")
        if not path.is_file():
            raise RuntimeError("WhisperX 未生成预期 JSON 结果。")
        data = json.loads(path.read_text(encoding="utf-8"))
        segs = normalize(data.get("segments", []))
        if args.diarize and segs and not any(s['speaker'] for s in segs):
            raise RuntimeError("说话人分离未返回任何标签，未冒充说话人版本。")
        return segs, dict(engine="whisperx", language=data.get("language", args.lang),
                          duration_seconds=None, diarization=args.diarize)


def run_openai(audio, args):
    if args.cloud_model != "whisper-1":
        raise ValueError("当前时间戳适配器只支持 whisper-1。")
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("未设置 OPENAI_API_KEY。")
    from openai import OpenAI
    client = OpenAI()
    segments, offset = [], 0.0
    with tempfile.TemporaryDirectory(prefix="asr_chunks_") as tmp:
        if Path(audio).stat().st_size >= 24_000_000:
            ffmpeg(["-i", str(audio), "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
                    "-f", "segment", "-segment_time", "600", str(Path(tmp) / "part_%05d.wav")])
            chunks = sorted(Path(tmp).glob("part_*.wav"))
            if not chunks:
                raise RuntimeError("未生成音频分块。")
        else:
            chunks = [Path(audio)]
        for ch in chunks:
            with ch.open("rb") as fh:
                kwargs = dict(model="whisper-1", file=fh, response_format="verbose_json",
                              timestamp_granularities=["segment"])
                if args.lang != "auto":
                    kwargs["language"] = args.lang
                if args.hint_words:
                    kwargs["prompt"] = args.hint_words
                response = client.audio.transcriptions.create(**kwargs)
            part = normalize(field(response, "segments", []) or [])
            if not part and str(field(response, "text", "") or "").strip():
                raise RuntimeError("云端有文本但缺少片段时间戳，请检查 SDK/模型；未编造时间戳。")
            segments.extend([{**s, "start": s["start"] + offset, "end": s["end"] + offset} for s in part])
            if len(chunks) > 1:
                with wave.open(str(ch), "rb") as wav:
                    offset += wav.getnframes() / wav.getframerate()
            else:
                offset = field(response, "duration")
    return segments, dict(engine="openai/whisper-1", language=args.lang, duration_seconds=offset, diarization=False)


def run_dashscope(audio, args):
    if not os.environ.get("DASHSCOPE_API_KEY"):
        raise RuntimeError("未设置 DASHSCOPE_API_KEY。")
    import dashscope
    from dashscope.audio.asr import Recognition
    dashscope.api_key = os.environ["DASHSCOPE_API_KEY"]
    with tempfile.TemporaryDirectory(prefix="asr_dashscope_") as tmp:
        wav_path = Path(tmp) / "input.wav"
        ffmpeg(["-i", str(audio), "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(wav_path)])
        result = Recognition(model=args.cloud_model_ds, format="wav", sample_rate=16000,
                             callback=None).call(str(wav_path))
        if result is None or field(result, "status_code", 200) != 200:
            raise RuntimeError("DashScope 调用失败，请核对 SDK、权限、地区与额度。")
        if not hasattr(result, "get_sentence"):
            raise RuntimeError("DashScope 返回结构不兼容，请更新 SDK。")
        sents = result.get_sentence() or []
        if not isinstance(sents, list):
            raise RuntimeError("DashScope 非流式结果应为句子列表。")
        segs = normalize([dict(start=field(s, "begin_time") / 1000, end=field(s, "end_time") / 1000,
                               text=field(s, "text")) for s in sents])
        with wave.open(str(wav_path), "rb") as wav:
            duration = wav.getnframes() / wav.getframerate()
    return segs, dict(engine="dashscope/" + args.cloud_model_ds, language=args.lang,
                      duration_seconds=duration, diarization=False)


def parser():
    ap = argparse.ArgumentParser(description="录音转文字：本地普通转写无需云端 API Key，每次生成独立目录。")
    ap.add_argument("audio", help="本地音频或视频文件")
    ap.add_argument("--engine", choices=["auto", "local", "cloud"], default="auto")
    ap.add_argument("--lang", default="zh", help="zh、en 或 auto")
    ap.add_argument("--model", default="small", help="默认 small；质量优先可选 large-v3")
    ap.add_argument("--cloud-provider", choices=["openai", "dashscope"], default="openai")
    ap.add_argument("--cloud-model", default="whisper-1")
    ap.add_argument("--cloud-model-ds", default="paraformer-realtime-v2")
    ap.add_argument("--diarize", action="store_true", help="WhisperX 说话人分离；失败不静默降级")
    ap.add_argument("--speakers", type=int, default=0)
    ap.add_argument("--min-speakers", type=int, default=0)
    ap.add_argument("--max-speakers", type=int, default=0)
    ap.add_argument("--formats", default="srt,txt", help="txt,md,srt,vtt,json")
    ap.add_argument("--output-dir", default="./outputs", help="父目录；每次建立独立子目录")
    ap.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    ap.add_argument("--compute-type", default="int8")
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--hf-token", default="", help="优先设置 HF_TOKEN，避免命令历史留存")
    ap.add_argument("--hint-words", default="", help="术语提示，不能保证专名识别正确")
    ap.add_argument("--offline", action="store_true", help="普通本地转写仅使用已缓存模型，不下载")
    ap.add_argument("--preview-seconds", type=int, default=0, help="仅试转开头 N 秒，需 ffmpeg；0 为全文")
    return ap


def validate_args(args):
    args.formats = list(dict.fromkeys(x.strip() for x in args.formats.split(",") if x.strip()))
    if not args.formats or set(args.formats) - FORMATS:
        raise ValueError("输出格式仅支持 txt,md,srt,vtt,json。")
    if args.preview_seconds < 0 or args.batch_size < 1:
        raise ValueError("试转秒数不能为负；batch-size 必须为正。")
    if any(x < 0 for x in [args.speakers, args.min_speakers, args.max_speakers]):
        raise ValueError("说话人数不能为负。")
    if args.min_speakers and args.max_speakers and args.min_speakers > args.max_speakers:
        raise ValueError("最少说话人数不能大于最多人数。")
    if args.speakers and (args.min_speakers or args.max_speakers):
        raise ValueError("确切人数和人数范围请选择一种。")
    if any([args.speakers, args.min_speakers, args.max_speakers]) and not args.diarize:
        raise ValueError("指定说话人数时需加 --diarize。")
    if args.engine == "cloud" and (args.diarize or args.offline):
        raise ValueError("当前云端适配器不支持 --diarize 或 --offline。")
    if args.engine == "cloud" and args.cloud_provider == "openai" and args.cloud_model != "whisper-1":
        raise ValueError("当前 OpenAI 时间戳适配器仅支持 whisper-1。")


def main(argv=None):
    configure_console()
    args = parser().parse_args(argv)
    try:
        validate_args(args)
        audio = Path(args.audio).expanduser().resolve()
        if not audio.is_file():
            raise ValueError("文件不存在或不是文件。")
        if audio.stat().st_size == 0:
            raise ValueError("音频文件为空。")
        parent = Path(args.output_dir).expanduser().resolve()
        if args.engine != "cloud":
            if args.diarize:
                runner = run_whisperx
            elif available("faster_whisper"):
                runner = run_faster
            elif shutil.which("whisperx"):
                runner = run_whisperx
            else:
                raise RuntimeError("本地引擎未安装。请按 references/install.md 安装 faster-whisper；不会自动上传云端。")
        else:
            runner = run_dashscope if args.cloud_provider == "dashscope" else run_openai
            print("[asr] 云端模式：音频将发送至所选服务商，请确保此文件已获上云授权。", flush=True)
        print("[asr] 转写启动；首次使用可能需下载模型。", flush=True)
        with tempfile.TemporaryDirectory(prefix="asr_preview_") as tmp:
            source = audio
            if args.preview_seconds:
                source = Path(tmp) / "preview.wav"
                ffmpeg(["-i", str(audio), "-t", str(args.preview_seconds), "-ar", "16000", "-ac", "1", str(source)])
            segments, meta = runner(source, args)
        segments = normalize(segments)
        parent.mkdir(parents=True, exist_ok=True)
        run_dir = Path(tempfile.mkdtemp(prefix="asr_", dir=str(parent)))
        status = "preview_completed" if args.preview_seconds else "completed"
        if not segments:
            status = "no_speech_detected"
        files = write_outputs(segments, run_dir, audio.stem, args.formats) if segments else []
        receipt = dict(version=VERSION, status=status, notice=WATERMARK,
                       scope="preview" if args.preview_seconds else "full", preview_seconds=args.preview_seconds,
                       audio_uploaded=args.engine == "cloud", segment_count=len(segments),
                       unassigned_speaker_segments=sum(not s['speaker'] for s in segments) if args.diarize else None,
                       **meta, files=files)
        receipt_path = run_dir / "run-receipt.json"
        receipt_number = 1
        while receipt_path.exists():
            receipt_number += 1
            receipt_path = run_dir / f"run-receipt-{receipt_number}.json"
        with receipt_path.open("x", encoding="utf-8") as receipt_file:
            json.dump(receipt, receipt_file, ensure_ascii=False, indent=2)
        print(json.dumps(dict(**receipt, receipt=str(receipt_path)), ensure_ascii=False, indent=2))
        return 3 if not segments else 0
    except (ValueError, FileNotFoundError) as e:
        print(f"[asr] 参数/输入错误：{e}", file=sys.stderr)
        return 2
    except RuntimeError as e:
        print(f"[asr] 未完成：{e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[asr] 未完成：{type(e).__name__}。请核对安装、模型缓存/权限、网络与资源；未生成成功回执。", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
