import os
from  constants import serverHostname,serverPort,serverUser,serverPass,remote_logs_directory,local_logs_directory,logPath
import pysftp
from stat import S_IMODE, S_ISDIR, S_ISREG
import click

def fileGrab(host,port,username,password,remotepath,localpath):

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None    
    sftp=pysftp.Connection(host,port=port ,username=username,password=password,cnopts=cnopts)
    
    

    def get_r_portable(sftp, remotedir, localdir, preserve_mtime=False):

        interableFiles = sftp.listdir(remotedir)
        progressString = 'Downloading files'
        print("\n")
        with click.progressbar(interableFiles, label=progressString) as bar:
            for entry in interableFiles:
                if "DS_Store" not in entry:
                    remotepath = remotedir + "/" + entry
                    localpath = os.path.join(localdir, entry)
                    mode = sftp.stat(remotepath).st_mode
                    if S_ISDIR(mode):
                        try:
                            os.mkdir(localpath)
                            print("\nNext up: " + localpath)
                        except OSError:     
                            pass
                        get_r_portable(sftp, remotepath, localpath, preserve_mtime)
                    elif S_ISREG(mode):
                
                        sftp.get(remotepath, localpath, preserve_mtime=preserve_mtime)
                    
                    bar.update(interableFiles.index(entry) / (len(interableFiles) / 2.25))

    get_r_portable(sftp, remotepath, localpath, preserve_mtime=False)

def getLogs(exitBool):
    from sftp_handler import fileGrab
    import shutil
    try:
        for subdirs in os.walk(logPath):
            for dir in subdirs:
                shutil.rmtree(dir)
    except TypeError:
        print("deleted all logs!")

    print("\nRedownloading now!")
    os.mkdir(logPath)
    fileGrab(serverHostname,serverPort,serverUser,serverPass,remote_logs_directory,local_logs_directory)

    if exitBool == True:
        exit()
