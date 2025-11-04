import os
import subprocess
import datetime

# Configure your parameters
user = 'root'
password = 'Oliver.usa1017$'
database_name = 'chalan_admin'
backup_path = r'C:\Users\Division 16 - #33\Dropbox\Contract Paysheets\chalan_pro\backups'

# Create the backup directory if it does not exist
if not os.path.exists(backup_path):
    os.makedirs(backup_path)

# Backup file name with date and time
backup_file = os.path.join(backup_path, f"{database_name}_{datetime.datetime.now().strftime('%Y%m%d')}.sql")
print(backup_file)


# Prepare the command
command = f'mysqldump -u {user} -p{password} {database_name} > "{backup_file}"'

# Execute the command
try:
    # subprocess.run() is used to execute the command
    result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
    print("Backup completed successfully.")
except subprocess.CalledProcessError as e:
    print("Error executing the command:", e)
    print("Standard output:", e.stdout)
    print("Error output:", e.stderr)
