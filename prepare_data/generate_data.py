#!/usr/bin/env python3
# author: Rohith
# date: 5 May 2020

'''
This script reads the final_text(generated by combining train and text) and generates the following:
speaker_analysis.csv, text, wav.scp and utt2spk for both train and test.
'''

import codecs
import math, random
import csv
import os


def read_data(file):
    '''
    This method takes the final_text, returns text(list) and a reference_dictionary
    '''
    file = codecs.open(file, encoding='utf-8')
    text = file.readlines()
    text.sort()
    file.close()
    ref_dict = {}
    for line in text:
        temp = line.split(" ")
        if temp[0] not in ref_dict:
            ref_dict[temp[0]] = temp[1:]
    return text, ref_dict

def generate_speaker_distribution_and_details(text):
    '''
    This method takes the text(list) returned by read_data(file) method and returns the speaker_distribution dictionary
    '''
    global_dict= {}
    speaker_details = {}
    for t in text:
        temp = t.split(" ")[0]
        if len(temp) == 9:
            key = temp[0:-3]
        elif len(temp) == 21:
            key = temp.split(".")[0]
        if key not in global_dict:
            global_dict[key] = 1
            speaker_details[key] = [temp]
        else:
            global_dict[key] += 1
            speaker_details[key].append(temp)
    return global_dict, speaker_details



def write_spkdist2csv(dictionary):
    '''
    This method takes the global_dictionary returned by the generate_speaker_distribution(text) method and generates csv file
    '''
    file = open("speaker_analysis.csv", 'w', newline='')
    write = csv.writer(file)
    write.writerow(['speaker', 'count'])
    for k, v in dictionary.items():
        write.writerow([k, v])
    file.close()

def train_test_split(global_dict, speaker_details, ratio=0.3):
    '''
    This method takes the ration(test_dataset_ration), global_dict and speaker_details returned by generate_speaker_distribution_and_details(text) method
    '''
    train_details = []
    test_details = []
    for k, v in global_dict.items():
        spk = k
        if v > 10:
            te = math.floor(ratio * v)
            to_check = speaker_details[spk]
            test = random.sample(to_check, te)
            for l in test:
                to_check.remove(l)
            test_details.extend(test)
            train_details.extend(to_check)
        elif v <= 10:
            test_details.extend(speaker_details[spk])
    return train_details, test_details


def gen_text_wavscp(details,ref_dict, data="train"):
    '''
    This method takes train_details/test_details, ref_dict, train/test data and generates the text and wav.scp file
    '''
    if not os.path.isdir("./"+data):
        os.mkdir("./"+data)
    audio_path = "/home/nvv/kaldi/egs/telugu/s1/data/audios"
    file = codecs.open(data+"/text", "w+", encoding='utf-8')
    wav = open(data+"/wav.scp", "w+")
    details.sort()
    for element in details:
        file.write(element+" "+" ".join(ref_dict[element]))
        wav.write(element+" "+audio_path+"/"+element+".wav\n")
    file.close()
    wav.close()

def generate_utt2spk(details, data="train"):
    '''
    This method takes the train_details/test_details and the list of train/test utterances
    '''
    data = str(data)
    utt2spk = open(data+"/utt2spk", "w+")
    for utt in details:
        if len(utt) == 9:
            spk = utt[0:-3]
        elif len(utt) == 21:
            spk = utt.split(".")[0]
        utt2spk.write(utt+" "+spk+"\n")
    utt2spk.close()

if __name__ == '__main__':
    random.seed(42)
    print("reading final_text....")
    text, ref_dict = read_data('final_text')
    print("generated text and ref_dict.")
    global_dict, speaker_details = generate_speaker_distribution_and_details(text)
    print("generated global_dict and speaker_details")
    write_spkdist2csv(global_dict)
    print("written speaker-distribution details to the CSV file.")
    r = float(input("Enter the ratio for test (eg: 0.3 for 30% test): "))
    train_details, test_details = train_test_split(global_dict, speaker_details, ratio=r)
    print("generated train_details and the test_details")
    gen_text_wavscp(train_details,ref_dict, "train")
    print("generated text and wav.scp for train")
    gen_text_wavscp(train_details,ref_dict, "test")
    print("generated text and wav.scp for test")
    generate_utt2spk(train_details, "train")
    print("generated utt2spk for train")
    generate_utt2spk(test_details, "test")
    print("generated utt2spk for test")