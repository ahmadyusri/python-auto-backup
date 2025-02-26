import os, sys, json, glob
from dotenv import load_dotenv
from google.oauth2 import service_account
import googleapiclient.discovery
from utils import exists_file, upload_file, delete_file

load_dotenv()

if len(sys.argv) < 2:
    exit("Please input path argument")
arg_path = sys.argv[1]

file_extension = '*'
if len(sys.argv) > 2:
    file_extension = sys.argv[2]

list_of_files = glob.glob(arg_path + "*." + file_extension)
if len(list_of_files) < 1:
    if file_extension == '*':
        exit('There are no file in backup dir')
    else:
        exit('There are no file in backup dir with extension "' + file_extension + '"')
latest_file = max(list_of_files, key=os.path.getctime)

head, tail = os.path.split(latest_file)

path = head + "/" + tail
filename = tail

GDRIVE_SHARE_EMAIL = os.getenv("GDRIVE_SHARE_EMAIL")
if GDRIVE_SHARE_EMAIL is None:
    exit("Please input GDRIVE_SHARE_EMAIL environment")
GDRIVE_AUTH = os.getenv("GDRIVE_AUTH")
if GDRIVE_AUTH is None:
    exit("Please input GDRIVE_AUTH environment")
GDRIVE_AUTH = r'{}'.format(GDRIVE_AUTH.encode("raw_unicode_escape")).replace("b'", "")[:-1]

service_account_info = json.loads(GDRIVE_AUTH)
SCOPES = ["https://www.googleapis.com/auth/drive"]

credentials = service_account.Credentials.from_service_account_info(
            service_account_info, 
            scopes=SCOPES
        )

drive = googleapiclient.discovery.build('drive', 'v3', credentials=credentials)

folder_name = "backup-files"
folder_ids = drive.files().list(q = "mimeType = 'application/vnd.google-apps.folder' and name = '"+ folder_name +"'", pageSize=1, fields="files(id)").execute()
folder_ids_result = folder_ids.get('files', [])
if len(folder_ids_result) == 0:
    exit("Cannot access folder: '" + folder_name + "' in google drive")

folder_id = folder_ids_result[0].get('id')

is_exists = exists_file(drive, folder_id, filename)
if is_exists == True:
    exit("File Backup: '" + filename + "' already exists in google drive")

upload_file(drive, folder_id, path, filename, {
    "type": "user",
    "role": "writer",
    "emailAddress": GDRIVE_SHARE_EMAIL,
})
delete_file(drive, folder_id, 3)
