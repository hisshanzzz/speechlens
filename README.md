# SpeechLens
<img width="952" height="1122" alt="Speech Lens Demo" src="https://github.com/user-attachments/assets/e0c99435-572e-4f9a-87d9-3aafa2204a55" />



A small Python tool I built to check speech scripts before I coach students at English Pro Hub.

Paste a `.txt` file with your speech. It tells you:
- roughly how long it will take to deliver
- whether you fit the Toastmasters 5-7 minute window (or any window you set)
- filler words like "um", "you know", "basically"
- whether sentences are easy to follow when spoken aloud

No extra libraries. Just Python 3.8+.

## Why I made this

I judge speech contests and coach students for English Day competitions. Most speakers lose points for the same three things: going over time, too many fillers, and sentences that look fine on paper but sound heavy when spoken.

I kept doing this review by hand. SpeechLens does the first pass for me in one second.

## Try it

```bash
git clone https://github.com/hisshanzzz/speechlens.git
cd speechlens
py -m speechlens samples/icebreaker.txt --target 4-6
```

On Windows you may need `py` instead of `python`.

## Commands

```bash
# Standard Toastmasters window (5-7 min)
py -m speechlens myspeech.txt

# Ice Breaker window (4-6 min)
py -m speechlens samples/icebreaker.txt --target 4-6

# If you speak faster (145 words per minute)
py -m speechlens myspeech.txt --wpm 145

# Save numbers to a JSON file
py -m speechlens myspeech.txt --json report.json
```

## What it checks

| Feature | What it means |
|---------|---------------|
| Delivery time | word count divided by your speaking speed |
| Timing check | under / on target / over your minute window |
| Filler words | counts "um", "uh", "you know", etc. |
| Reading ease | Flesch score — higher = easier to listen to |
| Vocabulary richness | how many unique words vs total words |
| Most repeated words | skips boring words like "the" and "and" |

## Project layout

```
speechlens/
    speechlens/
        analyzer.py    # does the maths
        report.py      # prints the report
        cli.py         # reads command-line arguments
        __main__.py    # lets you run: py -m speechlens
    samples/           # two speeches to test with
    tests/             # 24 unit tests
```

## Tests

```bash
py -m unittest discover tests -v
```

## What's next

- [ ] Sinhala and Tamil filler words
- [ ] Per-paragraph timing for rehearsal
- [ ] Simple web page so students do not need the terminal

## About me

Mohamed Jaufer Mohamed Hisshan — AI & Data Science undergrad (RGU), Toastmaster, speech adjudicator, founder of English Pro Hub.

- LinkedIn: https://www.linkedin.com/in/mohamed-jaufer-mohamed-hisshan-31399525b
- YouTube: https://www.youtube.com/@hisshanspeaks6063

