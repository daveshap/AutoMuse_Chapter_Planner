import re
import os
import json
import openai
import tkinter as tk
from time import time, sleep
from tkinter import ttk, scrolledtext


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


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
            retry += 1
            if retry >= max_retry:
                print(f"Exiting due to an error in ChatGPT: {oops}")
                exit(1)
            print(f'Error communicating with OpenAI: {oops}. Retrying in {2 ** (retry - 1) * 5} seconds...')
            sleep(2 ** (retry - 1) * 5)


def send_message(*args):
    user_input = user_text.get()
    if not user_input.strip():
        return

    chat_text.config(state='normal')
    chat_text.insert(tk.END, f"USER: {user_input}\n")
    chat_text.see(tk.END)
    chat_text.config(state='disabled')

    user_text.set("")

    conversation.append({'role': 'user', 'content': user_input})
    filename = 'chat_%s_user.txt' % time()
    if not os.path.exists('chat_logs'):
        os.makedirs('chat_logs')
    save_file('chat_logs/%s' % filename, user_input)

    response = chatgpt_completion(conversation)
    conversation.append({'role': 'assistant', 'content': response})

    chat_text.config(state='normal')
    chat_text.insert(tk.END, f"MUSE: {response}\n")
    chat_text.see(tk.END)
    chat_text.config(state='disabled')

if __name__ == "__main__":
    openai.api_key = open_file('key_openai.txt')
    scratchpad = open_file('scratchpad.txt')
    system_message = open_file('system_chapter_helper.txt').replace('<<INPUT>>', scratchpad)
    conversation = list()
    conversation.append({'role': 'system', 'content': system_message})

    # Tkinter GUI
    root = tk.Tk()
    root.title("ChatGPT")

    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    chat_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=60, height=20)
    chat_text.grid(column=0, row=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
    chat_text.insert(tk.END, "Welcome to ChatGPT!\n\n")
    chat_text.config(state='disabled')

    user_text = tk.StringVar()
    user_entry = ttk.Entry(main_frame, width=50, textvariable=user_text)
    user_entry.grid(column=0, row=1, sticky=(tk.W, tk.E, tk.N, tk.S))

    send_button = ttk.Button(main_frame, text="Send", command=send_message)
    send_button.grid(column=1, row=1, sticky=(tk.W, tk.E, tk.N, tk.S))

    user_entry.focus()
    root.bind("<Return>", send_message)

    root.mainloop()
