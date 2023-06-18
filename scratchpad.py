import subprocess

result = subprocess.run(["dir"], shell=True, capture_output=True, text=True)

print(result.stdout)


import subprocess

p = subprocess.Popen(["python", "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

output, errors = p.communicate()

print(output)

