#!/usr/bin/env python
import argparse
import marshal
from concurrent import futures

# P4Retrieve - Used to download files from a Perforce workspace even when you only have readonly access

# Make sure this is running in the same directory as your P4Client (so 'p4 where' works correctly)
# Easiest way to do this is via right clicking on your workspace root in p4v and selecting "Open command window here"

class Perforce:
    # Target CL
    Changelist = 0

    # Optional Credentials
    CredentialString = ""

    def __init__(self, InChangelist, InCredentials):
        self.Changelist         = InChangelist
        self.CredentialString   = InCredentials
        

    def RunP4CommandWithResult(self, command):
        output = []
        from subprocess import Popen, PIPE
        p4_command = "p4 -G %s %s" % (self.CredentialString, command)
        #print(p4_command)
        pipe = Popen(p4_command.split(), stdout=PIPE).stdout
        try:
            while 1:
                record = marshal.load( pipe )
                output.append( record )
        except EOFError:
            pass
        pipe.close()
        if output[0][b'code'] == b'error':
            print("P4 Command: '%s' failed with error: [%s]" % (p4_command, output[0][b'data']))
            output = []
        return output

    def DownloadFile(self, p4_file):

        print("Downloading file %s" % p4_file)
    
        # Convert to Local Path
        local_file = self.RunP4CommandWithResult("where %s" % p4_file)[0][b'path'].decode("utf-8")

         # Actual download of file
        self.RunP4CommandWithResult("print -q -o %s %s@=%s" % (local_file, p4_file, self.Changelist))

        print("Finished downloading: %s" % local_file)

def Run(P4_Object, AsyncCommands):

    # Get all files in the specified changelist
    print("Finding all files to download...")
    file_info = P4_Object.RunP4CommandWithResult("files @=%s" % P4_Object.Changelist)

    if AsyncCommands == True:
        with futures.ProcessPoolExecutor() as pool:
            for file_dict in file_info:
                pool.submit(P4_Object.DownloadFile, file_dict[b'depotFile'].decode("utf-8"))
    else:
        for file_dict in file_info:
            P4_Object.DownloadFile(file_dict[b'depotFile'].decode("utf-8"))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-cl", "--changelist",
                    dest="Changelist",
                    help="The changelist we want to download")

    parser.add_argument("-p4", "--credentials",
                    dest="P4Creds",
                    help="Any context data needed to make this run (-p [P4PORT] -c [P4Client] etc",
                    default="")

    parser.add_argument("-st", "--Synchronous",
                    dest="Synchronous",
                    help="Forces the downloads to be sequential instead of parallel",
                    action="store_const",
                    const=True)

    args = parser.parse_args()

    if args.Changelist == None:
        args.Changelist = input("Enter the changelist number you want to download: ")
    
    if args.Changelist != None:
        p4_object = Perforce(args.Changelist, args.P4Creds)
        Run(p4_object, not args.Synchronous)
    else:
        Exception("No changelist passed, aborting!")