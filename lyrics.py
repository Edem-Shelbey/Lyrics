# Play your favorite song
import os, time, random, math
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from colorama import init as colorama_init

colorama_init()

# ------------- CONFIG -------------
SONG_NAME = "I Wanna Be Yours" # Here you put the name of the song that you want to here
MUSIC_FOLDER = "C:/Users/folders" # Here you put the folder where the song is register

MIN_WORD_DELAY = 0.04
MAX_WORD_DELAY = 0.6
DEFAULT_LAST_LINE_DUR = 3.0

# ------------- LYRICS (timestamps en secondes) -------------
# To change the lyrics you should use the website LRCLIB to get the lyrics, and you can use chatgpt to make the lyrics that you take like that (I'll connect LRCLIB later)
Song_lyrics = {
    18.09: "I wanna be your vacuum cleaner",
    21.85: "Breathing in your dust",
    25.02: "I wanna be your Ford Cortina",
    28.72: "I will never rust",
    32.45: "If you like your coffee hot",
    36.08: "Let me be your coffee pot",
    39.44: "You call the shots, babe",
    42.38: "I just wanna be yours",
    46.04: "Secrets I have held in my heart",
    49.74: "Are harder to hide than I thought",
    53.39: "Maybe I just wanna be yours",
    56.79: "I wanna be yours",
    58.65: "I wanna be yours",
    62.04: "Wanna be yours",
    65.91: "Wanna be yours",
    69.43: "Wanna be yours",
    74.86: "Let me be your 'leccy meter",
    78.35: "And I'll never run out",
    81.55: "Let me be the portable heater",
    85.40: "That you'll get cold without",
    88.96: "I wanna be your setting lotion",
    92.70: "Hold your hair in deep devotion (I'll be)",
    96.29: "At least as deep as the Pacific Ocean",
    99.46: "Now I wanna be yours",
    102.98: "Secrets I have held in my heart",
    106.67: "Are harder to hide than I thought",
    110.32: "Maybe I just wanna be yours",
    113.62: "I wanna be yours",
    115.57: "I wanna be yours",
    119.26: "Wanna be yours",
    122.54: "Wanna be yours",
    126.16: "Wanna be yours",
    129.71: "Wanna be yours",
    133.36: "Wanna be yours",
    136.78: "Wanna be yours",
    140.36: "Wanna be yours",
    144.15: "Wanna be yours",
    146.23: "I wanna be your vacuum cleaner (Wanna be yours)",
    149.84: "Breathing in your dust (Wanna be yours)",
    152.90: "I wanna be your Ford Cortina (Wanna be yours)",
    156.88: "I will never rust (Wanna be yours)",
    159.64: "I just wanna be yours (Wanna be yours)",
    162.99: "I just wanna be yours (Wanna be yours)",
    166.63: "I just wanna be yours (Wanna be yours)",
    171.28: ""
}

# ------------- HELPERS -------------
def find_folder():
    folder = MUSIC_FOLDER
    try:
        return [f for f in os.listdir(folder) if f.lower().endswith(".mp3")]
    except FileNotFoundError:
        return []

def find_song(mp3_files, song_name):
    if mp3_files:
        return [f for f in mp3_files if song_name.lower() in f.lower()]
    return []

def hsv_to_rgb_i(h, s, v):
    h = h % 1.0
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    vals = {
        0: (v, t, p),
        1: (q, v, p),
        2: (p, v, t),
        3: (p, q, v),
        4: (t, p, v),
        5: (v, p, q),
    }[i % 6]
    return tuple(int(255 * x) for x in vals)

