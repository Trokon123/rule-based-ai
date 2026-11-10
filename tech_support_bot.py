"""
Wi-Fi & Internet Troubleshooting Assistant
A rule-based AI system (no machine learning).

How it works:
  1. The user describes a problem in plain English (input()).
  2. The text is cleaned up and split into words (normalize()).
  3. A chain of if / elif / else rules checks the words for keywords.
  4. The first rule that matches decides the diagnosis and the advice.
  5. For some problems the bot asks a follow-up yes/no question and
     uses a second layer of rules to narrow the answer down.

This is the same idea as early "expert systems" such as MYCIN:
a knowledge base of facts (the keyword lists) plus an inference
engine (the if/elif/else rules) that applies logic to those facts.
"""

import string

# ---------------------------------------------------------------------------
# KNOWLEDGE BASE
# Each set holds the keywords that signal one kind of problem.
# The rules below only look at these lists, so the bot can be taught new
# vocabulary by adding a word here without touching the logic.
# ---------------------------------------------------------------------------
GREETING_WORDS = {"hi", "hello", "hey"}
EXIT_WORDS = {"quit", "exit", "bye", "goodbye"}
HELP_WORDS = {"help", "menu", "options"}

PASSWORD_WORDS = {"password", "passcode", "forgot", "login", "credentials"}
NO_CONNECTION_WORDS = {"no", "not", "cant", "cannot", "wont", "unable", "down", "offline",
                       "isnt", "doesnt", "stopped"}
CONNECTION_WORDS = {"internet", "wifi", "connect", "connection", "connected", "online", "network"}
SLOW_WORDS = {"slow", "lag", "lagging", "laggy", "buffering", "buffer", "sluggish"}
DROPPING_WORDS = {"drops", "dropping", "disconnects", "disconnecting", "unstable", "cuts", "intermittent"}
ROUTER_WORDS = {"router", "modem", "light", "lights", "blinking", "red", "orange"}
ONE_DEVICE_WORDS = {"phone", "laptop", "tablet", "tv", "computer", "pc", "printer"}

YES_WORDS = {"yes", "y", "yeah", "yep", "sure"}
NO_WORDS = {"no", "n", "nope", "nah"}


def normalize(text):
    """Lowercase the text, strip punctuation, and return a set of words.

    "My Wi-Fi isn't working!" -> {"my", "wifi", "isnt", "working"}
    Using a set makes each rule a simple "do these share any word?" check.
    """
    text = text.lower().replace("-", "")            # "wi-fi" -> "wifi"
    text = text.translate(str.maketrans("", "", string.punctuation))
    return set(text.split())


def has_any(words, keywords):
    """Return True if the user's words contain at least one keyword."""
    return len(words & keywords) > 0


def ask_yes_no(question):
    """Ask a follow-up question until the user answers yes or no."""
    while True:
        answer = normalize(input(question + " (yes/no): "))
        if has_any(answer, YES_WORDS):
            return True
        if has_any(answer, NO_WORDS):
            return False
        print("Bot: Please answer yes or no.")


