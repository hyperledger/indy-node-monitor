import os
import fnmatch 
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def find_file(file_name):
    dir_path = os.path.dirname(os.path.realpath(__file__)) 
    for root, dirs, files in os.walk(dir_path): 
        for file in files:  
            if fnmatch.fnmatch(file, file_name): 
                return(root + '/' + str(file)) 

def gspread_authZ(gauth_json):
    # Google drive and Google sheets API setup
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    auth_file = find_file(gauth_json)
    if not auth_file:
        print("\033[1;31;40mUnable to find the Google API Credentials json file! Make sure the file is in the './conf' folder and name you specified is correct.")
        print("Json name entered: " + gauth_json + ".\033[m")
        exit()

    creds = ServiceAccountCredentials.from_json_keyfile_name(auth_file, scope) # Set credentials using json file
    authD_client = gspread.authorize(creds) # Authorize json file
    return(authD_client)

# Insert data in sheet
def gspread_append_sheet(authD_client, file_name, worksheet_name, row):
    try:
        sheet = authD_client.open(file_name).worksheet(worksheet_name) # Open sheet
        sheet.append_row(row, value_input_option='USER_ENTERED') # Append sheet
    except:
        print("\033[1;31;40mUnable to upload data to sheet! Please check file and worksheet name and try again.")
        print("File name entered: " + file_name + ". Worksheet name entered: " + worksheet_name + ".\033[m")
        exit()