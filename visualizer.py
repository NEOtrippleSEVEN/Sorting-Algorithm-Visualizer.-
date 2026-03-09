#!/usr/bin/env python3
import sys
import subprocess
import curses
import time

DELAY   = 0.06
BAR_MAX = 18

OP_COLORS = {
	'pa': 3, 'pb': 3,
	'ra': 4, 'rb': 4, 'rr': 4,
	'rra': 5, 'rrb': 5, 'rrr': 5,
	'sa': 6, 'sb': 6, 'ss': 6,
}

def get_ops(nums):
	r = subprocess.run(
		['./push_swap'] + [str(n) for n in nums],
		capture_output=True, text=True
	)
	return [o for o in r.stdout.strip().split('\n') if o]

def apply_op(op, a, b):
	if   op == 'sa'  and len(a) >= 2: a[0], a[1] = a[1], a[0]
	elif op == 'sb'  and len(b) >= 2: b[0], b[1] = b[1], b[0]
	elif op == 'ss':
		if len(a) >= 2: a[0], a[1] = a[1], a[0]
		if len(b) >= 2: b[0], b[1] = b[1], b[0]
	elif op == 'pa'  and b: a.insert(0, b.pop(0))
	elif op == 'pb'  and a: b.insert(0, a.pop(0))
	elif op == 'ra'  and a: a.append(a.pop(0))
	elif op == 'rb'  and b: b.append(b.pop(0))
	elif op == 'rr':
		if a: a.append(a.pop(0))
		if b: b.append(b.pop(0))
	elif op == 'rra' and a: a.insert(0, a.pop())
	elif op == 'rrb' and b: b.insert(0, b.pop())
	elif op == 'rrr':
		if a: a.insert(0, a.pop())
		if b: b.insert(0, b.pop())

def build_states(nums, ops):
	states = [{'a': list(nums), 'b': [], 'op': 'start'}]
	a, b = list(nums), []
	for op in ops:
		apply_op(op, a, b)
		states.append({'a': list(a), 'b': list(b), 'op': op})
	return states

def bar_len(val, min_v, max_v):
	if max_v == min_v:
		return BAR_MAX // 2
	return max(1, int((val - min_v) / (max_v - min_v) * BAR_MAX))

def draw(stdscr, state, step, total, min_v, max_v, scroll, playing, elapsed):
	stdscr.erase()
	h, w = stdscr.getmaxyx()
	a, b, op = state['a'], state['b'], state['op']
	mid = w // 2

	# header
	status = ' ▶ ' if playing else ' ⏸ '
	try:
		stdscr.addstr(0, 0, f" step {step:>5}/{total}", curses.A_BOLD)
		stdscr.addstr(0, 14, f" {op:<5}", curses.color_pair(OP_COLORS.get(op, 7)) | curses.A_BOLD)
		stdscr.addstr(0, 20, status, curses.A_DIM)
		stdscr.addstr(0, 24, f" {elapsed:.1f}s", curses.A_DIM)
	except curses.error:
		pass

	# column labels
	try:
		stdscr.addstr(1, 2,     f"stack_a ({len(a):3d})", curses.color_pair(1) | curses.A_BOLD)
		stdscr.addstr(1, mid+2, f"stack_b ({len(b):3d})", curses.color_pair(2) | curses.A_BOLD)
	except curses.error:
		pass

	# stack rows
	height      = max(len(a), len(b), 1)
	display_rows = h - 4
	view_end    = min(height, scroll + display_rows)

	for screen_i, i in enumerate(range(scroll, view_end)):
		row = screen_i + 2
		if row >= h - 1:
			break
		if i < len(a):
			attr = curses.color_pair(1) | (curses.A_BOLD if i == 0 else 0)
			line = f"  {a[i]:>7}  {'█' * bar_len(a[i], min_v, max_v)}"
			try:
				stdscr.addstr(row, 0, line[:mid - 1], attr)
			except curses.error:
				pass
		if i < len(b):
			attr = curses.color_pair(2) | (curses.A_BOLD if i == 0 else 0)
			line = f"  {b[i]:>7}  {'█' * bar_len(b[i], min_v, max_v)}"
			try:
				stdscr.addstr(row, mid, line[:w - mid - 1], attr)
			except curses.error:
				pass

	# footer
	try:
		foot = " ←→ step   ↑↓ scroll   space play/pause   q quit"
		stdscr.addstr(h - 1, 0, foot[:w - 1], curses.A_DIM)
	except curses.error:
		pass

	stdscr.refresh()

def main_loop(stdscr, states, min_v, max_v, delay):
	curses.start_color()
	curses.use_default_colors()
	curses.init_pair(1, curses.COLOR_CYAN,    -1)
	curses.init_pair(2, curses.COLOR_YELLOW,  -1)
	curses.init_pair(3, curses.COLOR_GREEN,   -1)
	curses.init_pair(4, curses.COLOR_BLUE,    -1)
	curses.init_pair(5, curses.COLOR_MAGENTA, -1)
	curses.init_pair(6, curses.COLOR_RED,     -1)
	curses.init_pair(7, curses.COLOR_WHITE,   -1)
	curses.curs_set(0)
	stdscr.nodelay(True)
	stdscr.keypad(True)

	total      = len(states) - 1
	step       = 0
	scroll     = 0
	playing    = True
	last_tick  = time.time()
	start_time = time.time()

	while True:
		elapsed = time.time() - start_time
		draw(stdscr, states[step], step, total, min_v, max_v, scroll, playing, elapsed)
		key = stdscr.getch()

		if key == ord('q'):
			break
		elif key == curses.KEY_RIGHT and step < total:
			step  += 1
			scroll = 0
		elif key == curses.KEY_LEFT and step > 0:
			step  -= 1
			scroll = 0
		elif key == ord(' '):
			playing = not playing
		elif key == curses.KEY_UP:
			scroll = max(0, scroll - 1)
		elif key == curses.KEY_DOWN:
			h, _   = stdscr.getmaxyx()
			height = max(len(states[step]['a']), len(states[step]['b']), 1)
			scroll = min(max(0, height - (h - 4)), scroll + 1)

		now = time.time()
		if playing and now - last_tick >= delay:
			if step < total:
				step  += 1
				scroll = 0
			else:
				playing = False
			last_tick = now

		time.sleep(0.005)

if __name__ == '__main__':
	fast = '--fast' in sys.argv
	args = [x for x in sys.argv[1:] if x != '--fast']
	if not args:
		print("Usage: python3 visualizer.py <numbers> [--fast]")
		sys.exit(1)
	try:
		nums = list(map(int, args))
	except ValueError:
		print("All arguments must be integers")
		sys.exit(1)
	ops    = get_ops(nums)
	states = build_states(nums, ops)
	curses.wrapper(main_loop, states, min(nums), max(nums), 0.02 if fast else DELAY)
