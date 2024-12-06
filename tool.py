import anthropic
import os

if "ANTHROPIC_API_KEY" not in os.environ:
    print('Please run \033[92mexport ANTHROPIC_API_KEY="sk-ant-api03-<foo>"\033[0m')
    exit(1)


def reset():
    global SYSTEM_PROMPT
    SYSTEM_PROMPT = "The following is a user request, explaining what they would like to do. You should output a suggested bash command and no other text, unless they are vague and you would like to request additional clarification in which case return a question, ending with a question mark, or you would like to run a command to gain more information, in which case return the exact command followed by an exclamation mark. For example, if the user wants to ping a server, you should ask which one, or if they are attempting to make a commit, you should ask what message they want. Remember to be careful around generating bash one-liners and use the correct syntax to get it right first time. If you want to write a python or bash script you can cat it to a file and then run it, as long as you delete it after."


def add_to_prompt(text):
    global SYSTEM_PROMPT
    SYSTEM_PROMPT += "\n"
    SYSTEM_PROMPT += text


def process_command(client, command):
    global SYSTEM_PROMPT
    response = get_LLM_response(client, command)
    if response[-1] in ("?", "!"):
        # Request for further information
        if response[-1] == ("?"):
            cprint(response, "\033[92m")
            context = input()
            add_to_prompt(
                "The user previously said they wanted to {}, you asked {} and got {} in response.".format(
                    command, response, context
                )
            )
            response = get_LLM_response(
                client,
                "Please now respond exactly with the bash command they should run. Do not ask for further information.",
            )
        elif response[-1] == "!":
            while response[-1] == "!":
                # Loop to gather more information
                auto = True
                auto = False  # If you want to destroy your computer, comment this line out
                decision = "y"
                if not auto:
                    cprint(
                        "I want to run this for further information. Can I run it? (y/n)",
                        "\033[95m",
                    )
                cprint(response[:-1], "\033[96m")
                if not auto:
                    decision = input()
                if decision.lower() != "y":
                    break
                else:
                    proposed = get_LLM_response(client, response[:-1])
                    output = run_command(proposed)
                    print(proposed)
                    print(output)

                    add_to_prompt(
                        "The user previously said they wanted to {}, you ran {} and got {} in response.".format(
                            command, proposed, output
                        )
                    )
                response = get_LLM_response(
                    client,
                    "Please now respond exactly with the bash command they should run, or ask for more information by giving a command and appending ! to the end",
                )
                # print(response)

    if response[-1] in ("?", "!"):
        # We declined a request for more info
        response = response[:-1]
    cprint(
        "I suggest this command. Would you like me to run it? (y/n/explain)", "\033[95m"
    )
    cprint(response, "\033[96m")
    decision = input()

    if decision.lower() == "explain":
        explain(response)

    if decision.lower() in {"y", "yes", "ok"}:
        print(run_command(response))
    elif decision.lower() == "explain":
        reset()
    else:
        # Else just ask again
        pass


def explain(command):
    global SYSTEM_PROMPT
    CACHE = SYSTEM_PROMPT
    SYSTEM_PROMPT = "Please explain this command clearly and concisely."
    explanation = get_LLM_response(client, command)
    SYSTEM_PROMPT = CACHE  # Reset
    cprint(explanation, "\033[95m")
    cprint("Would you like me to run it? (y/n)", "\033[95m")
    decision = input()  # Then get the original go/no-go

    return decision


def get_LLM_response(client, text):
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [{"type": "text", "text": text}],
            }
        ],
    )
    return message.content[0].text


def run_command(command):
    result = os.popen(command).read()
    return result


def cprint(text, colour):
    # Pretty print
    print(colour + text + "\033[0m" + " ")


if __name__ == "__main__":
    client = anthropic.Anthropic()
    while True:
        reset()
        cprint("What do you want to do?", "\033[92m")
        next_command = input()
        if next_command == "exit":
            break
        process_command(client, next_command)
        print("\n")
