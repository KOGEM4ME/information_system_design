"""
Rhythm Dash — 縦スクロール音楽ゲーム（上方向）
操作: A/← 左  D/→ 右  R リスタート  E エディター切替
エディター: クリック=コイン  Shift=三角  Ctrl=ブロック  Alt=スパイク  右クリック=削除
"""

import sys
import math
import random
import array

# pygame は init より前に Sound を使わない
import pygame

# ── 初期化 ────────────────────────────────────────────
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

W, H    = 600, 480
COLS    = 12
CELL    = W // COLS   # 50px
ROW_H   = 40
FPS     = 60
PLAYER_SCREEN_Y = H - ROW_H * 2

BG = (10, 10, 26)

COL_COLORS = [
    (231, 76,  60),(230,126, 34),(241,196, 15),( 46,204,113),
    ( 26,188,156),( 52,152,219),(155, 89,182),(253,121,168),
    (  0,184,148),(253,203,110),(108, 92,231),(  0,206,201),
]

NOTE_FREQS = [261.63,277.18,293.66,311.13,329.63,349.23,
              369.99,392.00,415.30,440.00,466.16,493.88]

# ── 音声生成（numpy なしでも動く） ───────────────────
def _make_wave(freq, dur=0.4, vol=0.35):
    sr  = 44100
    n   = int(sr * dur)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t      = i / sr
        env    = math.exp(-6 * t)
        sample = env * vol * math.sin(2 * math.pi * freq * t)
        buf[i] = max(-32768, min(32767, int(sample * 32767)))
    return buf

def _make_noise(dur=0.25, vol=0.3):
    sr  = 44100
    n   = int(sr * dur)
    buf = array.array('h', [0] * n)
    for i in range(n):
        t      = i / sr
        env    = math.exp(-10 * t)
        sample = env * vol * random.uniform(-1, 1)
        buf[i] = max(-32768, min(32767, int(sample * 32767)))
    return buf

def _buf_to_sound(buf):
    # numpy があれば速い
    try:
        import numpy as np
        arr = np.array(buf, dtype='int16')
        return pygame.sndarray.make_sound(arr)
    except Exception:
        pass
    # fallback: bytes経由
    raw = bytes(buf)
    snd = pygame.mixer.Sound(buffer=raw)
    return snd

COIN_SOUNDS = [_buf_to_sound(_make_wave(f)) for f in NOTE_FREQS]
HIT_SOUND   = _buf_to_sound(_make_noise())

def play_coin(col):
    try: COIN_SOUNDS[col % 12].play()
    except Exception: pass

def play_hit():
    try: HIT_SOUND.play()
    except Exception: pass

# ── ワールド生成 ──────────────────────────────────────
CHUNK    = 20
PATTERNS = ['random','wall_gap','zigzag','corridor','rain']
chunks   = {}

def get_chunk(ci):
    if ci in chunks:
        return chunks[ci]
    rows = []
    pat  = PATTERNS[abs(ci) % len(PATTERNS)]
    cz   = random.randint(0, COLS - 3)
    zc   = random.randint(0, COLS - 1)
    zd   = 1
    for r in range(CHUNK):
        row    = [None] * COLS
        absrow = ci * CHUNK + r
        if abs(absrow) < 6:
            rows.append(row); continue

        if pat == 'random':
            for c in range(COLS):
                v = random.random()
                if   v < 0.07: row[c] = 'coin'
                elif v < 0.12: row[c] = 'triangle'
                elif v < 0.16: row[c] = 'block'
                elif v < 0.19: row[c] = 'spike_l'
                elif v < 0.22: row[c] = 'spike_r'

        elif pat == 'wall_gap':
            if r % 4 == 0:
                for c in range(COLS):
                    row[c] = 'triangle' if (c < 3 or c > COLS-4) else None
                gap = random.randint(3, COLS-5)
                row[gap] = 'coin'
            elif r % 4 == 2:
                for c in range(COLS):
                    if random.random() < 0.08: row[c] = 'coin'

        elif pat == 'zigzag':
            if r % 3 == 0:
                for c in range(COLS):
                    if c not in (zc, zc+1):
                        row[c] = 'triangle' if random.random()<0.4 else 'block'
                row[zc] = 'coin'
                zc += zd * random.randint(1,2)
                if zc >= COLS-1: zc,zd = COLS-2,-1
                if zc <= 0:      zc,zd = 1, 1
            else:
                for c in range(COLS):
                    if random.random()<0.06: row[c] = 'coin'

        elif pat == 'corridor':
            for c in range(COLS):
                if c < cz or c > cz+2:
                    row[c] = 'block' if random.random()<0.6 else 'triangle'
            if r % 5 == 0:
                cz += random.choice([-1,1])
                cz  = max(0, min(COLS-3, cz))
            row[cz+1] = 'coin'

        elif pat == 'rain':
            for c in range(COLS):
                v = random.random()
                if   v < 0.11: row[c] = 'triangle'
                elif v < 0.15: row[c] = 'coin'
                elif v < 0.18: row[c] = 'spike_l'
                elif v < 0.21: row[c] = 'spike_r'

        rows.append(row)
    chunks[ci] = rows
    return rows

