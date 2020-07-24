This git includes the current version of the interactionmanager and knowledge-tracing
approach used for the HRI paper. If you want to use it, you maybe have to install
some additional dependencies into your python framework. Additionally in this repo
the Web-Interface can be found (src/web). To make it work, please change the IP
address in the index.html.

So, how to use the interactionmanager? It can/must be configured through several
different parameters.

--ip <robot_ip> : This is the IP-Address of the robot e.g.: '192.168.178.21'
--port <robot_port> : This is the Port-Number of the robot. Default value is 9559.
--sysip <the system ip> : The System-IP on which you run the interaction-manager.
--mode <mode> : The mode for the knowledge-tracing ('random', 'adaptive'). 
                The default-value is 'adaptive'.
--sgroups <group_1> <group_2> ...: Specify the skill-groups to be learned. This 
                                   groups have to be specified in the concept-files too.
--L1 <lang_1> : Default is "German".
--L2 <lang_2> : Default is "English".
--rnr <count> : The count of round to the played with the system.
--concepts <path> : The path to the files containing the object-concepts.
                    Default is "../data/study_1/lesson_concepts.csv"
--cbindings <path> : The path to the concept-binding-files for the object.
                     Default is "../data/study_1/lesson_concept_bindings.csv"

An example call could look like:
python interaction_manager.py --ip 192.168.178.22 --port 9559 --sysip 192.168.178.23 --mode "adaptive" --sgroups "type" "color" "size" --L1 "German" --L2 "English" --concepts "../data/study_1/lesson_concepts.csv" --cbindings "../data/study_1/lesson_concept_bindings.csv"

I'm personally using the IDE called Pycharm and configured this parameters 
to my "run-config" for this tool.


Animal experiment:
python interaction_manager.py --ip 169.254.193.70 --port 9559 --sysip 127.0.0.1 --mode "adaptive" --sgroups "type" --L1 "German" --L2 "English" --concepts "../data/study_1/animals_concepts.csv" --cbindings "../data/study_1/animals_concept_bindings.csv" --rnr=30 --gestures=1