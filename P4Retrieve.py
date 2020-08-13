#!/usr/bin/env python
import argparse
import marshal
from concurrent import futures

# P4Retrieve - Used to download files from a Perforce workspace even when you only have readonly access

# Make sure this is running in the same directory as your P4Client (so 'p4 where' works correctly)
# Easiest way to do this is via right clicking on your workspace root in p4v and selecting "Open command window here"

P4_CONTEXT = ""

def RunP4CommandWithResult(command):
    output = []
    #print("Running Command %s" % command)
    from subprocess import Popen, PIPE
    pipe = Popen( ["p4", "-G" ] + command.split(), stdout=PIPE).stdout
    try:
        while 1:
            record = marshal.load( pipe )
            output.append( record )
    except EOFError:
        pass
    pipe.close()

    if output[0][b'code'] == b'error':
        print("P4 Command: %s failed with error: %s" % (command, output[0][b'data']))
        output = []
    return output

def DownloadFile(p4_file):
    print("Downloading file %s" % p4_file)
        
    # Convert to Local Path
    local_file = RunP4CommandWithResult("%s where %s" % (P4_CONTEXT, p4_file))[0][b'path'].decode("utf-8")

     # Actual download of file
    RunP4CommandWithResult("%s print -q -o %s %s" % (P4_CONTEXT, local_file, p4_file))

    print("Finished downloading: %s" % local_file)

def Run(Target_CL, Synchronous):

    # Get all files in the specified changelist
    print("Finding all files to download...")
    file_info = RunP4CommandWithResult("%s files @=%s" % (P4_CONTEXT, Target_CL))

    if Synchronous == True:
        for file_dict in file_info:
            DownloadFile((file_dict[b'depotFile']).decode("utf-8"))
    else:
        with futures.ProcessPoolExecutor() as pool:
            for file_dict in file_info:
                pool.submit(DownloadFile, (file_dict[b'depotFile']).decode("utf-8"))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-cl", "--changelist",
                    dest="Changelist",
                    help="The changelist we want to download")

    parser.add_argument("-P4", "--P4Context",
                    dest="P4Context",
                    help="Any context data needed to make this run (-p [P4PORT] -c [P4Client] etc")

    parser.add_argument("-ST", "--Synchronous",
                    dest="Synchronous",
                    help="Forces the downloads to be sequential instead of parallel",
                    action="store_const",
                    const=True)

    args = parser.parse_args()

    if(args.P4Context != None):
        P4_CONTEXT = args.P4Context

    if args.Changelist == None:
        args.Changelist = input("Enter the changelist number you want to download: ")
    
    if args.Changelist != None:
        Run(args.Changelist, args.Synchronous)
    else:
        Exception("No changelist passed, aborting!")