import os
import csv
import uuid
import argparse
import subprocess
import json
import time
import pickle
from datetime import date
import hashlib 
### FUNCTIONS ###

### DISPLAY TITLE OF APPLICATION ###


def display_title_bar():

    os.system('cls')
    print("\t*********************************************")
    print("\t***            Welcome to IMUI            ***")
    print("\t*********************************************")

### VERIFY USERS INPUT ###


def verify_input(args):
    global image_dir_path
    global csv_out_file_path
    global GUID_TYPE
    global GUID_prefix
    global Input_csv_filepath

    if not os.path.isdir(args.directory[0]):
        print("Please enter the correct directory path")
        exit(0)
    else:
        image_dir_path = args.directory[0]

    csv_dir = os.path.dirname(os.path.abspath(args.output_csv[0]))
    if os.path.isdir(csv_dir) and not os.path.exists(args.output_csv[0]):
        csv_out_file_path = args.output_csv[0]
    else:
        print("Please enter corect output CSV File Path")
        exit(0)

    GUID_TYPE = args.guid_type[0]
    if args.guid_prefix != None:
        GUID_prefix = args.guid_prefix[0]
    if args.input_csv != None:
        if os.path.exists(args.input_csv[0]):
           verify_input_csv(args)
           Input_csv_filepath = args.input_csv[0]
        else:
            print("please enter valid input csv file")
            exit(0)   

   ### VERIFY THE USERS CSV FIELDS ###


def verify_input_csv(args):
    input_csv_temp = args.input_csv[0]
    global input_csv_data
    fields = {'identifier', 'file', 'mediatype', 'title', 'description', 'creator', 'date',
              'collection', 'recordID', 'accessURI', 'subject[0]', 'subject[1]', 'subject[2]'}
    excludedfields = {'identifier', 'file'}
    with open(input_csv_temp, 'r') as readFile:
        reader = csv.reader(readFile)
        lines = list(reader)
        i = 0
        for field in lines[0]:
            if field not in fields:
                print("Enter valid input csv")
                exit(0)
            else:
                if field not in excludedfields:
                    input_csv_data[field] = lines[1][i]
                i += 1
   ### SCAN DIRECTORY RECURSIVELY AND FIND ALL IMAGE FILES ###


def scan_dir(image_files):
    if os.path.isdir(image_dir_path):
        extensions = ['.gif', '.jpg', '.bmp','.jpeg','.tif','.tiff']
        for root, dirs, files in os.walk(image_dir_path):
            for f in files:
                fullpath = os.path.join(root, f)
                base, ext = os.path.splitext(fullpath)
                if ext.lower() in extensions:
                    image_files.append(fullpath)
    ### LOAD PERSISTENT DATA ###


def loadData():
    global persistent_data
    if os.path.exists('persistentdata'):
        dbfile = open('persistentdata', 'rb')
        persistent_data = pickle.load(dbfile)
        dbfile.close()
   ### CREATE CSV FILE CONTAINING LIST OF ALL IMAGE FILE IN IA FORMAT ###


def create_ia_csv(image_files):
    global GUID_prefix
    global input_csv_data
    global persistent_data
    with open('ia_upload_temp.csv', 'w') as csvfile:
        data = []
        temp = ['identifier', 'file']
        if not input_csv_data:
            data.append(temp)
        else:
            col = list(input_csv_data.keys())
            temp = temp+col
            data.append(temp)
        for image_file in image_files:
            id = None
            if image_file in list(persistent_data.keys()):
                id = persistent_data[image_file]
            else:
                id = uuid.uuid1().hex
                if GUID_TYPE == "prefixname" or GUID_TYPE == "prefixuuid" or GUID_TYPE == "prefixpath":
                   if GUID_prefix != None:
                      if GUID_TYPE == "prefixuuid":
                           id = GUID_prefix+"_"+id
                      elif GUID_TYPE == "prefixname":
                           id = GUID_prefix+"_" + \
                           os.path.basename(os.path.abspath(image_file))
                      elif GUID_TYPE == "prefixpath":
                           image_temp=image_file.replace(':','')
                           id = GUID_prefix+"_" + image_temp.replace('\\','-')
            temp_entry = []
            temp_entry.append(id)
            temp_entry.append(image_file)
            if image_file not in list(persistent_data.keys()):
                persistent_data[image_file] = id
            for c in temp:
                if c in list(input_csv_data.keys()):
                    temp_entry.append(input_csv_data[c])
            data.append(temp_entry)
        filewriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
        filewriter.writerows(data)
    csvfile.close()
    Pfile = open('persistentdata', 'wb')
    pickle.dump(persistent_data, Pfile)
    Pfile.close()

    ### UPLOAD FILES TO INTERNET ARCHIVE ###


