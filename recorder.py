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

    from plyer.platforms.android import activity

    PythonActivity = autoclass('org.kivy.android.PythonActivity').mActivity
    ExternalStoragePath = PythonActivity.getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS).getPath()
    DownLoadsPath = PythonActivity.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS).getPath()
# ############################################################     
# https://stackoverflow.com/questions/42253775/how-i-can-use-startactivity-method-from-service-in-python-kivy-jnius
# https://stackoverflow.com/questions/62782648/android-11-scoped-storage-permissions
#    Intent = autoclass('android.content.Intent')
# ############################################################        
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
        self.MP3_FILENAME = ''
        self.EMAIL_USERNAME = ''
        self.EMAIL_PASSWORD = ''
        self.EMAIL_FROM = ''
        self.EMAIL_TO = ''
        self.SERVER_HOST = ''
        self.SERVER_PORT = 0
            
    # ----------------- configInit ------------------------ #        
    def configInit(self):
        
        from os.path import exists
        import shutil
        import traceback
#       from Mp3Recorder import LogMessage
        
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
                    
            if self.config['Mp3Filename']:
                self.MP3_FILENAME = str(self.config['Mp3Filename'][0]).replace(' ','')
                print(f'self.MP3_FILENAME: {self.MP3_FILENAME}')
            if self.config['Username']:
                self.EMAIL_USERNAME = str(self.config['Username'][0]).replace(' ','')
                print(f'self.EMAIL_USERNAME: {self.EMAIL_USERNAME}')
            if self.config['Password']:
                self.EMAIL_PASSWORD = str(self.config['Password'][0]).replace(' ','')
                print(f'self.EMAIL_PASSWORD: {self.EMAIL_PASSWORD}')
            if self.config['From']:
                self.EMAIL_FROM = str(self.config['From'][0]).replace(' ','')
                print(f'self.EMAIL_FROM: {self.EMAIL_FROM}')
            if self.config['To']:
                lst = self.config['To']
                self.EMAIL_TO = []
                for s in lst:
                    s2 = s.replace(' ','')
                    if len(s2) > 0:
                        self.EMAIL_TO.append(s2)
                print(f'self.EMAIL_TO: {self.EMAIL_TO}')
            if self.config['Host']:
                self.SERVER_HOST = str(self.config['Host'][0]).replace(' ','')
                print(f'self.SERVER_HOST: {self.SERVER_HOST}')
            if self.config['Port']:
                self.SERVER_PORT = int(str(self.config['Port'][0]).replace(' ',''))
                print(f'self.SERVER_PORT: {self.SERVER_PORT}')
               
#            LogMessage(f'Receiver: {self.EMAIL_TO}')
#            rcvr = self.config['Receiver'] 
#            LogMessage(f'self.config[Receiver]: {rcvr}') 
                
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
# ############################################################ 
# https://pypi.org/project/python-settings/
# rm: add 'python-settings' to buildozer requirements
#        from python_settings import settings 
#        from . import settings as my_local_settings
#        settings.configure(my_local_settings) # configure() receives a python module
#        assert settings.configured # now you are set
#        PythonActivity.startActivity(       
#            Intent.setAction(settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
#        )
# ############################################################        
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
        self.mp3Fn = f'{self.MP3_FILENAME}_{dt_string}.mp3'

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
        import traceback

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
        print(f'EMAIL_TO |{self.EMAIL_TO}|')
        
        server.login(self.EMAIL_USERNAME, self.EMAIL_PASSWORD)
        
        # setup payload
        msg = MIMEMultipart()
        msg['From'] = self.EMAIL_FROM
        msg['To'] = ",".join(self.EMAIL_TO)

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
        # Note max emails per day limit:
        # https://answers.microsoft.com/en-us/outlook_com/forum/all/smtpdataerror-554-520-on-my-outlook-account/c9cd69cc-4ad0-4c30-b96f-67fc533b0603
        
        try:
            server.sendmail(self.EMAIL_FROM, self.EMAIL_TO, msg.as_string())
            server.quit()        
        except Exception as error:
            err = traceback.format_exc()
            print(' ================================ sendmail traceback START ================================ ')
            print(err)
            print(' ================================ sendmail traceback END ================================ ')
            return f'[{basefn}] email error : {err}.'
        
        return f'[{basefn}] email complete.'
    
    # ======== email ========
    def email(self, filename):
        return self.send_email(filename)

    # ======================
    #       exit 
    # ======================
    def exit(self):
        quit()

