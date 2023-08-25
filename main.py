from kivymd.app import MDApp
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.uix.scrollview import ScrollView
from kivymd.uix.list import MDList, OneLineListItem

from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.utils import platform

import time
from os.path import basename,exists

from recorder import Recorder

if platform == "android":
    from android.permissions import request_permissions, Permission

mp3Recorder = Recorder()

loadFilename = ''
emailFileMsg = ''
      
# ============================================
#               Mp3Recorder
# ============================================
class Mp3Recorder(MDBoxLayout):
    
    def __init__(self, **kwargs):
        
        global mp3Recorder
        
        super(Mp3Recorder, self).__init__(**kwargs)
        #
        if not platform == "android":
            return

        required_permissions = [
                    Permission.RECORD_AUDIO,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE,
                    # AttributeError: type object 'Permission' has no attribute 'MANAGE_EXTERNAL_STORAGE'                    
#                   Permission.MANAGE_EXTERNAL_STORAGE,
                    # AttributeError: type object 'Permission' has no attribute 'ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION'                    
#                   Permission.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION,
        # Wifi test:            
                    Permission.ACCESS_WIFI_STATE, 
                    Permission.INTERNET, 
            ]
        
        print('========== BEFORE init request_permissions ==============')
        request_permissions(required_permissions)
        print('========== AFTER  init request_permissions ==============')
        
#        from recorder import Recorder
#        mp3Recorder = Recorder()

        self.state = 'ready'
        self.time_started = False
        
        # ------------ ScrollView stuff. ie 'Info' -----------------
        self.sv = ScrollView()
        self.ml = MDList()
        self.sv.add_widget(self.ml)
        self.contacts = []
                     
        self.file_choose_root = Root()
        
        rsp = self.wifiCheck()
        print(f'after self.wifiCheck(), [{rsp}]')
        
        self.start_time()

    #
    # -------- timer -------
    #
    def timer(self, *args):
        global loadFilename
        global emailFileMsg

        time_str = f'Mp3Recorder [{time.asctime()}]'
        chk = ''
        # -------- TODO - log transition ----------- 
        if self.wifiCheck():
            chk = '* UP *'
            self.ids.time_label.color = "orange"
        else:
            chk = '- DN -'
            self.ids.time_label.color = "yellow"

        wifi_str = f'Wifi {chk}'
        self.ids.time_label.text = f'{time_str} - [{wifi_str}]'
        
        if exists(loadFilename):
            self.update_labels()
    #
    # -------- start_time -------
    #
    def start_time(self):
        Clock.schedule_interval(self.timer, 1)

    #
    # -------- wifiCheck -------
    #
    def wifiCheck(self):
        from ping3 import ping, verbose_ping
        # https://github.com/kyan001/ping3
        # UP rsp : 0.016164541244506836
        # DN rsp : None
        rsp = ping('google.com')
        return isinstance(rsp, float)
    #
    # -------- LogMessage ------- WIP -----
    #
#    @staticmethod
    def LogMessage(self, msg):
        from datetime import datetime
        
        now = datetime.now()
        dt_string = now.strftime("%d%b%Y_%H%M%S")
        
        logmsg = f'[{dt_string}] {msg}'

        self.ids.container.add_widget(
            OneLineListItem(text=logmsg)
        )
        self.sv.scroll_to(logmsg)
    
    # ======================
    #       record 
    # ======================
    def record(self):
        global mp3Recorder
        self.state = mp3Recorder.record(self.state)
        self.update_labels()

    # ======================
    #       email 
    # ======================
    def email(self):
        global mp3Recorder

        msg = ''
        if self.state != 'ready':
            msg = 'Recording in progress.'
        else:
            recordFilename = mp3Recorder.get_mp3_filename()
            msg = mp3Recorder.email(recordFilename)
        
        self.LogMessage(msg)
        
        self.update_labels()

    # ======================
    #       emailfile 
    # ======================
    def emailfile(self):
        if self.state != 'ready':
            self.LogMessage('Recording in progress.')
            self.update_labels()
            return
        
        # ------------------------------------------------------------------------
        # Root emailfile class will do the actual filechoose and email.
        # See show_load() stuff.
        # 'loadFilename' reported in timer() via update_labels() when available.
        # ------------------------------------------------------------------------
        self.file_choose_root.show_load()
            
        self.update_labels()
        
    # ======================
    #       exit 
    # ======================
    def exit(self):
        global mp3Recorder
        mp3Recorder.exit()

    # ======================
    #       update_labels
    # ======================
    def update_labels(self):
        global mp3Recorder
        global loadFilename

        # --------- Button label updates --------
        if self.state == 'ready':
            self.ids.record_button.text = 'START Recording'

        if self.state == 'recording':
            self.ids.record_button.text = 'STOP Recording'

        # -------- Email and EmailFile updates
        recordFilename = mp3Recorder.get_mp3_filename()
        if exists(recordFilename):
            basefn = basename(recordFilename)
            end_msg = f'[Audio : {self.state}] [Recorded File : {basefn}] '
            self.LogMessage(end_msg)

        if exists(loadFilename):
            basefn = basename(loadFilename)
            end_msg = f'[Email File : {basefn}] '
            self.LogMessage(end_msg)
            # NOTE - clear loacal loadFilename, generates only one update per load.
            loadFilename = ''
            
# ============================================
#               LoadDialog
# ============================================
class LoadDialog(FloatLayout):
    
    def sort_by_date(files, filesystem):    
        import os
        return (sorted(f for f in files if filesystem.is_dir(f)) +
            sorted((f for f in files if not filesystem.is_dir(f)), key=lambda fi: os.stat(fi).st_mtime, reverse = True))
        
    def sort_by_name(files, filesystem):
        return (sorted(f for f in files if filesystem.is_dir(f)) +
                sorted(f for f in files if not filesystem.is_dir(f))) 
        
    default_sort_func = ObjectProperty(sort_by_date)
          
    emailfile = ObjectProperty(None)
    cancel = ObjectProperty(None)
    sort = ObjectProperty(None)
    
# ============================================
#               Root
# ============================================
class Root(FloatLayout):

    #
    # -------- dismiss_popup --------
    #
    def dismiss_popup(self):
        self._popup.dismiss()

    #
    # -------- show_popup --------
    #
    def show_load(self):
        content = LoadDialog(emailfile=self.emailfile, cancel=self.dismiss_popup)
        PATH = "/storage/emulated/0/Music/Mp3Recorder"
        content.ids.filechooser.path = PATH

        self._popup = Popup(title="Load file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()
 
    #
    # -------- emailfile --------
    #
    def emailfile(self, path, selection):
        global mp3Recorder
        global loadFilename
        global emailFileMsg
        msg = ''
        try:
            loadFilename = selection[0]
            if exists(loadFilename):
                emailFileMsg = mp3Recorder.email(loadFilename)
            else:
                emailFileMsg = f'Email File error, file [{loadFilename}] does not exist'
            self.dismiss_popup()
        except:
            pass
        
class Mp3RecorderApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        return Mp3Recorder()

Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)

if __name__ == '__main__':
    Mp3RecorderApp().run()
