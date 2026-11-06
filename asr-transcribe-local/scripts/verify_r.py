#!/usr/bin/env python3
"""Deterministic regression tests using fake engines, not ASR accuracy tests."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import wave
import transcribe as t


class Regression(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.audio = self.root / "会议.wav"
        with wave.open(str(self.audio), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(b'\0\0' * 16000)
        self.segs = [dict(start=0.125, end=1.0, text="预算三万元。", speaker="SPEAKER_00")]
        self.meta = dict(engine="fake", language="zh", duration_seconds=1.0, diarization=False)

    def args(self, *extra):
        a = t.parser().parse_args([str(self.audio), *extra]); t.validate_args(a); return a

    def call(self, *extra, segments=None):
        output = io.StringIO()
        with patch.object(t, "available", return_value=True), patch.object(t, "run_faster", return_value=(self.segs if segments is None else segments, self.meta)), contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            rc = t.main([str(self.audio), "--output-dir", str(self.root), *extra])
        receipts = list(self.root.glob('asr_*/run-receipt.json'))
        return rc, receipts, output.getvalue()

    def test_timestamp_carry(self):
        self.assertEqual(t.fmt_ts(59.9999), "00:01:00,000")
        self.assertEqual(t.fmt_ts(3599.9999, True), "01:00:00.000")

    def test_timestamp_reject(self):
        for n in [float('nan'), float('inf'), -1]:
            with self.subTest(n=n), self.assertRaises(ValueError): t.fmt_ts(n)

    def test_output_all_formats(self):
        paths = t.write_outputs(self.segs, self.root / 'out', '会议', ['txt','md','srt','vtt','json'])
        self.assertEqual(len(paths), 5)
        for p in paths: self.assertIn('预算三万元', Path(p).read_text(encoding='utf-8'))
        self.assertTrue(Path(paths[3]).read_text(encoding='utf-8').startswith('WEBVTT'))
        self.assertIn(t.WATERMARK, Path(paths[0]).read_text(encoding='utf-8'))
        self.assertIn('SPEAKER_00', Path(paths[2]).read_text(encoding='utf-8'))

    def test_no_overwrite_preflight(self):
        (self.root/'会议.txt').write_text('手工修改', encoding='utf-8')
        with self.assertRaises(FileExistsError): t.write_outputs(self.segs,self.root,'会议',['srt','txt'])
        self.assertFalse((self.root/'会议.srt').exists())
        self.assertEqual((self.root/'会议.txt').read_text(encoding='utf-8'),'手工修改')

    def test_sibling_audio_preserved(self):
        original = self.audio.read_bytes()
        t.write_outputs(self.segs,self.root,'会议',['srt','txt'])
        self.assertEqual(self.audio.read_bytes(),original)

    def test_object_segments(self):
        obj = types.SimpleNamespace(start=0,end=1,text='  测试  ')
        self.assertEqual(t.normalize([obj])[0]['text'],'测试')

    def test_invalid_segments(self):
        for s in [dict(start=2,end=1,text='字'),dict(start=-1,end=1,text='字'),dict(start=0,end=float('inf'),text='字')]:
            with self.subTest(s=s), self.assertRaises(ValueError): t.normalize([s])

    def test_out_of_order(self):
        with self.assertRaises(ValueError): t.normalize([dict(start=2,end=3,text='一'),dict(start=1,end=2,text='二')])

    def test_empty_text_filtered(self):
        self.assertEqual(t.normalize([dict(text=' ')]), [])

    def test_formats_validation(self):
        for fmt in ['', 'docx', 'txt,docx']:
            with self.subTest(fmt=fmt), self.assertRaises(ValueError): self.args('--formats',fmt)
        self.assertEqual(self.args('--formats','txt,txt,srt').formats,['txt','srt'])

    def test_speaker_validation(self):
        for opts in [('--speakers','2'),('--diarize','--speakers','-1'),('--diarize','--min-speakers','3','--max-speakers','2'),('--diarize','--speakers','2','--max-speakers','3')]:
            with self.subTest(opts=opts), self.assertRaises(ValueError): self.args(*opts)

    def test_cloud_reject_unsupported(self):
        for opts in [('--diarize',),('--offline',),('--cloud-model','gpt-4o-transcribe')]:
            with self.subTest(opts=opts), self.assertRaises(ValueError): self.args('--engine','cloud',*opts)

    def test_unique_run_directory(self):
        original = self.audio.read_bytes()
        self.assertEqual(self.call()[0],0)
        rc, receipts, _ = self.call()
        self.assertEqual(rc,0); self.assertEqual(len(receipts),2)
        self.assertEqual(self.audio.read_bytes(),original)

    def test_empty_no_success(self):
        rc, receipts, _ = self.call(segments=[])
        r=json.loads(receipts[0].read_text(encoding='utf-8'))
        self.assertEqual(rc,3); self.assertEqual(r['status'],'no_speech_detected'); self.assertEqual(r['files'],[])

    def test_preview_truthful(self):
        with patch.object(t,'ffmpeg') as cut:
            rc, receipts, _ = self.call('--preview-seconds','30')
        self.assertEqual(rc,0); self.assertTrue(cut.called)
        r=json.loads(receipts[0].read_text(encoding='utf-8'))
        self.assertEqual(r['scope'],'preview'); self.assertEqual(r['status'],'preview_completed')

    def test_no_auto_cloud(self):
        with patch.object(t,'available',return_value=False), patch.object(t.shutil,'which',return_value=None), patch.object(t,'run_openai') as cloud, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(t.main([str(self.audio)]),1)
            cloud.assert_not_called()

    def test_diarization_no_fallback(self):
        with patch.object(t,'run_whisperx',side_effect=RuntimeError('missing')), patch.object(t,'run_faster') as plain, contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(t.main([str(self.audio),'--diarize']),1)
            plain.assert_not_called()

    def test_whisperx_isolated_and_token_not_logged(self):
        original=self.audio.read_bytes(); temp_paths=[]
        def fake(cmd, **kwargs):
            dest=Path(cmd[cmd.index('--output_dir')+1]); temp_paths.append(dest)
            self.assertNotEqual(dest,self.root)
            self.assertEqual(cmd[cmd.index('--output_format')+1],'json')
            (dest/(self.audio.stem+'.json')).write_text(json.dumps(dict(segments=self.segs,language='zh')),encoding='utf-8')
            return types.SimpleNamespace(returncode=0)
        buf=io.StringIO()
        with patch.object(t.shutil,'which',return_value='whisperx'),patch.object(t.subprocess,'run',side_effect=fake),contextlib.redirect_stdout(buf),contextlib.redirect_stderr(buf):
            segs, meta=t.run_whisperx(self.audio,self.args('--diarize','--hf-token','SECRET_TEST'))
        self.assertTrue(meta['diarization']); self.assertNotIn('SECRET_TEST',buf.getvalue())
        self.assertEqual(self.audio.read_bytes(),original); self.assertFalse(temp_paths[0].exists())

    def test_whisperx_no_labels_rejected(self):
        def fake(cmd,**kwargs):
            dest=Path(cmd[cmd.index('--output_dir')+1])
            (dest/(self.audio.stem+'.json')).write_text(json.dumps(dict(segments=[dict(start=0,end=1,text='字')])),encoding='utf-8')
            return types.SimpleNamespace(returncode=0)
        with patch.object(t.shutil,'which',return_value='whisperx'),patch.object(t.subprocess,'run',side_effect=fake),self.assertRaises(RuntimeError):
            t.run_whisperx(self.audio,self.args('--diarize','--hf-token','TEST'))

    def test_openai_dict_and_object(self):
        for response in [dict(segments=self.segs,duration=1),types.SimpleNamespace(segments=[types.SimpleNamespace(**self.segs[0])],duration=1)]:
            client=types.SimpleNamespace(audio=types.SimpleNamespace(transcriptions=types.SimpleNamespace(create=lambda **kw: response)))
            with patch.dict(sys.modules,{'openai':types.SimpleNamespace(OpenAI=lambda:client)}),patch.dict(os.environ,{'OPENAI_API_KEY':'TEST'}):
                segs,meta=t.run_openai(self.audio,self.args('--engine','cloud'))
            self.assertEqual(segs[0]['text'],'预算三万元。')
            self.assertEqual(meta['duration_seconds'],1)

    def test_openai_missing_timestamps_rejected(self):
        client=types.SimpleNamespace(audio=types.SimpleNamespace(transcriptions=types.SimpleNamespace(create=lambda **kw:dict(text='有文字',segments=[]))))
        with patch.dict(sys.modules,{'openai':types.SimpleNamespace(OpenAI=lambda:client)}),patch.dict(os.environ,{'OPENAI_API_KEY':'TEST'}),self.assertRaises(RuntimeError):
            t.run_openai(self.audio,self.args('--engine','cloud'))

    def test_faster_offline_forwarded(self):
        received={}
        class Model:
            def __init__(s,*a,**kw): received.update(kw)
            def transcribe(s,*a,**kw): return iter(self.segs),types.SimpleNamespace(language='zh',duration=1)
        with patch.dict(sys.modules,{'faster_whisper':types.SimpleNamespace(WhisperModel=Model)}):
            t.run_faster(self.audio,self.args('--offline'))
        self.assertTrue(received['local_files_only'])

    def test_missing_input(self):
        with contextlib.redirect_stderr(io.StringIO()): self.assertEqual(t.main([str(self.root/'missing.wav')]),2)

    def test_receipt_name_collision(self):
        self.audio = self.audio.rename(self.root/'run-receipt.wav')
        rc, receipts, _ = self.call('--formats','json')
        self.assertEqual(rc,0)
        out = list(self.root.glob('asr_*'))[0]
        transcript = json.loads((out/'run-receipt.json').read_text(encoding='utf-8'))
        receipt = json.loads((out/'run-receipt-2.json').read_text(encoding='utf-8'))
        self.assertEqual(transcript['segments'][0]['text'],'预算三万元。')
        self.assertEqual(receipt['status'],'completed')

    def test_openai_chunk_offsets_and_cleanup(self):
        with self.audio.open('ab') as f: f.truncate(24_000_001)
        paths=[]
        def fake_cut(argv):
            parent=Path(argv[-1]).parent; paths.append(parent)
            for i in range(2):
                with wave.open(str(parent/f'part_{i:05d}.wav'),'wb') as w:
                    w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(b'\0\0'*32000)
        response=dict(segments=[dict(start=.25,end=1,text='字')],duration=999)
        client=types.SimpleNamespace(audio=types.SimpleNamespace(transcriptions=types.SimpleNamespace(create=lambda **kw:response)))
        with patch.object(t,'ffmpeg',side_effect=fake_cut),patch.dict(sys.modules,{'openai':types.SimpleNamespace(OpenAI=lambda:client)}),patch.dict(os.environ,{'OPENAI_API_KEY':'TEST'}):
            segs,meta=t.run_openai(self.audio,self.args('--engine','cloud'))
        self.assertEqual(segs[1]['start'],2.25)
        self.assertEqual(meta['duration_seconds'],4)
        self.assertFalse(paths[0].exists())

    def test_dashscope_outputs_and_cleanup(self):
        paths=[]
        def fake_convert(argv):
            dest=Path(argv[-1]); paths.append(dest.parent); dest.write_bytes(self.audio.read_bytes())
        result=types.SimpleNamespace(status_code=200,get_sentence=lambda:[dict(begin_time=125,end_time=1000,text='测试')])
        api=types.SimpleNamespace(Recognition=lambda **kw:types.SimpleNamespace(call=lambda p:result))
        with patch.object(t,'ffmpeg',side_effect=fake_convert),patch.dict(sys.modules,{'dashscope':types.SimpleNamespace(),'dashscope.audio':types.SimpleNamespace(),'dashscope.audio.asr':api}),patch.dict(os.environ,{'DASHSCOPE_API_KEY':'TEST'}):
            segs,meta=t.run_dashscope(self.audio,self.args('--engine','cloud','--cloud-provider','dashscope'))
        self.assertEqual(segs[0]['start'],.125)
        paths_out=t.write_outputs(segs,self.root/'ds','文字稿',['txt','md','srt','vtt','json'])
        self.assertEqual(len(paths_out),5); self.assertFalse(paths[0].exists())

    def test_dashscope_error_no_success(self):
        def fake_convert(argv): Path(argv[-1]).write_bytes(self.audio.read_bytes())
        api=types.SimpleNamespace(Recognition=lambda **kw:types.SimpleNamespace(call=lambda p:types.SimpleNamespace(status_code=401)))
        with patch.object(t,'ffmpeg',side_effect=fake_convert),patch.dict(sys.modules,{'dashscope':types.SimpleNamespace(),'dashscope.audio':types.SimpleNamespace(),'dashscope.audio.asr':api}),patch.dict(os.environ,{'DASHSCOPE_API_KEY':'TEST'}),self.assertRaises(RuntimeError):
            t.run_dashscope(self.audio,self.args('--engine','cloud','--cloud-provider','dashscope'))

    def test_smoke_preflight_is_not_asr(self):
        r=subprocess.run([sys.executable,str(Path(__file__).with_name('smoke_test.py'))],capture_output=True,encoding='utf-8')
        self.assertEqual(r.returncode,0)
        self.assertIn('preflight_only',r.stdout); self.assertIn('"recognition_tested": false',r.stdout)

    def test_env_does_not_echo_secrets(self):
        r=subprocess.run([sys.executable,str(Path(__file__).with_name('check_env.py')),'--json'],env={**os.environ,'OPENAI_API_KEY':'SECRET_MARKER'},capture_output=True,encoding='utf-8')
        self.assertEqual(r.returncode,0); self.assertNotIn('SECRET_MARKER',r.stdout+r.stderr)
        self.assertTrue(json.loads(r.stdout)['openai_key_present'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