def _chunk_row(wr):
    ci = wr // CHUNK
    ri = wr  % CHUNK
    if ri < 0: ci -= 1; ri += CHUNK
    return ci, ri

def get_cell(wr, col):
    ci,ri = _chunk_row(wr)
    return get_chunk(ci)[ri][col]

def set_cell(wr, col, val):
    ci,ri = _chunk_row(wr)
    get_chunk(ci)[ri][col] = val

# ── 描画 ──────────────────────────────────────────────
def draw_cell(surf, cell, col, px, py):
    cx, cy = px + CELL//2, py + ROW_H//2
    if cell == 'coin':
        c = COL_COLORS[col % 12]
        pygame.draw.circle(surf, c, (cx, cy), 10)
        pygame.draw.circle(surf, (255,255,255), (cx, cy), 10, 1)
    elif cell == 'triangle':
        pts = [(cx, py+4),(px+CELL-4, py+ROW_H-4),(px+4, py+ROW_H-4)]
        pygame.draw.polygon(surf, (231,76,60), pts)
        pygame.draw.polygon(surf, (255,107,107), pts, 2)
    elif cell == 'block':
        r = pygame.Rect(px+3, py+3, CELL-6, ROW_H-6)
        pygame.draw.rect(surf, (99,110,114), r)
        pygame.draw.rect(surf, (178,190,195), r, 1)
    elif cell == 'spike_l':
        pts = [(px+4,cy),(px+CELL-4,py+5),(px+CELL-4,py+ROW_H-5)]
        pygame.draw.polygon(surf, (162,155,254), pts)
        pygame.draw.polygon(surf, (108,92,231), pts, 2)
    elif cell == 'spike_r':
        pts = [(px+CELL-4,cy),(px+4,py+5),(px+4,py+ROW_H-5)]
        pygame.draw.polygon(surf, (253,121,168), pts)
        pygame.draw.polygon(surf, (232,67,147), pts, 2)

