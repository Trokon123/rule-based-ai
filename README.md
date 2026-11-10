# 2.3 Building a Rule-Based AI System with Python

**Student:** Trokon Reeves
**Project:** Wi-Fi & Internet Troubleshooting Assistant

## How to run

```bash
python3 tech_support_bot.py
```

No packages need to be installed. The program uses only the Python standard library (see `requirements.txt`).

## Part 1: Three initial project ideas

I asked an AI assistant (Claude) to suggest rule-based AI project ideas. These are the three I wrote down.

| # | Idea | What the system does | How it would work using rules |
|---|------|----------------------|-------------------------------|
| 1 | Wi-Fi and internet troubleshooting assistant | The user describes a connection problem in plain English and the system gives a diagnosis and numbered steps to fix it. | Keyword lists for each kind of problem (slow, dropping, password, router lights). An if/elif/else chain picks the first matching problem, and yes/no follow-up questions narrow it down. |
| 2 | Recipe recommender | The user types the ingredients they have and the system suggests a dish they can make. | Each recipe has a required ingredient list. IF every required ingredient is in the user's input THEN recommend that recipe, ELSE suggest the recipe with the fewest missing items. |
| 3 | Study-habit advisor chatbot | The user says what they are struggling with (procrastination, test anxiety, time management) and the bot replies with a study tip. | Keyword matching in the style of ELIZA. IF the input contains "procrastinate" THEN give the tip about breaking work into 25-minute blocks, and so on, with a default reply when nothing matches. |

**Chosen idea: the Wi-Fi and internet troubleshooting assistant.** I chose it because it is closest to the expert systems from the lecture, such as MYCIN, where a knowledge base of facts is combined with rules that reach a diagnosis. Troubleshooting is also a problem where the order of the questions matters, so it lets me show nested rules and follow-up questions instead of only one keyword per answer. It is also something I would use myself.

## Part 2: Rules and logic for the chosen system

Before any rule runs, the input is lowercased, hyphens and punctuation are removed, and the text is split into a set of words. For example, `"My Wi-Fi isn't working!"` becomes `{my, wifi, isnt, working}`.

The rules are checked from top to bottom and the first match wins. Specific problems come before general ones.

```
RULE 0  IF input is empty                      THEN ask the user to describe the problem
RULE 0  IF input contains quit/exit/bye        THEN say goodbye and stop the program

RULE 1  IF input is a short greeting (hi, hello, hey)
        THEN greet the user and ask what is wrong

RULE 2  IF input is a short request for help (help, menu, options)
        THEN list the problems the bot can handle

RULE 3  IF input contains password/passcode/forgot/login
        THEN diagnosis = Wi-Fi password problem (check sticker, admin page, reset)

RULE 4  IF input contains router/modem/light/blinking/red/orange
        THEN ASK "Have you already restarted the router?"
             IF yes THEN diagnosis = outage or failing router (check cable, outage map, call provider)
             ELSE        diagnosis = router needs a restart (power-cycle steps)

RULE 5  IF input contains drops/dropping/disconnects/unstable/intermittent
        THEN diagnosis = unstable signal (move closer, avoid interference, use 5 GHz)

RULE 6  IF input contains slow/lag/buffering/sluggish
        THEN ASK "Is it slow on every device?"
             IF yes THEN diagnosis = whole network congested (restart router, speed test)
             ELSE        diagnosis = problem on one device (close apps, restart device)

RULE 7  IF input contains a negative word (no, not, cant, isnt, down, offline ...)
        AND input contains a connection word (internet, wifi, connect, network ...)
        THEN IF input names one device (phone, laptop, tv ...)
                  THEN diagnosis = one device cannot connect (toggle Wi-Fi, forget network)
             ELSE      diagnosis = no internet connection (check power, restart, outage map)

RULE 8  ELSE (nothing matched)
        THEN say "I'm not sure I understand" and suggest keywords
```

