#!/usr/bin/python

import sys, os, getopt
import hipchat

HIPCHAT_API_TOKEN = '7f5bcfce32f121ae98e1e2eba602bb'
HIPCHAT_ROOM_ID = '48723'
HIPCHAT_MESSAGE_NAME = 'Clone Report'
HIPCHAT_API = hipchat.HipChat(token=HIPCHAT_API_TOKEN)

DEFAULT_CLONEDIGGER_PATH = '/usr/lib/clonedigger/clonedigger/clonedigger.py'
DEFAULT_SOURCE_DIR = '.'
REPORT_DIR_RELATIVE_TO_HOME = 'userContent'
PUBLIC_REPORT_BASE_URL = 'http://build.testflightapp.com'
REPORT_SUFFIX = '-clone_report.html'

def main(argv):
    project_name = None
    ignore_dirs = []
    clonedigger_path = None
    source_dir = None
    help_text = 'process_clone_report.py -p <project_name>\n\nOptional:\n-s Source directory (default is '+DEFAULT_SOURCE_DIR+')\n-i Ignore directory\n-c Clonedigger exec path (Default is '+DEFAULT_CLONEDIGGER_PATH+')\n\nExamples:\nprocess_clone_report.py -p MyProject\nprocess_clone_report.py -p MyProject -i dirToIgnore -i anotherDirToIgnore'
    try:
    	opts, args = getopt.getopt(argv,"hp:i:s:c:")
    except getopt.GetoptError:
        print help_text
        sys.exit(2)        
    for opt, arg in opts:
        if opt == '-h':
            print help_text
            sys.exit()
        elif opt in ("-i"):
            ignore_dirs.append(arg)
        elif opt in ("-p"):
            project_name = arg
        elif opt in ("-s"):
            source_dir = arg
        elif opt in ("-c"):
            clonedigger_path = arg
	
    if project_name is None:
        print 'Must supply project name:\n'+help_text
        sys.exit()

    # Default values
    if clonedigger_path is None:
        clonedigger_path = DEFAULT_CLONEDIGGER_PATH
    if source_dir is None:
        source_dir = DEFAULT_SOURCE_DIR
    ignore_dirs_cmd = ''
    for ignore_dir in ignore_dirs:
        ignore_dirs_cmd += ' --ignore-dir='+ignore_dir
    # Build path to clone report
    home_path = os.getenv("HOME")
    report_name = project_name+REPORT_SUFFIX
    report_path = home_path+'/'+REPORT_DIR_RELATIVE_TO_HOME+'/'+report_name
    relative_report_path = os.path.relpath(report_path)
    # Generate clone report
    print 'Generating clone report:\n'+report_path
    clonedigger_cmd = clonedigger_path+ignore_dirs_cmd+' '+relative_report_path+' '+source_dir
    os.system(clonedigger_cmd)

    # Ensure clone report was generated
    if os.path.isfile(report_path) is False:
        # Clone report can't be found.
        print('Failed to generate clone report')
        sys.exit()

    # Send clone report message to HipChat
    report_url = PUBLIC_REPORT_BASE_URL+'/'+REPORT_DIR_RELATIVE_TO_HOME+'/'+report_name
    #send_clone_report_to_hipchat(project_name, report_url)

def send_clone_report_to_hipchat(project_name, url):
    message = 'Generated clone report for '+project_name+' (<a href="'+url+'">Open</a>)'
    print('Will send HipChat message: '+message)
    return
    HIPCHAT_API.method(url='rooms/message/', 
		method='POST', 
		parameters={'room_id': HIPCHAT_ROOM_ID, 
		'from': HIPCHAT_MESSAGE_NAME, 
		'message': message, 
		'message_format': 'html', 
		'color': 'gray'})

if __name__ == "__main__":
    main(sys.argv[1:])
