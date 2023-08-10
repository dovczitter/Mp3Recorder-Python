# 1. Mp3Recorder, Python demo project

Android 11 Python app to record and email mp3 files.

# 2. Design and component review

    - Android Kivymd framework app gui interface
    - User buttons drive Record, Email, EmailFile and Exit.
    - Timed log activity updates.

========== Mp3Recorder Main Screen [*Wifi UP*] [*Info log*] ========== 
![Main Screen](/screenshots/MainScrn.png)

========== Mp3Recorder Email File popup screen ========== 
![EmailFile Screen](/screenshots/EmailFileScrn.png)


# 3. Useage
    - [START Recording] changes to [STOP Recording],say something to record.
    - [STOP Recording] stops the recording and changes back to [START Recording] for the next recording, log shows Mp3Recorder_<datestamp>.mp3 recorded file
    - [Email] will email the current recorded file to the Mp3Recorder.csv 'Receiver' list.
    - [Email File] brings up a popup list of previously recorded files, tap/highlight the requested file, tap [EmailFile] to email, [Cancel] to return to main screen.
    - [Exit] quit the app.
# 4. Buid Mp3Recorder.apk
    - Android app, Mp3Recorder.apk, is created by Buildozer on Linux
    - Install Unbutu Linux on Windows: 
        <https://ubuntu.com/tutorials/install-ubuntu-on-wsl2-on-windows-11-with-gui-support#1-overview>
        <https://stackoverflow.com/questions/28210637/unable-to-ssh-localhost-permission-denied-publickey-connection-closed-by>

        NOTE this Windows WSL configuration requirement:
        <https://docs.microsoft.com/en-us/windows/wsl/install>.

        If you're running Ubuntu on Windows Subsystem for Linux, there will not be a preinstalled public key or authorized keys list, so you'll need to generate your own.
        If you don't already have openssh-server installed:
        	1.	sudo apt-get upgrade
        	2.	sudo apt-get update
        	3.	sudo apt-get install openssh-server
        	4.	sudo service ssh start
        Then take the following steps to enable sshing to localhost:
	        1.	cd ~/.ssh
            2.	ssh-keygen to generate a public/private rsa key pair; use the default options
	        3.	cat id_rsa.pub >> authorized_keys to append the key to the authorized_keys file
	        4.	chmod 640 authorized_keys to set restricted permissions
	        5.	sudo service ssh restart to pickup recent changes
	        6.	ssh localhost

    - Install Visual Code, 
        <https://linuxize.com/post/how-to-install-visual-studio-code-on-ubuntu-20-04/>
    - Install Python
        <https://linuxize.com/post/how-to-install-python-on-ubuntu-22-04/>
    - Install PIP
        <https://linuxize.com/post/how-to-install-pip-on-ubuntu-20.04/>
    - Install Buildozer 
        <https://buildozer.readthedocs.io/en/latest/installation.html>
        Setup a virtual enviornment within Visual Code, which containerizes the build [create new folder, '.venv']
        Visual Code->Terminal->New Terminal.
    
        $ virtualenv .venv
        dovczitter@DESKTOP-N4F7Q65:~/Mp3Recorder$ source .venv/bin/activate
        (.venv) dovczitter@DESKTOP-N4F7Q65:~/Mp3Recorder$
        To create a new buildozer.spec file,run
        $ buildozer init
        Otherwise, use the one buildozer.spec in gitHub, or edit the new one line by line.

        Assuming *.py, *.csv, *.png and .gitignore are installed, to generate the bin/Mp3Reorder.apk, run:
        $  buildozer -v android debug 
        First build will take many minutes, must see the ending 'BUILD SUCCESSFUL' to generate an apk.
        Next build should be less than a minute, to fully rebuild, 'rm -rf .bin'.
# 5. Installation
    - I used this tablet:
        YQSAVIOR Tablet Android 11 Tablets 7 inch
        Available on Amazon, $42.99
        <https://www.amazon.com/gp/product/B09LHMMJ2Q/ref=pe_2313390_735257480_em_1p_0_lm>
    - Install PlayStore 'File Manager Plus',free
    - Install PlayStore 'OutLook' free, create and save your new email username and password.
    - Enable tablet for debug mode, which allows for direct usb
        <https://www.youtube.com/watch?v=CCFMai4JmeM>
    - File transfer the Mp3Recorder.apk to the Android 'Downloads' folder
      NOTE - Windows explorer to the tablet's 'Internal shared storage' on connecting the usb in DEBUG mode.
    - Enable the tablet's Wifi.
    - Suggest that you edit the Mp3Recorder.csv file and copy via explore to the tablet's 'Main storage > Documents > Mp3Recorder' folder.
    - Requires a tablet 'outlook' account, install via PlayStore.
    - Mp3Recorder.csv configuration, <key>,<value>:
        - Outlook host and port:
            Host,smtp-mail.outlook.com
            Port,587
        - Outlook login username:
            Username,myusername@outlook.com
        - Outlook login password:
            Password,@Mypassword
        - Outlook email 'From':
            Sender,myusername@outlook.com
        - Outlook email 'To' list:
        - wip - requires both yahoo and outlook, may be a bug or outlook requirement.
            Receiver,myusername@outlook.com,buddy1@addr1.com,buddy2@addr2.com,
        - Recorded base filename:
            Mp3FileRoot,Mp3RecorderTest

    - Run the app via 'File Magager +', then 'Downloads', tap the mp3recorderapp.apk file
    - Choose 'Install'
    - Choose 'Open'
    - If all works, the app comes up, top line shows per-second update, and [Wifi *UP*] if enabled.
    - Nice to do, would be the enable premission 'Allow management of all files'. Could not get the app to do this automatically. Requirement to access 'Main storage > Documents > Mp3Recorder > Mp3Recorder.csv' file. This file loaded from the apk install, programically moved to the Documents folder if not present, allows for external Mp3Recorder.csv configuration updates.

    Two configuration choices:
        - builddozer with modified Mp3Recorder.csv
        - delete 'Main storage > Documents > Mp3Recorder > Mp3Recorder.csv'
        - Uninstall current [File Manager > Apps > Mp3Recorder | UNINSTALL]
        - Install new Mp3Recorder.apk via 'File Manager +'
    -or-
        - 'Allow management of all files', see above
        - USB copy Windows edited Mp3Recorder.csv to the tables 'Internal shared storage\Documents\Mp3Recorder\Mp3Recorder.csv' 
