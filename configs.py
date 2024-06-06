tolerance = 0.8
win_s = 4096  
hop_s = 1024  
samplerate = 44100  
pitch_method = "default"  
pitch_unit = "midi"  

def create_pitch_detector():
    import aubio
    pitch_o = aubio.pitch(pitch_method, win_s, hop_s, samplerate)
    pitch_o.set_unit(pitch_unit)
    pitch_o.set_tolerance(tolerance)
    return pitch_o