def upload_IA():
    cmd = "ia upload --spreadsheet=ia_upload_temp.csv --retries 10"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    print("Upload Completed")

    ### CREATE OUTPUT CSV CONTAINING URI ###


def create_output_csv():
    data = [['idigbio:recordID', 'ac:accessURI','dc:type','dc:format','dc:rights','idigbio:OriginalFileName','ac:hashFunction',
             'ac:hashValue','idigbio:jsonProperties','idigbio:mediaStatus','idigbio:mediaStatusDate','idigbio:mediaStatusDetail']]
    global csv_out_file_path
    with open('ia_upload_temp.csv', 'r') as readFile:
        reader = csv.reader(readFile)
        lines = list(reader)
        for line in lines:
            if line[0] != "identifier":
                uri = "https://"
                cmd = "ia metadata "+line[0]
                output = subprocess.check_output(cmd)
                metadata_list = json.loads(output)
                count = 0
                sleep_time = 0
                while 'workable_servers' not in metadata_list and count < 5:
                    count += 1
                    sleep_time += 2
                    time.sleep(sleep_time)
                    output = subprocess.check_output(cmd)
                    metadata_list = json.loads(output)
                if "workable_servers" in metadata_list and "dir" in metadata_list and "files" in metadata_list:
                   uri = uri+metadata_list["workable_servers"][0]
                   uri = uri+metadata_list["dir"]+"/"
                   fm="image/"
                   for l in metadata_list["files"]:
                       base = os.path.basename(line[1])
                       if l["name"] == base:
                          name, ext = os.path.splitext(base)
                          fm=fm+ext.replace(".","")
                          uri = uri+base
                   hasher = hashlib.md5()
                   with open(line[1], 'rb') as afile:
                        buf = afile.read()
                        hasher.update(buf)       
                   temp_entry = [line[0], uri,'StillImage',fm,'CC BY',line[1],'md5',hasher.hexdigest(),"{}",'uploaded',date.today()]
                   data.append(temp_entry)
                   afile.close()
                else:
                    print("metadata not found for image:-",line[0])
    readFile.close()
    with open(csv_out_file_path, 'w') as outputfile:
        filewriter = csv.writer(outputfile, delimiter=',', lineterminator='\n')
        filewriter.writerows(data)
    outputfile.close()

### MAIN PROGRAM ###


image_dir_path = None
csv_out_file_path = None
GUID_prefix = None
GUID_TYPE = None
input_csv_data = {}
persistent_data = {}
Input_csv_filepath = None
image_files = []

parser = argparse.ArgumentParser(description="IMUI")
parser.add_argument("-dir", "--directory", type=str, nargs=1,
                    default=None, required=True, metavar="Directory_Path",
                    help="Give the Directory path containing all the image files to upload ")
parser.add_argument("-ocsv", "--output_csv", type=str, nargs=1,
                    default=None, required=True, metavar="Output_csv_filepath",
                    help="Give the output csv file name with complete path(file should not exist)")
parser.add_argument("-gt", "--guid_type", type=str, nargs=1, metavar="ID_Type",
                    choices=['random', 'prefixname', 'prefixuuid', 'prefixpath'], required=True,
                    help="Select one of the following unique ID type random, prefixname, prefixuuid, prefixpath")
parser.add_argument("-gp", "--guid_prefix", type=str, nargs=1, default=None, metavar="Prefix_String",
                    help="Please enter the string you want to use as prefix")
parser.add_argument("-icsv", "--input_csv", type=str, nargs=1, metavar="Input_csv_filepath", default=None,
                    help="Please enter the string you want to use as prefix")

args = parser.parse_args()
display_title_bar()
verify_input(args)
loadData()
scan_dir(image_files)
create_ia_csv(image_files)
upload_IA()
create_output_csv()
print("\nThanks for using IMUI. Bye.")
