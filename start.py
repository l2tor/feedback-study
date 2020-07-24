import subprocess
import shlex
import os

import signal
import sys
import getopt
import time

import webbrowser

# Conditions:
# 1 = no feedback
# 2 = dispreferred feedback
# 3 = preferred feedback


def main(argv):
    strategy = 'best'
    
    ip = '169.254.189.41'
    ip_sys = "137.56.53.1"
    condition = 0
    gestures = 0
    word_set = 1
    #retention = ""
    intro = False
    print argv
    try:
        opts, args = getopt.getopt(argv, "hi:is:c:v:r:", ["ip=","ip_sys=", "condition=", "word_set="])
    except getopt.GetoptError:
        print 'start.py -i <robot_ip> -s <ip_sys> -c <condition> -v <word_set>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'start.py -i <robot_ip> -s <ip_sys> -c <condition> -v <word_set>'
            sys.exit()
        elif opt in ("-i", "--ip"):
            ip = arg
        elif opt in ("-s", "--ip_sys"):
            ip_sys = arg
        elif opt in ("-c", "--condition"):
            try:
                if int(arg) > 0 and int(arg) < 34:
                    condition = int(arg)
            except ValueError:
                pass
        elif opt in ("-v", "--word_set"):
        	try:
        		if int(arg) > 0 and int(arg) < 4:
        			word_set = int(arg)
        	except ValueError:
        		pass

    if condition == 0:
        print 'start.py -i <robot_ip> -s <ip_sys> -c <condition>'
        sys.exit(2)

    print("condition:",condition)
    if condition == 1:
    	strategy = "no"
    elif condition ==2:
    	strategy = "dispreferred"
    elif condition == 3:
    	strategy = "preferred"

    # No need to change directory for our service as it doesn't need file system
    p1 = subprocess.Popen(shlex.split("python \"animalexperimentservice/app/scripts/myservice.py\" --qi-url " + ip + " --word_set " + str(word_set) + " --strategy " + strategy))

    # Interaction manager, however, does!
    os.chdir('interactionmanager/src')
    p2 = subprocess.Popen(shlex.split("python interaction_manager.py --ip " + ip + " --port 9559 --sysip "+ip_sys+" --mode \"" + strategy + "\" --sgroups \"type\" --L1 \"Dutch\" --L2 \"English\" --concepts \"../data/study_1/animals_concepts.csv\" --cbindings \"../data/study_1/animals_concept_bindings.csv\" --rnr=1 --chunks=6 --word_set=" + str(word_set)))
    # p2 = subprocess.Popen(shlex.split("python interaction_manager.py --ip 127.0.0.1 --port 61693 --sysip 192.168.1.24 --mode \"" + strategy + "\" --sgroups \"type\" --L1 \"German\" --L2 \"English\" --concepts \"../data/study_1/animals_concepts.csv\" --cbindings \"../data/study_1/animals_concept_bindings.csv\" --rnr=1 --chunks=6 --gestures=" + str(gestures)))

    time.sleep(2)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    webbrowser.get('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s').open('file://' + dir_path + '/web_2/index.html')

    def signal_handler(signal, frame):
        print('Ctrl+C detected, stopping the services..')
        p1.kill()
        p2.kill()
        time.sleep(1)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to stop experiment')

    loop = True

    while loop:
        time.sleep(1)
        loop = p1.poll() == None or p2.poll() == None


if __name__ == "__main__":
    main(sys.argv[1:])
