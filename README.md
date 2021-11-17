# IntelliJDBPass
A tool for backing up your DB Connections from the IntelliJ IDEA IDE

If you're using IntelliJ IDEA to do your database queries, it's great! However, if you have to switch to a new computer, it's not easy to back up your connection info, especially with your passwords intact. This tool helps you do just that.

At this time, it only works if you are using Keepass to store your connection info (check your Intellij settings). However, it's possible to extend this to provide Keychain support as well.

## Requirements
- Install Python 3
- After downloading this app, you can install everything else by running the command: `pip install -r requirements.txt`

## How To Run
This tool looks for the required info in a few places that IntelliJ stores connection information:
- datasources.xml: the IntelliJ Datasources XML file; has your Connection info (Ex. C:\gitrepos\sandbox\.idea\dataSources.xml)
- Keepass DB file: The Keepass file that has your Passwords. You can find this in the IntelliJ settings (Ex. C:\Users\someuser\AppData\Roaming\JetBrains\IntelliJIdea2021.2/c.kdbx)
- (OPTIONAL) The Datasources.local.xml file: Use this if the datasources.xml file does not contain the usernames (which may or may not be the case) (Ex. Ex. C:\gitrepos\sandbox\.idea\dataSources.local.xml)

## Sample Runs
You can run the tool to pull data for 1 connection or all of them. See the examples below, and use `python intellijdbpass.py -h` for the latest run instructions.

### 1 source, w/user
`python ./intellijdbpass.py -c "beta@localhost" -u C:\gitrepos\sandbox\.idea\dataSources.local.xml -o out-demo-1.csv C:\gitrepos\sandbox\.idea\dataSources.xml "C:/Users/someuser/AppData/Roaming/JetBrains/IntelliJIdea2021.2/c.kdbx"`

### All sources, w/user (if datasources.xml does NOT already have the user info)
`python ./intellijdbpass.py -a -u C:\gitrepos\sandbox\.idea\dataSources.local.xml -o out-demo-all-wuser.csv C:\gitrepos\sandbox\.idea\dataSources.xml "C:/Users/someuser/AppData/Roaming/JetBrains/IntelliJIdea2021.2/c.kdbx"`

### All sources, no user (if datasources.xml already has the user info)
`python ./intellijdbpass.py -a -o out-demo-all-nouser.csv C:\gitrepos\sandbox\.idea\dataSources.xml "C:/Users/someuser/AppData/Roaming/JetBrains/IntelliJIdea2021.2/c.kdbx"`

## NOTE
The script will ask you for the Master Password for the Keepass DB file. If you don't know it or need to set it, you can do that in IntelliJ's settings. (As of this writing, check *Settings > Appearance and Behavior > System Settings > Passwords* & click on the gear on the right side.)
