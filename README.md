# push_swap

Sorts a stack of integers using two stacks (a, b) and a limited set of operations: `sa sb ss pa pb ra rb rr rra rrb rrr`.

## Build

```bash
make
```

## Visualizer

Interactive terminal visualizer built with curses. Stack A is **cyan**, stack B is **yellow**. The current operation is colour-coded by type:

| Colour  | Operations       |
|---------|-----------------|
| Green   | `pa` `pb`        |
| Blue    | `ra` `rb` `rr`   |
| Magenta | `rra` `rrb` `rrr`|
| Red     | `sa` `sb` `ss`   |

```bash
python3 visualizer.py 3 1 5 2 4
python3 visualizer.py 3 1 5 2 4 --fast
```

### Controls

| Key        | Action                        |
|------------|-------------------------------|
| `space`    | Play / pause                  |
| `→` / `←` | Step forward / backward       |
| `↑` / `↓` | Scroll stack view up / down   |
| `q`        | Quit                          |

## Generating test numbers

```bash
# 5 numbers (small test)
python3 -c "import random; print(*random.sample(range(-100, 101), 5))"

# 100 numbers
python3 -c "import random; print(*random.sample(range(-500, 501), 100))"

# 500 numbers
python3 -c "import random; print(*random.sample(range(-1000, 1001), 500))"

# pipe directly into push_swap and count operations
ARG=$(python3 -c "import random; print(*random.sample(range(-1000,1001), 500))")
./push_swap $ARG | wc -l

# pipe directly into visualizer
python3 visualizer.py $(python3 -c "import random; print(*random.sample(range(-100,101), 20))")
```