# ── ゲーム状態 ────────────────────────────────────────
class Game:
    def reset(self):
        self.score      = 0
        self.hi         = getattr(self, 'hi', 0)
        self.player_col = 5
        self.world_px   = 0.0    # 上方向に増加するピクセル座標
        self.speed      = 120.0  # px/秒
        self.alive      = True
        self.editor     = False
        global chunks
        chunks = {}

    def player_world_row(self):
        return int(self.world_px // ROW_H)

    def world_row_at_screen_y(self, sy):
        wy = self.world_px - (sy - PLAYER_SCREEN_Y)
        return int(wy // ROW_H)

g = Game()
g.reset()

font_big = pygame.font.SysFont(None, 36)
font_med = pygame.font.SysFont(None, 24)
font_sm  = pygame.font.SysFont(None, 20)

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Rhythm Dash ▲")
clock  = pygame.time.Clock()

move_left  = False
move_right = False
move_timer = 0.0
MOVE_INTERVAL = 0.12

def handle_move(dt):
    global move_timer
    move_timer -= dt
    if move_timer > 0: return
    if move_left:
        nc = max(0, g.player_col - 1)
        if get_cell(g.player_world_row(), nc) != 'block':
            g.player_col = nc; move_timer = MOVE_INTERVAL
    elif move_right:
        nc = min(COLS-1, g.player_col + 1)
        if get_cell(g.player_world_row(), nc) != 'block':
            g.player_col = nc; move_timer = MOVE_INTERVAL

# ── メインループ ──────────────────────────────────────
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_a, pygame.K_LEFT):
                move_left = True; move_timer = 0.0
            if ev.key in (pygame.K_d, pygame.K_RIGHT):
                move_right = True; move_timer = 0.0
            if ev.key == pygame.K_r:
                g.reset(); move_left = move_right = False
            if ev.key == pygame.K_e:
                g.editor = not g.editor
        elif ev.type == pygame.KEYUP:
            if ev.key in (pygame.K_a, pygame.K_LEFT):  move_left  = False
            if ev.key in (pygame.K_d, pygame.K_RIGHT): move_right = False
        elif ev.type == pygame.MOUSEBUTTONDOWN and g.editor:
            mx, my = ev.pos
            col = mx // CELL
            wr  = g.world_row_at_screen_y(my)
            if 0 <= col < COLS:
                mods = pygame.key.get_mods()
                if   ev.button == 3:             set_cell(wr, col, None)
                elif mods & pygame.KMOD_SHIFT:   set_cell(wr, col, 'triangle')
                elif mods & pygame.KMOD_CTRL:    set_cell(wr, col, 'block')
                elif mods & pygame.KMOD_ALT:     set_cell(wr, col, random.choice(['spike_l','spike_r']))
                else:                            set_cell(wr, col, 'coin')

    # 更新
    if g.alive and not g.editor:
        handle_move(dt)
        g.world_px += g.speed * dt
        g.speed     = 120.0 + g.score * 1.5

        wr   = g.player_world_row()
        cell = get_cell(wr, g.player_col)
        if cell == 'coin':
            g.score += 1
            if g.score > g.hi: g.hi = g.score
            set_cell(wr, g.player_col, None)
            play_coin(g.player_col)
        elif cell in ('triangle','spike_l','spike_r'):
            g.alive = False
            play_hit()

    # 描画
    screen.fill(BG)

    for c in range(1, COLS):
        pygame.draw.line(screen, (30,30,50), (c*CELL,0), (c*CELL,H))

    # 列カラーヒント
    col_hint = pygame.Surface((CELL, ROW_H*2), pygame.SRCALPHA)
    for c in range(COLS):
        col_hint.fill((0,0,0,0))
        r2,g2,b2 = COL_COLORS[c]
        col_hint.fill((r2,g2,b2,18))
        screen.blit(col_hint, (c*CELL, H-ROW_H*2))

    # セル描画（連続座標）
    sub = g.world_px % ROW_H
    base_wr = g.player_world_row()
    for dr in range(-1, int(H/ROW_H)+3):
        wr = base_wr + dr
        wy_top = wr * ROW_H
        sy = int(PLAYER_SCREEN_Y - (wy_top - g.world_px))
        if sy > H + ROW_H or sy < -ROW_H*2: continue
        for col in range(COLS):
            cell = get_cell(wr, col)
            if cell:
                draw_cell(screen, cell, col, col*CELL, sy)

    # プレイヤー
    px2 = g.player_col * CELL
    py2 = PLAYER_SCREEN_Y
    pygame.draw.rect(screen, (52,152,219), (px2+4,py2+4,CELL-8,ROW_H-8), border_radius=5)
    pygame.draw.rect(screen, (116,185,255),(px2+4,py2+4,CELL-8,ROW_H-8), 2, border_radius=5)
    star = font_med.render("★", True, (255,255,255))
    screen.blit(star, star.get_rect(center=(px2+CELL//2, py2+ROW_H//2)))

    # HUD
    hud = font_med.render(f"スコア: {g.score}  ハイスコア: {g.hi}  列: {g.player_col+1}", True, (178,190,195))
    screen.blit(hud, (8,8))
    hint = font_sm.render("A/← 左  D/→ 右  R リスタート  E エディター", True, (60,65,80))
    screen.blit(hint, (8, H-20))

    if g.editor:
        ov = pygame.Surface((W,30), pygame.SRCALPHA)
        ov.fill((0,0,0,160))
        screen.blit(ov,(0,30))
        etxt = font_sm.render("エディター | クリック:コイン  Shift:三角  Ctrl:ブロック  Alt:スパイク  右クリック:削除", True, (220,230,233))
        screen.blit(etxt,(8,38))

    if not g.alive and not g.editor:
        ov = pygame.Surface((W,120), pygame.SRCALPHA)
        ov.fill((0,0,0,190))
        screen.blit(ov,(0,H//2-60))
        t1 = font_big.render("GAME OVER", True, (231,76,60))
        t2 = font_med.render(f"スコア: {g.score}   ハイスコア: {g.hi}", True, (178,190,195))
        t3 = font_sm.render("R キーで再挑戦", True, (99,110,114))
        screen.blit(t1, t1.get_rect(center=(W//2, H//2-20)))
        screen.blit(t2, t2.get_rect(center=(W//2, H//2+12)))
        screen.blit(t3, t3.get_rect(center=(W//2, H//2+38)))

    pygame.display.flip()

pygame.quit()
sys.exit()
