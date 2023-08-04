from jnius import autoclass
from kivy import Logger, platform
from datetime import datetime
import os

# https://github.com/kivy/python-for-android/pull/2725
# https://stackoverflow.com/questions/73909410/manage-external-storage-vs-write-external-storage
# https://github.com/kivy/buildozer/issues/1004
# https://developer.android.com/reference/android/os/Environment

Environment = autoclass('android.os.Environment')

from sharedstorage import SharedStorage
#
PythonActivity = None
if platform == "android":
    from android import mActivity, autoclass, api_version
    from android.permissions import request_permissions, Permission

    from android.storage import app_storage_path
    from android.storage import primary_external_storage_path
    from android.storage import secondary_external_storage_path

    PythonActivity = autoclass("org.kivy.android.PythonActivity").mActivity
    ExternalStoragePath = PythonActivity.getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS).getPath()
    DownLoadsPath = PythonActivity.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS).getPath()
    Context = autoclass('android.content.Context')

# =========================================================== #
#                   class Recorder                         #
# =========================================================== #

class Recorder():

    required_permissions = [
            Permission.RECORD_AUDIO,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE,
# Wifi test:            
            Permission.ACCESS_WIFI_STATE, 
            Permission.INTERNET, 
    ]

    def __init__(self, **kwargs):
        super(Recorder, self).__init__(**kwargs)

        if not platform == "android":
            return
        
        self.MediaRecorder = autoclass('android.media.MediaRecorder')
        self.AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
        self.OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
        self.AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
        #
        self.mp3_filename = ''
        self.mp3Fn = ''
        self.config = dict()
        self.MP3_FILEROOT = ''
        self.EMAIL_USERNAME = ''
        self.EMAIL_PASSWORD = ''
        self.EMAIL_SENDER = ''
        self.EMAIL_RECEIVER = ''
        self.SERVER_HOST = ''
        self.SERVER_PORT = 0
            
    # ----------------- configInit ------------------------ #        
    def configInit(self):
        
        from os.path import exists
        import shutil
        import traceback

        self.config.clear()
            
        print('START # ----------------- configInit ------------------------ #')
        # ==============================================================================================
        # Note for local editing Mp3Recorder.cvs file [problems due to file extension and write restrictions in 'Documents']:
        # Name the new local edited file 'Mp3Recorder.apk' [or '.txt', not '.csv']
        # Copy via explorer 'Mp3Recorder.apk' to the Documents folder
        # Delete the old 'Mp3Recorder.csv' [or rename to something with a '.csv' ext, ie 'Mp3RecorerOld.csv']
        # Rename the new 'Mp3Recorder.apk' file to 'Mp3Recorder.csv', now you're done.
        # ==============================================================================================
        SharePath = './Mp3Recorder.csv'
        ConfigPath = '/storage/emulated/0/Documents/Mp3Recorder/Mp3Recorder.csv' 
        path = ''  
        content_list = []    
        try:
            
            # Move a local copy and read config from here, may be locally modified.
            # https://www.tutorialspoint.com/How-to-copy-files-from-one-folder-to-another-using-Python
            documents_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS).getPath()
            ConfigPath = f'{documents_dir}/Mp3Recorder/Mp3Recorder.csv'
            if exists(ConfigPath) == False:
                ss = SharedStorage()
                share = ss.copy_to_shared(SharePath)
                path = ss.copy_from_shared(share)
                
            with open(ConfigPath) as f:
                content_list = f.readlines()
            f.close()

            for item in content_list:
                i = item.replace('\n','')
                print(f'[{i}]')
                itemList = []
                try:
                    itemList = item.replace(' ','').split(',')
                except ValueError:
                    continue
                if len(itemList) > 1 and itemList[0][0] != '#':
                    # cleanup NL etc
                    for i,s in enumerate(itemList):
                        itemList[i] = s.strip()
                    k = itemList[0].strip()
                    v = itemList[1:]
                    self.config[k] = v
                    print(f'[ {k}:{v} ]')
                    
            if self.config['Mp3FileRoot']:
                self.MP3_FILEROOT = str(self.config['Mp3FileRoot'][0])
                print(f'self.MP3_FILEROOT: {self.MP3_FILEROOT}')
            if self.config['Username']:
                self.EMAIL_USERNAME = str(self.config['Username'][0])
                print(f'self.EMAIL_USERNAME: {self.EMAIL_USERNAME}')
            if self.config['Password']:
                self.EMAIL_PASSWORD = str(self.config['Password'][0])
                print(f'self.EMAIL_PASSWORD: {self.EMAIL_PASSWORD}')
            if self.config['Sender']:
                self.EMAIL_SENDER = str(self.config['Sender'][0])
                print(f'self.EMAIL_SENDER: {self.EMAIL_SENDER}')
            if self.config['Receiver']:
                self.EMAIL_RECEIVER = (','.join(self.config['Receiver']))
                print(f'self.EMAIL_RECEIVER: {self.EMAIL_RECEIVER}')
            if self.config['Host']:
                self.SERVER_HOST = str(self.config['Host'][0])
                print(f'self.SERVER_HOST: {self.SERVER_HOST}')
            if self.config['Port']:
                self.SERVER_PORT = int(self.config['Port'][0])
                print(f'self.SERVER_PORT: {self.SERVER_PORT}')
                
        except Exception as error:
            self.config.clear()
            err = traceback.format_exc()
            print(' ================================ configInit traceback START ================================ ')
            print(err)
            print(' ================================ configInit traceback END ================================ ')
   
    # ----------------- permissions ------------------------ #        
    def check_permission(permission, activity=None):
        if platform == "android":
            activity = PythonActivity
        if not activity:
            return False

        permission_status = 0
        permission_granted = 0 == permission_status
        return permission_granted

    def ask_permission(self,permission):
        PythonActivity.requestPermissions([permission])
        if len(self.config) == 0:
            self.configInit()

    def ask_permissions(self):
        request_permissions(self.required_permissions)
        if len(self.config) == 0:
            self.configInit()

    def check_required_permission(self):
        permissions = self.required_permissions
        #
        has_permissions = True
        for permission in permissions:
            if not self.check_permission(permission):
                has_permissions = False
        return has_permissions
            
    def create_recorder(self):
        now = datetime.now()
        dt_string = now.strftime("%d%b%Y_%H%M%S")
        self.mp3Fn = f'{self.MP3_FILEROOT}_{dt_string}.mp3'

        self.recorder = self.MediaRecorder()
        self.recorder.setAudioSource(self.AudioSource.MIC)
        self.recorder.setOutputFormat(self.OutputFormat.MPEG_4)
        self.recorder.setOutputFile(self.mp3Fn)
        self.recorder.setAudioEncoder(self.AudioEncoder.AAC)
        self.recorder.prepare()

    def get_recorder(self):
        if not hasattr(self, "recorder"):
            self.create_recorder()
        return self.recorder

    def remove_recorder(self):
        delattr(self, "recorder")
   
    # ----------------- record_start ------------------------ #
    def record_start(self):
        self.get_recorder()
        
        self.mp3_filename = ''
        
        if self.check_required_permission():
            # - new
            self.create_recorder()
            # - 
            self.recorder.start()
        else:
            self.ask_permissions()
    
    # ----------------- record_stop ------------------------ #
    def record_stop(self):
        self.get_recorder()
        self.recorder.stop() 
      
        # Copy the mp3 to Main Storage:
        ss = SharedStorage()
        share = ss.copy_to_shared(self.mp3Fn)
        path = ss.copy_from_shared(share)
        self.mp3_filename = path

        self.recorder.reset()
        self.recorder.release()
        # we need to do this in order to make the object reusable
        self.remove_recorder()
          
    # ----------------- get_mp3_filename ------------------------ #
    def get_mp3_filename(self):
        return self.mp3_filename
    
    # ======================
    #       record 
    # ======================
    def record(self,state):
        if state == 'ready':
            state = 'recording'
            if len(self.config) == 0:
                self.configInit()
            self.record_start()
        elif state == 'recording':
            state = 'ready'
            self.record_stop()
        return state

    # ======================
    #       email 
    # ======================

    def send_email(self, filename):
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders
        from os.path import exists

        if filename == None or not exists(filename):
            return f' Error: [{filename}] does not exist.'
        
        basefn = os.path.basename(filename)
        
        # set up the SMTP server
        server = smtplib.SMTP(self.SERVER_HOST, self.SERVER_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        
        print(f'SERVER_HOST |{self.SERVER_HOST}|')
        print(f'SERVER_PORT |{self.SERVER_PORT}|')
        print(f'EMAIL_USERNAME |{self.EMAIL_USERNAME}|')
        print(f'EMAIL_PASSWORD |{self.EMAIL_PASSWORD}|')
        print(f'EMAIL_RECEIVER |{self.EMAIL_RECEIVER}|')
        
        server.login(self.EMAIL_USERNAME, self.EMAIL_PASSWORD)
        
        # setup payload
        msg = MIMEMultipart()
        msg['From'] = self.EMAIL_SENDER
        msg['To'] = self.EMAIL_RECEIVER

        # Subject
        msg['Subject'] = f'[{basefn}] From Mp3Recorder'

        # Body
        body = f'[{basefn}] From Mp3Recorder'
        msg.attach(MIMEText(body, 'plain'))

        # file attachment
        attachment = open(filename, "rb")
        p = MIMEBase('application', 'octet-stream')
        p.set_payload((attachment).read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % basefn)
        msg.attach(p)
        
        #Send the mail
        text = msg.as_string()
        server.sendmail(self.EMAIL_SENDER, self.EMAIL_RECEIVER, text)
        server.quit()        
        
        return f'[{basefn}] email complete.'
    
    # ======== email ========
    def email(self, filename):
        return self.send_email(filename)

    # ======================
    #       exit 
    # ======================
    def exit(self):
        quit()

