from flask import Flask, render_template
import os
import dropbox

app = Flask(__name__)

access_token = os.environ['DROPBOX_ACCESS_TOKEN']
CLIENT = dropbox.client.DropboxClient(access_token)

def _download_pics(pics_to_download):
    for file_name in pics_to_download:
        f = CLIENT.get_file('/fuji-mix/'+file_name)
        out = open('static/images/'+file_name, 'wb')
        out.write(f.read())
        out.close()

def _remove_pics(pics_to_remove):
    for file_name in pics_to_remove:
        file_path = 'static/images/' + file_name
        os.remove(file_path)

def get_local_images():
    local_pics_path = 'static/images/'
    images = [local_pics_path+infile for infile in \
              os.listdir(local_pics_path) if not \
              infile.startswith('.')]
    return images

def sync_folders():
    dropbox_pic_folder = CLIENT.metadata('/fuji-mix')
    local_pics_path = 'static/images/'

    dropbox_pics = [pic['path'].strip('/fuji-mix/') \
                    for pic in dropbox_pic_folder['contents']]

    local_pics = [f for f in os.listdir(local_pics_path) \
                   if not f.startswith('.')] 

    if dropbox_pics is not local_pics:
        pics_to_download = list(set(dropbox_pics) - set(local_pics))
        pics_to_remove = list(set(local_pics) - set(dropbox_pics))

        if pics_to_download:
            _download_pics(pics_to_download)

        if pics_to_remove:
            _remove_pics(pics_to_remove)


@app.route("/")
def home():
    sync_folders()
    images = get_local_images()
    return render_template("/index.html", images=images)


if __name__ == "__main__":
    app.debug = False
    app.run(host='0.0.0.0')