def diagnose(words, ask=ask_yes_no):
    """THE INFERENCE ENGINE: apply the rules in priority order.

    Order matters. The most specific rules are checked first so that a
    general rule (like "internet") does not swallow a specific problem
    (like "forgot my wifi password").

    `ask` is the function used for follow-up questions. It is a parameter
    so the automated tests can answer the questions without a keyboard.
    """
    # RULE 1: greeting -> introduce the bot
    if has_any(words, GREETING_WORDS) and len(words) <= 3:
        return "Hello! Tell me what is wrong with your internet or Wi-Fi."

    # RULE 2: help -> list what the bot can handle
    elif has_any(words, HELP_WORDS) and len(words) <= 3:
        return ("I can help with: no connection, slow internet, a connection "
                "that keeps dropping, a forgotten Wi-Fi password, or router "
                "warning lights. Describe your problem in a sentence.")

    # RULE 3: forgotten password -> where to find or reset it
    elif has_any(words, PASSWORD_WORDS):
        return ("Diagnosis: Wi-Fi password problem.\n"
                "  1. Check the sticker on the back or bottom of the router.\n"
                "  2. If it was changed, log in to the router admin page to view it.\n"
                "  3. As a last resort, hold the reset button for 10 seconds to "
                "restore the default password printed on the sticker.")

    # RULE 4: router lights -> hardware or provider problem
    elif has_any(words, ROUTER_WORDS):
        # Follow-up rule: does a restart clear the warning light?
        if ask("Have you already unplugged the router for 30 seconds and plugged it back in?"):
            return ("Diagnosis: likely an outage or a failing router.\n"
                    "  1. Check that the cable from the wall is tight.\n"
                    "  2. Look up your provider's outage map.\n"
                    "  3. If there is no outage, call your provider. The router may need replacing.")
        else:
            return ("Diagnosis: router needs a restart.\n"
                    "  1. Unplug the router and modem for 30 seconds.\n"
                    "  2. Plug the modem in first, wait 2 minutes, then the router.\n"
                    "  3. If the warning light comes back, run me again and answer yes.")

    # RULE 5: connection keeps dropping -> signal or interference
    elif has_any(words, DROPPING_WORDS):
        return ("Diagnosis: unstable Wi-Fi signal.\n"
                "  1. Move closer to the router and test again.\n"
                "  2. Keep the router away from microwaves and thick walls.\n"
                "  3. Switch to the 5 GHz network if you are in the same room.\n"
                "  4. Update the router firmware.")

    # RULE 6: slow internet -> congestion or distance
    elif has_any(words, SLOW_WORDS):
        # Follow-up rule: one device or all of them?
        if ask("Is it slow on every device in the house?"):
            return ("Diagnosis: the whole network is congested.\n"
                    "  1. Restart the router.\n"
                    "  2. Pause large downloads and streaming on other devices.\n"
                    "  3. Run a speed test. If it is far below your plan, call your provider.")
        else:
            return ("Diagnosis: the problem is on that one device.\n"
                    "  1. Close unused apps and browser tabs.\n"
                    "  2. Restart the device.\n"
                    "  3. Move it closer to the router.")

    # RULE 7: no connection at all (needs a negative word AND a connection word)
    elif has_any(words, NO_CONNECTION_WORDS) and has_any(words, CONNECTION_WORDS):
        # Nested rule: if a single device is named, treat it as a device problem
        if has_any(words, ONE_DEVICE_WORDS):
            return ("Diagnosis: one device cannot connect.\n"
                    "  1. Turn Wi-Fi off and on again on that device.\n"
                    "  2. Forget the network and re-enter the password.\n"
                    "  3. Restart the device.")
        else:
            return ("Diagnosis: no internet connection.\n"
                    "  1. Check that the router is plugged in and its lights are on.\n"
                    "  2. Unplug the router for 30 seconds, then plug it back in.\n"
                    "  3. Check your provider's outage map.")

    # RULE 8 (default): nothing matched -> admit it instead of guessing
    else:
        return ("I'm not sure I understand. Try words like 'slow', 'no internet', "
                "'keeps dropping', 'password', or 'router light'. Type 'help' for options.")


def main():
    """Conversation loop: read input, apply the rules, print the output."""
    print("=" * 60)
    print(" Wi-Fi & Internet Troubleshooting Assistant (rule-based)")
    print(" Describe your problem, or type 'quit' to exit.")
    print("=" * 60)

    while True:
        user_text = input("\nYou: ")
        words = normalize(user_text)

        # Empty input rule: ask again instead of running the rules on nothing
        if not words:
            print("Bot: Please type a short description of your problem.")
            continue

        # Exit rule: checked here because it ends the loop
        if has_any(words, EXIT_WORDS):
            print("Bot: Goodbye! I hope your connection is working.")
            break

        print("Bot:", diagnose(words))


if __name__ == "__main__":
    main()
