import csv
import json
from transformers import BertTokenizer
from tqdm import tqdm
import random
import argparse



parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str)
parser.add_argument("--json_save", type=str)
parser.add_argument("--span_json_save", type=str)
parser.add_argument("--toxic_sample_num", type=str,default=9900)
parser.add_argument("--non_toxic_sample_num", type=str,default=1100)
args = parser.parse_args()

# Paths to the input CSV file and the output JSON file
input_csv_path = args.input
output_json_path = args.json_save
output_span_json_path = args.span_json_save


def convert_csv_to_json(csv_file_path, json_file_path):
    # Initialize a list to store the dictionaries
    json_data = []

    # Open the CSV file and read the contents
    with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Iterate over the CSV rows
        for row in reader:
            # Convert the 'toxic' field to an integer
            toxic_value = int(row["toxic"])
            
            # Append the dictionary with 'comment_text' and 'toxic' to the list
            json_data.append({"comment_text": row["comment_text"], "toxic": toxic_value})

    # Open the JSON file and write each dictionary to a new line
    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        for entry in json_data:
            # Dump the dictionary to a JSON formatted string and write to the file
            jsonfile.write(json.dumps(entry) + '\n')


# Call the function to perform the conversion
convert_csv_to_json(input_csv_path, output_json_path)


# Load the tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Function to process each comment
def process_comment(comment_data):
    # Tokenize the comment text
    tokenize_content = tokenizer.tokenize(comment_data['comment_text'])
    
    # Encode the comment text and generate spans for each 2-gram
    encoded = tokenizer.encode(comment_data['comment_text'], add_special_tokens=True)[1:-1]
    spans = [tokenizer.decode(encoded[i:i+2], skip_special_tokens=True) for i in range(len(encoded)-1)]
    
    return {
        'content': comment_data['comment_text'],
        'tokenize_content': tokenize_content,
        'span': spans,
        'toxic': int(comment_data['toxic'])  
    }

# Load the comments_toxicity.json
with open(output_json_path, 'r') as file:
    lst = file.readlines()
    toxic = []
    non_toxic = []
    for i in range(len(lst)):
        if lst[i]['toxic'] == '0':
            non_toxic.append(lst[i])
        elif lst[i]['toxic'] == '1':
            toxic.append(lst[i])
    comments_data = random.sample(toxic,args.toxic_sample_num) + random.sample(non_toxic,args.non_toxic_sample_num)
    

# Process each comment and store the results
train_span_data = [process_comment(comment) for comment in tqdm(comments_data,total=len(comments_data))]

# Save the processed data to train_span.json
with open(output_span_json_path, 'w') as outfile:
    for i in range(len(train_span_data)):
        outfile.write(json.dumps(train_span_data[i])+'\n')
