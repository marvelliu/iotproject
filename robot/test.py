#!/usr/bin/python
import sys;
import getopt;
import twitter;
 
def main(argv):
  api = twitter.Api();
  api.SetCredentials("marvelliu@gmail.com", "idiot@sme"); 
  
  command = ""
  user = ""
 
  if argv[0][0] != "-":
    command = argv[0]
    argv = argv[1:]
  opts, args = getopt.getopt(argv, "c:u:", ["command=", "user="]);
  for opt, arg in opts:
    if opt in ("-c", "--command"):
      command = arg
    elif opt in ("-u", "--user"):
      user = arg
  if user != "":
    account = api.GetUser(user)
    if command == "picture":
      print account.profile_image_url
  else:
    if command == "picture":
      print "picture command requires -u user"
 
 
main(sys.argv[1:])
