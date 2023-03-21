import os
import openai
import json
#import numpy as np
#from numpy.linalg import norm
import re
from time import time,sleep
#from uuid import uuid4
#import datetime


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


if __name__ == "__main__":
    openai.api_key = open_file('key_openai.txt')
    scratchpad = open_file('scratchpad.txt')
    system_message = open_file('system_chapter_helper.txt').replace('<<INPUT>>', scratchpad)
    conversation = list()
    conversation.append({'role': 'system', 'content': system_message})
    while True:
        # get user input and save it
        a = input('\n\nUSER: ')
        conversation.append({'role': 'user', 'content': a})
        filename = 'chat_%s_user.txt' % time()
        if not os.path.exists('chat_logs'):
            os.makedirs('chat_logs')
        save_file('chat_logs/%s' % filename, a)
        # generate a response
        response = chatgpt_completion(conversation)
        conversation.append({'role': 'assistant', 'content': response})
        print('\n\nMUSE: %s' % response)