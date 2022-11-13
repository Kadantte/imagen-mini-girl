import os
import pickle
import time

import markovify
from concurrent.futures  import ProcessPoolExecutor
from tqdm import tqdm

from transformers import CLIPTokenizer

LIMIT_CLIP_TEXT_ENC=75

def generate_girl_prompt(model,tokenizer):
    prompt=model.make_sentence()

    if (prompt is None):
        return None

    tokens = tokenizer.tokenize(prompt)

    if (len(tokens) > LIMIT_CLIP_TEXT_ENC):
        return None

    if ("girl" in prompt):
        if (all([not x in prompt for x in ("boy", "man", "male")])):
            return prompt

    return None

def compile(model_json):
    model = markovify.Text.from_json(model_json)
    model = model.compile()
    return model

if __name__ == "__main__":
    NUM_PROMPTS=2**10
    prompts=[]

    tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")

    with open("models/prompt_gen.json", "r") as f:
        model_json = f.read()

    model=compile(model_json)

    with tqdm(total=NUM_PROMPTS) as pbar:
        with ProcessPoolExecutor(max_workers=os.cpu_count()*3) as executor:
            futures = []
            for i in range(os.cpu_count()*3):
                futures.append(executor.submit(generate_girl_prompt, model, tokenizer))

            while(True):
                for i in range(os.cpu_count()*3):
                    if(futures[i].done()):
                        prompt=futures[i].result()
                        if(prompt is not None):
                            print(prompt)
                            prompts.append(prompt)
                            pbar.update(1)
                        futures[i]=executor.submit(generate_girl_prompt, model, tokenizer)
                if (len(prompts) > NUM_PROMPTS):
                    break

    prompts=prompts[:NUM_PROMPTS]
    with open("prompts.pickle","wb") as f:
        pickle.dump(prompts,f,pickle.HIGHEST_PROTOCOL)