**Why this order:** "I forgot my wifi password" contains the word *wifi*, so if the general connection rule came first the bot would give the wrong answer. Putting the password rule earlier fixes that. The greeting and help rules only fire on inputs of three words or fewer, so "hey my internet is slow" still reaches the slow-internet rule.

## Part 3: Code

See `tech_support_bot.py`. It is organised into small functions:

- `normalize()` cleans the input and turns it into a set of words.
- `has_any()` checks whether the input shares a word with a keyword list.
- `ask_yes_no()` asks a follow-up question and repeats until it gets yes or no.
- `diagnose()` holds the if/elif/else rules (the inference engine).
- `main()` runs the conversation loop with `input()`.

## Test cases: results of three inputs

Each test was run with `python3 tech_support_bot.py`.

### Test 1: slow internet with a follow-up question (Rule 6)

```
You: My internet is really slow
Is it slow on every device in the house? (yes/no): yes
Bot: Diagnosis: the whole network is congested.
  1. Restart the router.
  2. Pause large downloads and streaming on other devices.
  3. Run a speed test. If it is far below your plan, call your provider.
```

**Why:** "slow" matched the slow-internet keywords, and answering "yes" selected the whole-network branch. Result: as expected.

### Test 2: forgotten password, checking rule priority (Rule 3)

```
You: I forgot my wifi password
Bot: Diagnosis: Wi-Fi password problem.
  1. Check the sticker on the back or bottom of the router.
  2. If it was changed, log in to the router admin page to view it.
  3. As a last resort, hold the reset button for 10 seconds to restore the default password printed on the sticker.
```

**Why:** the input contains both "wifi" and "password". The password rule is checked before the connection rule, so the bot gives the password answer. Result: as expected.

### Test 3: one device cannot connect, nested rule (Rule 7)

```
You: My laptop will not connect to the wifi
Bot: Diagnosis: one device cannot connect.
  1. Turn Wi-Fi off and on again on that device.
  2. Forget the network and re-enter the password.
  3. Restart the device.
```

**Why:** "not" is a negative word and "connect"/"wifi" are connection words, so Rule 7 fired. The word "laptop" then selected the single-device branch. Result: as expected.

### Extra test: input the rules do not cover (Rule 8)

```
You: what is the weather
Bot: I'm not sure I understand. Try words like 'slow', 'no internet', 'keeps dropping', 'password', or 'router light'. Type 'help' for options.
```

**Why:** no keyword matched, so the default rule answered instead of guessing. Result: as expected.

## Part 4: Reflection

My system is a troubleshooting assistant for Wi-Fi and internet problems. It works in three steps. First it takes what the user typed, makes it lowercase, removes punctuation, and splits it into a set of words. Second it compares those words with keyword lists that act as its knowledge base, one list for each kind of problem. Third it runs an if/elif/else chain, and the first rule that matches decides the diagnosis. For slow internet and router lights it asks a yes/no follow-up question, and a second layer of rules uses that answer to choose between two possible causes. If nothing matches, a default rule says it does not understand.

The biggest challenge in working with the AI was rule order. A sentence like "I forgot my wifi password" contains the word "wifi", so if the general "no connection" rule is checked first the bot gives connection advice for a password problem. The design had to put the specific rules ahead of the general ones, and the greeting rule had to be limited to short inputs so "hey my internet is slow" was not treated as a greeting. A second problem showed up in testing: "My Wi-Fi isn't working" fell through to the default answer, because removing the apostrophe turns "isn't" into "isnt", which was not in the keyword list. The fix was to add more words by hand.

That second problem taught me the most about rule-based AI. The bot does not understand anything. It only reacts to the exact words I prepared it for, which is the same brittleness the lecture described in expert systems like MYCIN and in ELIZA. Every new phrasing needs a person to add a rule. A modern machine learning system would instead learn patterns from thousands of example sentences and could handle wording nobody planned for. The trade-off is that my system is fully predictable, and I can point to the exact rule behind every answer.
