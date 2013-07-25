#!/usr/bin/python

import sys, os, getopt
import hipchat

HIPCHAT_MESSAGE_NAME = 'Clone Report'

DEFAULT_CLONEDIGGER_PATH = '/usr/lib/clonedigger/clonedigger/clonedigger.py'
DEFAULT_SOURCE_DIR = '.'
REPORT_SUFFIX = '-clone_report.html'

def main(argv):
    project_name = None
    ignore_dirs = []
    clonedigger_path = None
    source_dir = None
    report_dir = None
    send_notification = False
    hipchat_api_token = None
    hipchat_room_id = None
    public_report_base_url = None
    help_text = 'process_clone_report.py -p <project_name>'
    help_text += '\n\nOptional:\n-s <value> Source directory (default is '+DEFAULT_SOURCE_DIR+')\n-i <value> Ignore directory\n-c <value> Clonedigger exec path (Default is '+DEFAULT_CLONEDIGGER_PATH+')\n-o <value> Output directory for report\n-n Send notification (Requires -a <hipchat_api_token> -r <hipchat_room_id> -u <base_url_for_public_report>)'
    help_text += '\n\nExamples:\nprocess_clone_report.py -p MyProject\nprocess_clone_report.py -p MyProject -i dirToIgnore -i anotherDirToIgnore'
    try:
    	opts, args = getopt.getopt(argv,"hnp:i:s:c:a:r:o:u:")
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
        elif opt in ("-n"):
            send_notification = True
        elif opt in ("-a"):
            hipchat_api_token = arg
        elif opt in ("-r"):
            hipchat_room_id = arg
        elif opt in ("-o"):
            report_dir = arg
        elif opt in ("-u"):
            public_report_base_url = arg
	
    if project_name is None:
        print 'Error: Must supply project name:\n'+help_text
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
    report_name = project_name+REPORT_SUFFIX
    if report_dir is None:
        report_dir = os.getenv("HOME")
    if os.path.isdir(report_dir) is False:
        # Report dir does not exist
        print 'Error: Output directory does not exist:\n'+report_dir
        sys.exit()
    report_path = report_dir+'/'+report_name
    relative_report_path = os.path.relpath(report_path)
    # Generate clone report
    print 'Generating clone report: '+report_path
    clonedigger_cmd = clonedigger_path+ignore_dirs_cmd+' --output='+relative_report_path+' '+source_dir
    print clonedigger_cmd
    os.system(clonedigger_cmd)

    # Ensure clone report was generated
    if os.path.isfile(report_path) is False:
        # Clone report can't be found.
        print 'Error: Failed to generate clone report'
        sys.exit()

    # Send clone report message to HipChat
    if send_notification:
        if hipchat_api_token and hipchat_room_id and public_report_base_url:
            hipchat_api = hipchat.HipChat(token=hipchat_api_token)
            report_url = public_report_base_url+'/'+report_name
            send_clone_report_to_hipchat(hipchat_api, hipchat_room_id, project_name, report_url)
        else:
            print 'Warning: Notification will not be sent because required options were not specified. See help -h'

def send_clone_report_to_hipchat(hipchat_api, room_id, project_name, url):
    if hipchat_api is None:
        print 'Warning: Was unable to establish HipChat API'
        return
    message = 'Generated clone report for '+project_name+' (<a href="'+url+'">Open</a>)'
    print('Will send HipChat message: '+message)
    hipchat_api.method(url='rooms/message/', 
		method='POST', 
		parameters={'room_id': room_id, 
		'from': HIPCHAT_MESSAGE_NAME, 
		'message': message, 
		'message_format': 'html', 
		'color': 'gray'})

if __name__ == "__main__":
    main(sys.argv[1:])
