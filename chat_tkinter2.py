import re
import os
import json
import openai
import tkinter as tk
from time import time, sleep
from threading import Thread
from tkinter import ttk, scrolledtext


##### simple helper functions


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return json.load(infile)


def save_json(filepath, payload):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        json.dump(payload, outfile, ensure_ascii=False, sort_keys=True, indent=2)


##### OpenAI functions


def chatgpt_completion(messages, model="gpt-4"):
    max_retry = 7
    retry = 0
    while True:
        try:
            response = openai.ChatCompletion.create(model=model, messages=messages)
            text = response['choices'][0]['message']['content']
            filename = 'chat_%s_muse.txt' % time()
            if not os.path.exists('chat_logs'):
                os.makedirs('chat_logs')
            save_file('chat_logs/%s' % filename, text)
            return text
        except Exception as oops:
            print('\n\n\n OPENAI ERROR:', str(oops), '\n\n\n')
            if 'maximum context length' in str(oops):
                a = messages.pop(1)
                continue
            retry += 1
            if retry >= max_retry:
                print(f"Exiting due to an error in ChatGPT: {oops}")
                exit(1)
            print(f'Error communicating with OpenAI: "{oops}" - Retrying in {2 ** (retry - 1) * 5} seconds...')
            sleep(2 ** (retry - 1) * 5)


####### TKINTER functions 


def send_message(event=None):
    user_input = user_entry.get("1.0", tk.END).strip()
    if not user_input.strip():
        return

    chat_text.config(state='normal')
    chat_text.insert(tk.END, f"\n\nUSER:\n{user_input}\n\n", 'user')
    chat_text.see(tk.END)
    chat_text.config(state='disabled')

    user_entry.delete("1.0", tk.END)  # Clear user_entry content

    # Disable input and button while MUSE is thinking
    user_entry.config(state='disabled')
    send_button.config(state='disabled')


    conversation.append({'role': 'user', 'content': user_input})
    filename = 'chat_%s_user.txt' % time()
    if not os.path.exists('chat_logs'):
        os.makedirs('chat_logs')
    save_file('chat_logs/%s' % filename, user_input)

    ai_status.set("MUSE is thinking...")
    Thread(target=get_ai_response).start()
    # Re-enable input and button after response
    user_entry.config(state='normal')
    send_button.config(state='normal')


def get_ai_response():
    response = chatgpt_completion(conversation)
    conversation.append({'role': 'assistant', 'content': response})
    # save debug
    filename = 'debug/log_%s_main.json' % time()
    save_json(filename, conversation)

    def update_chat_text():
        chat_text.config(state='normal')
        chat_text.insert(tk.END, f"\n\nMUSE:\n{response}\n\n", 'muse')
        chat_text.see(tk.END)
        chat_text.config(state='disabled')
        ai_status.set("")

    # Update the chat_text in the main thread
    root.after(0, update_chat_text)



def on_return_key(event):
    if event.state & 0x1:  # Shift key is pressed
        user_entry.insert(tk.END, '\n')
    else:
        send_message()


if __name__ == "__main__":
    openai.api_key = open_file('key_openai.txt')
    scratchpad = open_file('scratchpad.txt')
    system_message = open_file('default_system.txt').replace('<<INPUT>>', scratchpad)
    conversation = list()
    conversation.append({'role': 'system', 'content': system_message})

    # Tkinter GUI
    root = tk.Tk()
    root.title("AutoMuse")

    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(0, weight=1)

    chat_text = tk.Text(main_frame, wrap=tk.WORD, width=60, height=20)
    chat_text.grid(column=0, row=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
    chat_text.tag_configure('user', background='#D0F0C0', wrap='word')
    chat_text.tag_configure('muse', background='#AED6F1', wrap='word')
    chat_text.insert(tk.END, "Welcome to AutoMuse!\n\n")
    chat_text.config(state='disabled')

    user_text = tk.StringVar()
    # Replace the Entry widget with a Text widget
    user_entry = tk.Text(main_frame, wrap=tk.WORD, width=50, height=3)
    user_entry.grid(column=0, row=1, sticky=(tk.W, tk.E, tk.N, tk.S))

    send_button = ttk.Button(main_frame, text="Send", command=send_message)
    send_button.grid(column=1, row=1, sticky=(tk.W, tk.E, tk.N, tk.S))

    ai_status = tk.StringVar()
    ai_status_label = ttk.Label(main_frame, textvariable=ai_status)
    ai_status_label.grid(column=2, row=1, sticky=(tk.W, tk.E, tk.N, tk.S))

    user_entry.focus()
    # Update the event binding to use the new Text widget
    root.bind("<Return>", on_return_key)
    # Update the event binding for the user_entry Text widget
    #user_entry.bind("<Return>", on_return_key)

    root.mainloop()