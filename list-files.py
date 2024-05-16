import os
from dotenv import load_dotenv
import json
from google.oauth2 import service_account
import googleapiclient.discovery

load_dotenv()  

GDRIVE_AUTH = os.getenv("GDRIVE_AUTH")
if GDRIVE_AUTH is None:
    exit("Please input GDRIVE_AUTH environment")

service_account_info = json.loads(GDRIVE_AUTH)
SCOPES = ["https://www.googleapis.com/auth/drive"]


credentials = service_account.Credentials.from_service_account_info(
            service_account_info, 
            scopes=SCOPES
        )

drive = googleapiclient.discovery.build('drive', 'v3', credentials=credentials)

folder_ids = drive.files().list(pageSize=10, fields="nextPageToken, files(id, name, mimeType, parents)").execute()
folder_ids_result = folder_ids.get('files', [])

for file in folder_ids_result:
    parent_names = []
    parent_ids = None
    try:
        parent_ids = file['parents']
        for parent_id in parent_ids:
            parent_folder_ids = drive.files().get(fileId=parent_id, fields="id, name, mimeType").execute()
            parent_names.append(parent_folder_ids['name'])
    except:
        pass

    if file['mimeType'] == 'application/vnd.google-apps.folder':
        print('Folder', 'name: {}, id: {}, parents: {}'.format(file['name'], file['id'], parent_names))
    else:
        print('File', 'name: {}, id: {}, parents: {}'.format(file['name'], file['id'], parent_names))
