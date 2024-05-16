from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

def upload_file(drive, folder_id, path, filename, permission = None):
    upload_file_id = None
    print("Start upload_file", path)
    try:
        file_metadata = {"name": filename, "parents": [folder_id]}
        media = MediaFileUpload(path, chunksize=1024*1024, resumable = True)
        request = drive.files().create(body=file_metadata, media_body=media, fields="id")

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status is not None:
                print('Uploading ' + str(int(status.progress() * 100)) +'% "'+ filename +'"')

        upload_file_id = request.execute()['id']

        print("Upload Complete! ID: ", upload_file_id)

        if permission is not None:
            drive.permissions().create(
                fileId=upload_file_id,
                body=permission,
                fields="id",
            ).execute()
    except HttpError as error:
        print(f"An error occurred: {error}")

    return upload_file_id

def delete_file(drive, folder_id, max_files = None):
    if max_files is None:
        max_files = 3

    # Get all the files from folder
    results = drive.files().list(
            q="mimeType != 'application/vnd.google-apps.folder' and '" + folder_id + "' in parents",
            pageSize=10,
            fields="nextPageToken, files(id, name, createdTime)",
            orderBy="folder,createdTime asc"
        ).execute()
    files = results.get('files', [])

    if len(files) > max_files:
        deleted_files = files[0:(len(files) - max_files)]

        # Delete oldest files
        for file in deleted_files:
            drive.files().delete(
                fileId=file['id']
            ).execute()
            print('Deleted File', 'name: {}, id: {}'.format(file['name'], file['id']))

def exists_file(drive, folder_id, filename):
    # Get file from folder
    results = drive.files().list(
            q="name = '" + filename + "' and mimeType != 'application/vnd.google-apps.folder' and '" + folder_id + "' in parents",
            pageSize=1,
            fields="nextPageToken, files(id, name, createdTime)",
        ).execute()
    files = results.get('files', [])

    return len(files) > 0
