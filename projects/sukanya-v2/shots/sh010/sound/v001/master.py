# static-gain master to -14.00 LUFS (no limiter/compressor: the true peak is already far below -1.5 dBTP after gain)
# usage: vfx-python master.py in.wav out.wav
import sys, json, subprocess, re, numpy as np, soundfile as sf
def lufs(p):
    e = subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',p,'-af','loudnorm=I=-14:TP=-1.5:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
    return json.loads(e[e.rindex('{'):e.rindex('}')+1])
x, sr = sf.read(sys.argv[1], dtype='float64')
m = lufs(sys.argv[1]); gdb = -14.0 - float(m['input_i'])
y = x * 10 ** (gdb / 20)
assert np.abs(y).max() < 0.84, "sample peak too high for a static-gain master"
sf.write(sys.argv[2], y, sr, subtype='PCM_24')
m2 = lufs(sys.argv[2])
print(json.dumps(dict(gain_db=round(gdb,3), in_I=m['input_i'], in_TP=m['input_tp'], out_I=m2['input_i'], out_TP=m2['input_tp'], out_LRA=m2['input_lra'], sample_peak_dbfs=round(20*np.log10(np.abs(y).max()),2))))