def rgb_ansi(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

RESET = "\033[0m"

def apply_size_sim(word, size_effect):
    if size_effect == "large":
        return word.upper()
    if size_effect == "small":
        return word.lower()
    return word

def build_line(words, states, colors, sizes):
    parts = []
    for i, w in enumerate(words):
        st = states[i]
        col = colors[i]
        size = sizes[i]
        wtxt = apply_size_sim(w, size)
        if st == "done":
            r, g, b = col
            r = int(r * 0.5); g = int(g * 0.5); b = int(b * 0.5)
            parts.append(f"{rgb_ansi(r,g,b)}{wtxt}{RESET}")
        elif st == "current":
            r, g, b = col
            parts.append(f"{rgb_ansi(r,g,b)}\033[1m{wtxt}{RESET}")
        else:
            parts.append(f"\033[38;2;120;120;120m{wtxt}{RESET}")
    return " ".join(parts)

# ------------- PLAYER -------------
mp3_files = find_folder()
found_songs = find_song(mp3_files, SONG_NAME)
start_time = None

if found_songs:
    filepath = os.path.join(MUSIC_FOLDER, found_songs[0])
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        start_time = time.time()
    except Exception as e:
        print("Erreur pygame:", e)
        start_time = time.time()
else:
    print("Aucun fichier trouvé pour", SONG_NAME)
    start_time = time.time()

# ------------- PREPARE LYRICS -------------
lyrics_list = sorted(Song_lyrics.items(), key=lambda x: x[0])
if not lyrics_list:
    print("Aucune parole à afficher.")
else:
    total = len(lyrics_list)
    lyric_index = 0

    while lyric_index < total:
        current_time = time.time() - start_time
        next_time, next_lyric = lyrics_list[lyric_index]

        if current_time >= next_time:
            if lyric_index + 1 < total:
                next_line_time = lyrics_list[lyric_index + 1][0]
                duration = max(0.0, next_line_time - next_time)
            else:
                duration = DEFAULT_LAST_LINE_DUR

            words = [w for w in next_lyric.split() if w]
            n = len(words)
            if n == 0:
                lyric_index += 1
                print("")
                continue

            weights = [max(1, len(w)) for w in words]
            total_weight = sum(weights)
            per_word_durations = [max(MIN_WORD_DELAY, min(MAX_WORD_DELAY, duration * (w / total_weight))) for w in weights]

            colors = []
            sizes = []
            for _ in words:
                hue = random.random()
                r, g, b = hsv_to_rgb_i(hue, 0.8, 1.0)
                colors.append((r, g, b))
                sizes.append(random.choice(["small", "medium", "large"]))

            states = ["pending"] * n

            prev_print_len = 0
            line_base = " ".join(words)

            t_cursor = next_time
            for j, w in enumerate(words):
                wd = per_word_durations[j]
                if wd < MIN_WORD_DELAY:
                    wd = MIN_WORD_DELAY

                states[j] = "current"
                for k in range(0, j):
                    states[k] = "done"
                for k in range(j+1, n):
                    states[k] = "pending"

                steps = 3
                step_sleep = wd / steps if wd > 0 else MIN_WORD_DELAY
                if step_sleep < 0.01:
                    step_sleep = 0.01

                for s in range(steps):
                    factor = 0.4 + 0.6 * ((s + 1) / steps)
                    cr, cg, cb = colors[j]
                    cr_s = int(cr * factor); cg_s = int(cg * factor); cb_s = int(cb * factor)
                    colors_for_display = []
                    for idx in range(n):
                        if idx == j:
                            colors_for_display.append((cr_s, cg_s, cb_s))
                        else:
                            colors_for_display.append(colors[idx])
                    display_line = build_line(words, states, colors_for_display, sizes)
                    print("\r" + display_line + " " * max(0, prev_print_len - len(display_line)), end="", flush=True)
                    prev_print_len = len(display_line)
                    now = time.time() - start_time
                    target = t_cursor + (s + 1) * step_sleep
                    sleep_for = target - now
                    if sleep_for > 0:
                        time.sleep(sleep_for)
                states[j] = "done"
                t_cursor += wd

            print("")
            lyric_index += 1
        else:
            to_sleep = next_time - current_time
            time.sleep(max(0.01, min(0.15, to_sleep)))