from jnius import autoclass
from kivy import Logger, platform
from datetime import datetime
import os
import traceback

from sharedstorage import SharedStorage

#from moviepy.editor import VideoFileClip

#
Environment = None

if platform == "android":
    from android import autoclass
    Environment = autoclass('android.os.Environment')

# =========================================================== #
#                   class Recorder                         #
# =========================================================== #

class Recorder():

# https://developer.android.com/reference/android/media/MediaRecorder.OutputFormat
# https://stackoverflow.com/questions/4886365/androidhow-to-get-media-recorder-output-in-mp3-format
# https://pypi.org/project/PythonVideoConverter/
# https://dev.to/dheerajprogrammer/mp4-to-mp3-converter-in-python-5eba

# This one looks the best....
# https://webcodespace.com/how-to-convert-mp4-to-mp3-using-python/

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
        self.BASE_FILENAME = ''
        self.EMAIL_USERNAME = ''
        self.EMAIL_PASSWORD = ''
        self.EMAIL_FROM = ''
        self.EMAIL_TO = ''
        self.SERVER_HOST = ''
        self.SERVER_PORT = 0
        
        self.configInit()
            
    # ----------------- configInit ------------------------ #        
    def configInit(self):
        
        from os.path import exists
        import shutil
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
                    
            if self.config['BaseFilename']: 
                self.BASE_FILENAME = str(self.config['BaseFilename'][0]).replace(' ','')
                print(f'self.BASE_FILENAME: {self.BASE_FILENAME}')
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
            
    def create_recorder(self):
        now = datetime.now()
        dt_string = now.strftime("%d%b%Y_%H%M%S")
#       self.mp4Fn = f'{self.BASE_FILENAME}_{dt_string}.mp4'
        self.mp3Fn = f'{self.BASE_FILENAME}_{dt_string}.mp3'

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
        self.create_recorder()
        self.recorder.start()
    
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

    # ----------------- get_mp3_path ------------------------ #
    def get_mp3_path(self):
#       path = "/storage/emulated/0/Movies/Mp3Recorder"
        path = "/storage/emulated/0/Music/Mp3Recorder"
        return path
    
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

