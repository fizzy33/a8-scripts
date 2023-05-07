#!/usr/bin/env python


import os
from subprocess import call
import shutil

account = "foo@bar.com"


print(""""

So you want to backup an email account.  You should have already hopped into
gmail admin made sure the account is active and reset the password to something known.

Also you would have done something like

pip install --user gmvault

gmvault does some funky browser stuff to get an oauth token and this behavious is different on each platform.
Worst case just quit whatever browser it sticks you in and get back to the terminal and it will give you an oauth url cut
paste that into an incognito browser window and login as that user and get the oauth token that is provided at the end.  Cut
and paste that into the session.

Note it is important to use an incognito session so that you are logging into that users account and not your own.

""")



raw_input("we will delete any pre-existing gmvault databases or settings on this machine press ENTER to continue")


def delete_tree(path):
    epath = os.path.expanduser(path)
    if os.path.exists(epath):
        print("removing " + epath)
        shutil.rmtree(epath)


delete_tree("~/.gmvault")
delete_tree("~/gmvault-db")

print("running gmvault sync")
call(["gmvault", "sync", account])


print("""

!!! SUCCESS !!!

okay looks like that worked...  Now do something like this to rsync the backed up user to nettle.accur8.io


rsync --compress --archive --partial --progress --stats ~/gmvault-db user@server@bar:/ebs/former-employees-emails/foo@bar


""")
