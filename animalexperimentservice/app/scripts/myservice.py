#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A sample showing how to have a NAOqi service as a Python app.
"""

__version__ = "0.0.3"

__copyright__ = "Copyright 2015, Aldebaran Robotics"
__author__ = 'YOURNAME'
__email__ = 'YOUREMAIL@aldebaran.com'

import qi
import stk.runner
import stk.events
import stk.services
import stk.logging
import random
from threading import Thread
import json
import datetime
from TCP_Client import TCPClient
import sys
import getopt
import time

is_test = False #shorter version to test main functionalities

word_set = ""
strategy = ""

feedback = ""
robot_name = ""
#woordenset = 2


class ALAnimalExperimentService(object):
	"NAOqi service for animal experiment."
	APP_ID = "com.aldebaran.ALMyService"

	def __init__(self, qiapp):
		self.conn_man = TCPClient("interactionmanager", self, "127.0.0.1", 1111)

		# generic activity boilerplate
		self.qiapp = qiapp
		self.events = stk.events.EventHelper(qiapp.session)
		self.s = stk.services.ServiceCache(qiapp.session)
		self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

		# self.s.ALMemory.raiseEvent("show_screen", "game")
		# [JAN] register for gaze 
		self.events.subscribe("toggle_facetracking", "ALAnimalExperimentService", self._toggle_facetracking_callback)
		self.last_known_child_location = None

		# Set audio volume to 80 and enable blinking eyes
		try:
			self.s.ALAudioDevice.setOutputVolume(80)
		except:
			pass

		try:
			self.s.ALBehaviorManager.startBehavior("custom/blinking")
		except:
			pass
		#self.s.ALBehaviorManager.startBehavior("custom/blinking")
		#self.s.ALBehaviorManager.startBehavior("pointing/tablet")
		self.woordenset = int(woordenset)
		self.gestures = True
		self.paused = False
		self.intro = True
		self.next_animal_intro = False
		print ("word set is ", self.woordenset)
		if self.woordenset == 1:
			self.target_words = {
				"DOG": {
					"type": "noun",
					"English": "dog",
					"Article": "de",
					"UnArticle": "een",
					"Dutch": "hond",
					"Color": "BROWN",					
					"SoundSetName": " \\prn= d O: g \\ ",
				},
				"FROG": {
					"type": "noun",
					"English": "frog",
					"Article": "de",
					"UnArticle": "een",
					"Dutch": "kikker",
					"Color": "BROWN",					
					"SoundSetName": " \\prn= f r O: k\\ ",
				},
				"PARROT": {
					"type": "noun",
					"English": "parrot",
					"Article": "de",
					"UnArticle": "een",
					"Dutch": "papagaai",
					"Color": "BROWN",			
					"SoundSetName": " \\prn=p E r @ t \\ ",
				},
				"BUTTERFLY": {
					"type": "noun",
					"English": "butterfly",
					"UnArticle": "een",
					"Article": "de",
					"Dutch": "vlinder",
					"Color": "BROWN",
					"SoundSetName": " batterflaj ",
				},
				"SHARK": {
					"type": "noun",
					"English": "shark",
					"UnArticle": "een",
					"Article": "de",
					"Dutch": "haai",
					"SoundSetName": " \\prn=S j A r k\\ ",
				},
				"RHINO": {
					"type": "noun",
					"English": "rhino",
					"UnArticle": "een",
					"Article": "de",
					"Dutch": "neushoorn",
					"Color": "BROWN",
					"SoundSetName": " \\prn= r A i n o :\\ ",
				}

			}
		elif self.woordenset == 2:
			self.target_words = {
				"BIRD": {
					"type": "noun",
					"English": "bird",
					"Article": "de",
					"UnArticle": "een",
					"Dutch": "vogel",
					"Color": "BROWN",
					"SoundSetName": " \\prn= b 2 r d \\ ",
				},
				"CHICKEN": {
					"type": "noun",
					"English": "chicken",
					"Article": "de",
					"UnArticle": "een",
					"Dutch": "kip",
					"Color": "BROWN",
					"SoundSetName": " \\prn=t s I k @ n\\ ",
				},
				"SNAKE": {
					"type": "noun",
					"English": "snake",
					"Article": "de",
					"UnArticle": "een",
					"Color": "BROWN",
					"Dutch": "slang",
					"SoundSetName": " \\prn=s n e @ k :\\ ",
				},
				"WHALE": {
					"type": "noun",
					"English": "whale",
					"UnArticle": "een",
					"Article": "de",
					"Dutch": "walvis",
					"Color": "BROWN",
					"Behavior": "Animals/Seal",
					"SoundSetName": " weel ",
				},
				"HIPPO": {
					"type": "noun",
					"English": "hippo",
					"German": "Hase",
					"UnArticle": "een",
					"Article": "de",
					"Dutch": "nijlpaard",
					"Color": "RED",
					"Behavior": "Animals/Rabbit",
					"SoundSetName": " hippo ",
				},
				"SNAIL": {
					"type": "noun",
					"English": "snail",
					"UnArticle": "een",
					"Article": "de",
					"Dutch": "slak",
					"Color": "BROWN",
					"SoundSetName": " \\prn=s n e @ l :\\ ",
				}

			}            
		else:
			self.target_words = {
				"HORSE": {
					"type": "noun",
					"English": "horse",
					"Article": "het",
					"UnArticle": "een",
					"Dutch": "paard",
					"Color": "BROWN",
					"SoundSetName": " \\prn=h O1 rr s s\\ ",
				},
				"RABBIT": {
					"type": "noun",
					"English": "rabbit",
					"Article": "het",
					"UnArticle": "een",
					"Dutch": "konijn",
					"Color": "BROWN",
					"SoundSetName": " \\prn=r E1 b @ t\\ ",
				},
				"PIG": {
					"type": "noun",
					"English": "pig",
					"Article": "het",
					"UnArticle": "een",
					"Color": "BROWN",
					"Dutch": "varken",
					"SoundSetName": " \\prn=p I g\\ ",
				},
				"SQUIRREL": {
					"type": "noun",
					"English": "squirrel",
					"UnArticle": "een",
					"Article": "de",
					"Dutch": "eekhoorn",
					"Color": "BROWN",
					"SoundSetName": " \\prn=s k w 2 r r l :\\ ",
				},
				"SEAL": {
					"type": "noun",
					"English": "seal",
					"UnArticle": "een",
					"Article": "de",
					"Dutch": "zeehond",
					"Color": "RED",
					"SoundSetName": " \\prn=s i @ l\\ ",
				},
				"DEER": {
					"type": "noun",
					"English": "deer",
					"UnArticle": "een",
					"Article": "het",
					"Dutch": "hert",
					"Color": "BROWN",
					"SoundSetName": " deer ",
				}

			}                  
		self.unicorn = {
					"type": "noun",
					"English": "unicorn",
					"UnArticle": "een",
					"Article": "de",
					"Dutch": "eenhoorn",
					"Color": "WHITE",
					"SoundSetName": "joenicorn",
				}


		self.isFirstTestRun = True
		self.isTestRun = True
		self.isLastAnswerWrong = False

		self.round_number = 1

		if is_test:
			self.num_rounds = 2
		else:
			self.num_rounds = 24


		# Subscribe to events we can expect from the interaction manager
		self.s.ALMemory.subscribeToEvent("animated_tts", "ALAnimalExperimentService", "animated_tts_event")
		self.s.ALMemory.subscribeToEvent("describe_object", "ALAnimalExperimentService", "describe_object_event")
		self.s.ALMemory.subscribeToEvent("test", "ALAnimalExperimentService", "test_event")

		self.s.ALMemory.subscribeToEvent("skip_object", "ALAnimalExperimentService", "skip_object_event")
		self.s.ALMemory.subscribeToEvent("explain_skill", "ALAnimalExperimentService", "explain_skill_event") #verwijst naar give_explanation in the interaction manager
		self.s.ALMemory.subscribeToEvent("explain_skill2", "ALAnimalExperimentService", "explain_skill_event2") #verwijst naar give_explanation in the interaction manager

		self.s.ALMemory.subscribeToEvent("dialog_stop", "ALAnimalExperimentService", "stop_tts_event")
		self.s.ALMemory.subscribeToEvent("motivate_request", "ALAnimalExperimentService", "motivate_request_event")
		self.s.ALMemory.subscribeToEvent("sing_a_song", "ALAnimalExperimentService", "sing_a_song_event")
		self.s.ALMemory.subscribeToEvent("repeat_answer", "ALAnimalExperimentService", "repeat_answer_event")
		self.s.ALMemory.subscribeToEvent("look_at", "ALAnimalExperimentService", "look_at_event")
		self.s.ALMemory.subscribeToEvent("round_nr", "ALAnimalExperimentService", "round_number_update_event")
		self.s.ALMemory.subscribeToEvent("gui/buttons", "ALAnimalExperimentService", "gui_buttons_event")
		
		# So far, these are actually used for the animal experiment
		self.s.ALMemory.subscribeToEvent("vadFake", "ALAnimalExperimentService", "vadFake_event")
		self.s.ALMemory.subscribeToEvent("vadFakeFalse", "ALAnimalExperimentService", "vadFakeFalse_event")
		# self.s.ALMemory.subscribeToEvent("start", "ALAnimalExperimentService", "start_event")
		# self.s.ALMemory.subscribeToEvent("pause", "ALAnimalExperimentService", "pause_event")
		# self.s.ALMemory.subscribeToEvent("exit", "ALAnimalExperimentService", "exit_event")
		self.s.ALMemory.subscribeToEvent("did_not_understand", "ALAnimalExperimentService", "did_not_understand_event")
		# self.s.ALMemory.subscribeToEvent("resume", "ALAnimalExperimentService", "resume_event")
		self.s.ALMemory.subscribeToEvent("test_run", "ALAnimalExperimentService", "test_run_event")
		self.s.ALMemory.subscribeToEvent("introduce_word", "ALAnimalExperimentService", "introduce_word_event")
		self.s.ALMemory.subscribeToEvent("introduce_word2", "ALAnimalExperimentService", "introduce_word_event2")

		self.s.ALMemory.subscribeToEvent("practice", "ALAnimalExperimentService", "practice_event")
		self.s.ALMemory.subscribeToEvent("validation", "ALAnimalExperimentService", "show_validation_event")
		self.s.ALMemory.subscribeToEvent("start_button_clicked", "ALAnimalExperimentService", "start_button_clicked_event")
		self.s.ALMemory.subscribeToEvent("gesture_condition", "ALAnimalExperimentService", "gesture_condition_event")
		self.s.ALMemory.subscribeToEvent("tts", "ALAnimalExperimentService", "tts_event")
		self.s.ALMemory.subscribeToEvent("ALAnimatedSpeech/EndOfAnimatedSpeech", "ALAnimalExperimentService", "output_finished_event")
		self.s.ALMemory.subscribeToEvent("end_of_interaction", "ALAnimalExperimentService", "end_of_interaction_event")
		self.s.ALMemory.subscribeToEvent("chunk_changed", "ALAnimalExperimentService", "chunk_changed_event")
		self.s.ALMemory.subscribeToEvent("recap", "ALAnimalExperimentService", "recap_event")
		self.s.ALMemory.subscribeToEvent("next_animal_intro", "ALAnimalExperimentService", "next_animal_intro_event")
		self.s.ALMemory.subscribeToEvent("berry_dropped", "ALAnimalExperimentService", "berry_dropped_event")

		self.pos_feedback = ["Goed gedaan!", "Knap hoor", "Ja goed gedaan!", "Ga zo door!", "Super!", "Heel knap gedaan"]
		self.neg_feedback = ["Helaas, dat was niet goed. [explanation]", "Sorry deze is niet goed. [explanation]", "Helaas, [explanation] probeer het nog een keer", "Jammer, [explanation] we proberen het nog eens", "Ah jammer, denk nog even goed na, [explanation]","Super goed geluisterd, maar dat was niet goed [explanation] probeer het nog eens"]

		self.last_pos_feedback_pick = ''
		self.last_feedback_pick = ''

		self._word_first_time = False
		self._output_finished = False
		self._request_answer = False
		self._vad_detected = False
		self._vad_correct = False
		self._finished = (False, False)
		self._chunk_changed = False
		self._recap = False
		self._val_arrived = False
		self._child_name = ""
		self.childNamePpnrRobotName = ""
		self._ra_thread = None
		self._exit_interaction = False
		self.running = False
		self.post_test = False
		self._intro = True
		self._reengage_strategy = None
		self.post_result = False
		self.post_test_target_word = None
		global word_set
		self.word_set = word_set == "1"
		global strategy
		self.strategy = strategy
		print("================== strategy = " + strategy + "==========================\n")

		#self.s.ALMemory.raiseEvent("log_dit_even", "Feedback strategy is set to: " + str(strategy))

		self.skills_seen = []
		self.distraction_counter = 0
		self.reengage_counter = 0
		self.verbalize_actions = { "task_2": ["Ik probeer een dier te zoeken wat je nog niet kent.",
											 "Mm ik zoek een dier wat je nog niet kent."],
								  "intro": "Wij gaan vandaag Engelse woorden voor verschillende dieren leren.",
								  "word_first_time": ["Ik zoek nog een keertje een nieuw dier uit. Probeer het te vinden","Ik ga weer een nieuw dier zoeken.","Nu weer een nieuw dier."]}

		self.verbalize_index = {"task_1": 0, "task_2": 0, "task_3": 0, "task_4": 0, "word_first_time": 0}

		self.reeng_strategies = {"tired": ["Engagement/Tired1", "Engagement/Tired2"],
								 "activity": ["Engagement/Activity1", "Engagement/Activity2"],
								 "distractionLow": ["Engagement/distractionLow1", "Engagement/distractionLow2"],
								 "distractionHigh": ["Engagement/DistractionHigh", ]}
		self.track_feedback = {}
		
		for animal in self.target_words:
		   
			n = random.randint(0,2)
			#self.track_feedback[animal]= [0,1]
			if n == 0:    
				self.track_feedback[animal] = [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]
			elif n == 1:    
				self.track_feedback[animal] = [1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1]       
			else:    
				self.track_feedback[animal] = [0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]   
			self.s.ALMemory.raiseEvent("log", "[animal] " + animal + "[feedback order]: "+ str(self.track_feedback[animal]))                

		Thread(target=self.start, args=()).start()

	def berry_dropped_event(self, key, value):
		self.post_result = True

	def vadFake_event(self, key, value):
		"""Correct word has been spoken by the child"""
		if self.conn_man.acceptVAD:
			print "vadFake"
			self.conn_man.acceptVAD = False
			self._vad_detected = True
			self._vad_correct = True

	def vadFakeFalse_event(self, key, value):
		"""Wrong word has been spoken by the child"""
		if self.conn_man.acceptVAD:
			print "vadFakeFalse"
			self._vad_detected = True
			self._vad_correct = False

	def next_animal_intro_event(self, key, value):
		self.next_animal_intro = True

	def recap_event(self, key, value):
		self._recap = True

	def chunk_changed_event(self, key, value):
		print "==== chunk changed arrived! ===="
		self._chunk_changed = True

	def end_of_interaction_event(self, key, value):
		self._finished = (True, json.loads(value))

	def output_finished_event(self, key, value):
		print "output finished"
		self._output_finished = True

	def tts_set_language(self, lang):
		self.s.ALTextToSpeech.setLanguage(lang)

		if lang == "English":
			self.s.ALTextToSpeech.setParameter("defaultVoiceSpeed", 75)
			self.s.ALTextToSpeech.setParameter("pitchShift", 1.1)
			self.s.ALTextToSpeech.setVolume(1.0)
			self.s.ALAnimatedSpeech.setBodyLanguageMode(0)
		else:
			self.s.ALTextToSpeech.setVolume(0.6)
			self.s.ALTextToSpeech.setParameter("defaultVoiceSpeed", 80)
			self.s.ALTextToSpeech.setParameter("pitchShift", 1.2)
			self.s.ALAnimatedSpeech.setBodyLanguageMode(0)

	def tts_event(self, key, value):
		self.tts_set_language('Dutch')
		self.s.ALAnimatedSpeech.say(value)

	def pos_feedback_picker(self):
		current = self.last_pos_feedback_pick    
		while self.last_pos_feedback_pick == current:
			current = random.choice(self.pos_feedback)

		return current

	def feedback_picker(self, answer):
		if answer == "correct":
			current = self.last_pos_feedback_pick
			while self.last_feedback_pick == current:
				current = random.choice(self.pos_feedback)
		else:
			
			current = self.last_feedback_pick
			while self.last_feedback_pick == current:
				current = random.choice(self.neg_feedback)  
		return current        


	def gesture_condition_event(self, key, value):
		if value == 1:
			self.gestures = True
		else:
			self.gestures = False

	def did_not_understand_event(self, key, value):
		self.logger.info("did_not_understand_event")
		print "== Child did not understand the game =="
		self.s.ALTextToSpeech.say("Ok, geen probleem, dan leggen we het nog een keertje uit!")

	def animated_tts_event(self, key, value):
		self.logger.info("animated_tts_event")

	def describe_object_event(self, key, value):
		self.logger.info("describe_object_event")

	def skip_object_event(self, key, value):
		self.logger.info("skip_object_event")

	def explain_skill_event(self, key, value):
		self.logger.info("explain_skill_event")

	def explain_skill_event2(self, key, value):
		self.logger.info("explain_skill_event2")    

	def stop_tts_event(self, key, value):
		self.logger.info("stop_tts_event")

	def motivate_request_event(self, key, value):
		self.logger.info("motivate_request_event")

	def sing_a_song_event(self, key, value):
		self.logger.info("sing_a_song_event")

	def start_button_clicked_event(self, key, value):
		self.experiment_start = datetime.datetime.now()
		self.s.ALTextToSpeech.say("Super!")
		self.s.ALTextToSpeech.say("Laten we beginnen!")
		self.s.ALMemory.raiseEvent("describe_object", "")

	def practice_event(self, key, value):       
		self.tts_set_language("Dutch")
		if self.isFirstTestRun and not self.isLastAnswerWrong:
			self.s.ALMemory.raiseEvent("show_images", False)
			practice_1 = ["Kijk!",
						  "Er zijn allemaal dieren op het scherm.",
						  "\\pau=500\\Ok.",
						  "Laten we even oefenen\\pau=250\\"]
			
			for line in practice_1:
				print line
				self.s.ALTextToSpeech.say(line)

		self.introduce_word_event(key, value)

	def reengage(self):
		return False


	def introduce_word_event2(self, key, value):
		if self._reengage_strategy and not self.isLastAnswerWrong:
			if self.reengage():
				return
		self.tts_set_language("Dutch")
		_data = json.loads(value)
		word = _data["word"]
		self._word_first_time = _data["first_time"]

		if self.paused:
			return

		self.logger.info("introduce_word_event2")
		# self.s.ALMemory.raiseEvent("activate_images", True)
		if self.isFirstTestRun:
			self.s.ALMemory.raiseEvent("show_images", False)
			print self._child_name
			if not self.isLastAnswerWrong:                 
				self.s.ALAnimatedSpeech.say("ik zie, ik zie wat jij niet ziet $toggle_facetracking=False en het is een \\pau=500\\ eenhoorn. $toggle_facetracking=True")
				self.s.ALMemory.raiseEvent("activate_images", True)
				if (self.s.ALBehaviorManager.isBehaviorInstalled("pointing/tablet")):
        # Check that it is not already running.
        			#if (not behavior_mng_service.isBehaviorRunning(behavior_name))
					self.s.ALBehaviorManager.startBehavior("pointing/tablet")
				self.s.ALAnimatedSpeech.say("\\pau=300\\ Klik maar met je vinger op de \\pau=500\\ eenhoorn.")
			else:
				if (self.s.ALBehaviorManager.isBehaviorInstalled("pointing/tablet")):
					self.s.ALBehaviorManager.startBehavior("pointing/tablet")
				self.s.ALAnimatedSpeech.say("Klik maar met je vinger op de \\pau=500\\ eenhoorn.")
				self.s.ALMemory.raiseEvent("activate_images", True)
			self._ra_thread = Thread(target=self.request_answer_val, args=(self.unicorn, True))

		else:
			if not self.isLastAnswerWrong:
				if not self.isTestRun and self.round_number == 2:
					self.s.ALTextToSpeech.say("Laten we naar het volgende dier gaan. \\pau=250\\")
				if 2 < self.round_number < 6:
					self.s.ALTextToSpeech.say("Hier komt het volgende dier. \\pau=250\\")
				if 5 < self.round_number < 9:
					self.s.ALTextToSpeech.say("Daar gaan we weer! \\pau=250\\")

				if self.isTestRun:
					self.s.ALMemory.raiseEvent("show_images", False)
					self.s.ALAnimatedSpeech.say("ik zie, ik zie wat jij niet ziet $toggle_facetracking=False en het is een \\pau=500\\."
												+ self.unicorn['SoundSetName'] + ". $toggle_facetracking=True")
					self.s.ALMemory.raiseEvent("activate_images", True)
					if (self.s.ALBehaviorManager.isBehaviorInstalled("pointing/tablet")):
						self.s.ALBehaviorManager.startBehavior("pointing/tablet")
					self.s.ALAnimatedSpeech.say("\\pau=300\\ Klik maar met je vinden op de "+ "\\pau=500\\ "
												+ self.unicorn['SoundSetName'] + ".")

					# self.s.ALMemory.raiseEvent("activate_images", True)
					self._ra_thread = Thread(target=self.request_answer_val, args=(self.unicorn, False))
					self._ra_thread.start()
					return
				elif self.target_words[word]["type"] == "noun":
					if self.verbalization:
						# verba = self.verbalize_actions[_data["action"]]
						# random.shuffle(verba)
						if word in self.skills_seen:
							_str = self.verbalize_actions[_data["action"]][self.verbalize_index[_data["action"]]]
							self.verbalize_index[_data["action"]] += 1
							if len(self.verbalize_actions[_data["action"]]) == self.verbalize_index[_data["action"]]:
								self.verbalize_index[_data["action"]] = 0
							self.s.ALAnimatedSpeech.say(_str)
						elif len(self.skills_seen) > 0:
							_str = self.verbalize_actions["word_first_time"][self.verbalize_index["word_first_time"]]
							self.verbalize_index["word_first_time"] += 1
							if len(self.verbalize_actions["word_first_time"]) == self.verbalize_index["word_first_time"]:
								self.verbalize_index["word_first_time"] = 0
							self.s.ALAnimatedSpeech.say(_str)
						if word not in self.skills_seen:
							self.skills_seen.append(word)
					self.s.ALMemory.raiseEvent("show_images", False)
					self.s.ALAnimatedSpeech.say("ik zie, ik zie wat jij niet ziet $toggle_facetracking=False en het is "
												+ self.target_words[word]['UnArticle'] + " \\pau=500\\."
												+ self.target_words[word]['SoundSetName'] + " $toggle_facetracking=True")
						# self.s.ALMemory.raiseEvent("activate_images", True)
			else:
				self.s.ALMemory.raiseEvent("show_images", False)

				if self.isTestRun:
					if (self.s.ALBehaviorManager.isBehaviorInstalled("pointing/tablet")):
						self.s.ALBehaviorManager.startBehavior("pointing/tablet")
					self.s.ALAnimatedSpeech.say("$toggle_facetracking=False Klik maar op de " + " \\pau=500\\ "
												+ self.unicorn['Dutch'] + " $toggle_facetracking=True")
					self.s.ALMemory.raiseEvent("activate_images", True)
					self._ra_thread = Thread(target=self.request_answer_val, args=(self.unicorn, False))
					self._ra_thread.start()
					return
				else:
					if self.target_words[word]["type"] == "noun":
						if (self.s.ALBehaviorManager.isBehaviorInstalled("pointing/tablet")):
							self.s.ALBehaviorManager.startBehavior("pointing/tablet")
						self.s.ALAnimatedSpeech.say("Klik maar op " + self.target_words[word]['Article'] + " \\pau=500\\ "
													+ self.target_words[word]['Dutch'])
			self.s.ALMemory.raiseEvent("activate_images", True)
			self._ra_thread = Thread(target=self.request_answer_val, args=(self.target_words[word], False))
		self._ra_thread.start()
		if self.paused:
			return		

	def introduce_word_event(self, key, value):
		if self._reengage_strategy and not self.isLastAnswerWrong:
			if self.reengage():
				return
		self.tts_set_language("Dutch")
		_data = json.loads(value)
		word = _data["word"]
		self._word_first_time = _data["first_time"]

		if self.paused:
			return

		self.logger.info("introduce_word_event")
		# self.s.ALMemory.raiseEvent("activate_images", True)
		if self.isFirstTestRun:
			self.s.ALMemory.raiseEvent("show_images", False)
			self.s.ALMemory.raiseEvent("show_images", False)
			print self._child_name
			#self.s.ALAnimatedSpeech.say(self._child_name)
			if not self.isLastAnswerWrong:                 
				self.s.ALAnimatedSpeech.say("ik zie, ik zie wat jij niet ziet $toggle_facetracking=False en het is een \\pau=500\\ eenhoorn. $toggle_facetracking=True")
				self.s.ALMemory.raiseEvent("activate_images", True)
				if (self.s.ALBehaviorManager.isBehaviorInstalled("pointing/tablet")):
					self.s.ALBehaviorManager.startBehavior("pointing/tablet")
				self.s.ALAnimatedSpeech.say("\\pau=300\\ Klik maar met je vinger op de \\pau=500\\ eenhoorn.")
			else:
				if (self.s.ALBehaviorManager.isBehaviorInstalled("pointing/tablet")):
					self.s.ALBehaviorManager.startBehavior("pointing/tablet")
				self.s.ALAnimatedSpeech.say("Klik maar met je vinger op de \\pau=500\\ eenhoorn.")
				self.s.ALMemory.raiseEvent("activate_images", True)
			self._ra_thread = Thread(target=self.request_answer_val, args=(self.unicorn, True))

		else:
			if not self.isLastAnswerWrong:
				if not self.isTestRun and self.round_number == 2:
					self.s.ALTextToSpeech.say("Laten we naar het volgende dier gaan. \\pau=250\\")
				if 2 < self.round_number < 6:
					self.s.ALTextToSpeech.say("Hier komt het volgende dier. \\pau=250\\")
				if 5 < self.round_number < 9:
					self.s.ALTextToSpeech.say("Daar gaan we weer! \\pau=250\\")

				if self.isTestRun:
					self.s.ALMemory.raiseEvent("show_images", False)
					self.s.ALAnimatedSpeech.say("ik zie, ik zie wat jij niet ziet $toggle_facetracking=False en het is een \\pau=500\\."
												+ self.unicorn['SoundSetName'] + ". $toggle_facetracking=True")
					self.s.ALMemory.raiseEvent("activate_images", True)
					if (self.s.ALBehaviorManager.isBehaviorInstalled("pointing/tablet")):
						self.s.ALBehaviorManager.startBehavior("pointing/tablet")
					self.s.ALAnimatedSpeech.say("\\pau=300\\ Klik maar met je vinger op de "+ "\\pau=500\\ "
												+ self.unicorn['SoundSetName'] + ".")

					# self.s.ALMemory.raiseEvent("activate_images", True)
					self._ra_thread = Thread(target=self.request_answer_val, args=(self.unicorn, False))
					self._ra_thread.start()
					return
				elif self.target_words[word]["type"] == "noun":
					if self.word_set:
						# verba = self.verbalize_actions[_data["action"]]
						# random.shuffle(verba)
						if word in self.skills_seen:
							_str = self.verbalize_actions[_data["action"]][self.verbalize_index[_data["action"]]]
							self.verbalize_index[_data["action"]] += 1
							if len(self.verbalize_actions[_data["action"]]) == self.verbalize_index[_data["action"]]:
								self.verbalize_index[_data["action"]] = 0
							self.s.ALAnimatedSpeech.say(_str)
						elif len(self.skills_seen) > 0:
							_str = self.verbalize_actions["word_first_time"][self.verbalize_index["word_first_time"]]
							self.verbalize_index["word_first_time"] += 1
							if len(self.verbalize_actions["word_first_time"]) == self.verbalize_index["word_first_time"]:
								self.verbalize_index["word_first_time"] = 0
							self.s.ALAnimatedSpeech.say(_str)
						if word not in self.skills_seen:
							self.skills_seen.append(word)
					self.s.ALMemory.raiseEvent("show_images", False)
					self.s.ALAnimatedSpeech.say("ik zie, ik zie wat jij niet ziet $toggle_facetracking=False en het is "
												+ self.target_words[word]['UnArticle'] + " \\pau=500\\."
												+ self.target_words[word]['SoundSetName'] + " $toggle_facetracking=True")
						# self.s.ALMemory.raiseEvent("activate_images", True)
			else:
				self.s.ALMemory.raiseEvent("show_images", False)

				if self.isTestRun:
					if (self.s.ALBehaviorManager.isBehaviorInstalled("pointing/tablet")):
						self.s.ALBehaviorManager.startBehavior("pointing/tablet")
					self.s.ALAnimatedSpeech.say("$toggle_facetracking=False Klik maar op de " + " \\pau=500\\ "
												+ self.unicorn['SoundSetName'] + " $toggle_facetracking=True")
					self.s.ALMemory.raiseEvent("activate_images", True)
					self._ra_thread = Thread(target=self.request_answer_val, args=(self.unicorn, False))
					self._ra_thread.start()
					return
				else:
					if self.target_words[word]["type"] == "noun":
						if (self.s.ALBehaviorManager.isBehaviorInstalled("pointing/tablet")):
							self.s.ALBehaviorManager.startBehavior("pointing/tablet")
						self.s.ALAnimatedSpeech.say("Klik maar op " + self.target_words[word]['Article'] + " \\pau=500\\ "
													+ self.target_words[word]['SoundSetName'])
			self.s.ALMemory.raiseEvent("activate_images", True)
			self._ra_thread = Thread(target=self.request_answer_val, args=(self.target_words[word], False))
		self._ra_thread.start()
		if self.paused:
			return

	def happy_eyes(self):
		Thread(target=self.s.ALLeds.rasta, args=(2,)).start()

	def request_answer_val(self, data, test):
		timeout = 7000

		while not self._val_arrived:
			# prepare timeout timer
			start_time = time.time()
			# wait for timeout or vad event
			while (time.time() - start_time) * 1000 < timeout:
				# reset timeout timer if the current task is REPEATED to get an answer, so that
				# the child get the same amount of time to answer again (interrupt also possible)
				if self._request_answer:
					# reset timer
					start_time = time.time()

				# hsa some voice been detected?
				if self._val_arrived:
					# break timeout look
					break

				# wait 500ms until check again
				time.sleep(0.5)

			# if still not valid --> no answer was detected --> request a response from child
			if not self._val_arrived:
				self._request_answer = True
				# word_str = "^runSound(" + data['SoundSetName'] + ")"
				word_str = data['SoundSetName']
				if test:
					word_str = "Eenhoorn"
				elif self.isLastAnswerWrong:
					word_str = data['Dutch']
				if data["type"] == "noun":
					self.s.ALAnimatedSpeech.say("$toggle_facetracking=True" + self._child_name + " Kan je de "+"  \\pau=300\\ " + word_str + " aanraken? $toggle_facetracking=False")
				else:
					self.s.ALAnimatedSpeech.say(self._child_name + "Druk maar op de \\pau=300\\ " + word_str + "")

				self._request_answer = False
		self._val_arrived = False

	def test_run_event(self, key, value):
		if value:
			self.isTestRun = True
			# practice_0 = ["Du hast das Spiel also gut verstanden!",
			#               "Lass uns das einmal ausprobieren."]

			# practice_0 = ["Dann lass uns das einmal ausprobieren.",]
			#
			# for line in practice_0:
			#     print line
			#     self.s.ALTextToSpeech.say(line)

			self.s.ALMemory.raiseEvent("describe_object", "")

		else:
			self.isTestRun = False
			self.s.ALMemory.raiseEvent("hide_images", "")
			self.s.ALMemory.raiseEvent("round_nr", self.round_number)
			test_done = ["$toggle_facetracking=True Ok.Ik denk dat je nu het echte spel kan spelen.",
						 "Klik maar op het groene hoofdje om te beginnen."]
			if (self.s.ALBehaviorManager.isBehaviorInstalled("pointing/tablet")):
				self.s.ALBehaviorManager.startBehavior("pointing/tablet")

			for line in test_done:
				print line
				self.s.ALAnimatedSpeech.say(line)

			self.s.ALMemory.raiseEvent("show_start_button", "")

	def repeat_answer_event(self, key, value):
		self.logger.info("repeat_answer_event")

	def look_at_event(self, key, value):
		self.logger.info("look_at_event")

	def round_number_update_event(self, key, value):
		self.logger.info("round_number_update_event")
		print "--- round number update event " + str(value)

	def gui_buttons_event(self, key, value):
		self.logger.info("gui_buttons_event")

	def _check_vad(self, target_word, intro=False, no_request_answer=False, timeout=5000):
		"""
			This function is listening for voice activity until a timeout happened and then actively requests an answer.

			:param target_word: The word to be pronounced by the child.

			:return: if VAD: True
					   else: False
		"""
		#timeout = 5000

		# reset valid variable --> valid if voice has been detected
		valid = False
		answer = False
		feedback_data = None

		# accept information form VAD service
		self.conn_man.acceptVAD = True

		print "Start answer detection"
		while not valid:
			# prepare timeout timer
			start_time = time.time()
			# wait for timeout or vad event
			while (time.time() - start_time) * 1000 < timeout:
				# if self.paused or self._exit_interaction:
				#     self.conn_man.acceptVAD = False
				#     self._vad_detected = False
				#     self._vad_correct = False
				#     return None
				# reset timeout timer if the current task is REPEATED to get an answer, so that
				# the child get the same amount of time to answer again (interrupt also possible)
				if self._request_answer or no_request_answer:
					# reset timer
					start_time = time.time()

				# has some voice been detected?
				if self._vad_detected:
					print "Voice detected!"

					# child said at least something
					answer = True
					# task is valid or not
					valid = self._vad_correct
					# interrupt the outputmanager (e.g. when currently the task is repeated)
					self._vad_detected = self._vad_correct = False
					self.conn_man.acceptVAD = not valid

					add_info = {"target_word": target_word}
					feedback_data = {"valid": valid, "answer": answer, "type": "VOICE_ACTIVATION_CRITERIUM",
									 "ADD_INFO": add_info}

					# break timeout loop
					break

				# wait 100ms until check again
				time.sleep(0.1)

			# if still not valid --> no answer was detected --> request a response from child
			if not answer:
				print "Request an answer."
				# self.conn_man.acceptVAD = False
				# request answer from child
				data = {"type": "VOICE_ACTIVATION_CRITERIUM", "word": target_word}
				self.request_answer(data, intro)
			else:
				break
			self.conn_man.acceptVAD = True

		# don't listen anymore
		self.conn_man.acceptVAD = False
		print "finished answer detection"
		return feedback_data

	def _check_vad_2(self, target_word):
		# reset valid variable --> valid if voice has been detected
		valid = False
		timeout = 7000

		# accept information form VAD service
		self.conn_man.acceptVAD = True

		while not valid:
			# prepare timeout timer
			start_time = time.time()
			# wait for timeout or vad event
			while (time.time() - start_time) * 1000 < timeout:
				# reset timeout timer if the current task is REPEATED to get an answer, so that
				# the child get the same amount of time to answer again (interrupt also possible)
				if self._request_answer:
					# reset timer
					start_time = time.time()

				# hsa some voice been detected?
				if self._vad_detected:
					# task is valid
					valid = True
					# interrupt the output manager (e.g. when currently the task is repeated)
					# self.s.ALTextToSpeech.stopAll()
					# self.s.ALBehaviorManager.stopAllBehaviors()
					# don't accept further information from VAD service
					self.conn_man.acceptVAD = False
					# reset variable for the next time
					self._vad_detected = False

					# break timeout look
					break

				# wait 500ms until check again
				time.sleep(0.5)

			# if still not valid --> no answer was detected --> request a response from child
			if not valid:
				self.conn_man.acceptVAD = False
				# request answer from child
				data = {"type": "VOICE_ACTIVATION_CRITERIUM", "word": target_word}
				# thread.start_new_thread(self.request_answer, (data,))
				self.request_answer(data)
				self.conn_man.acceptVAD = True
		# don't listen anymore
		self.conn_man.acceptVAD = False

		result = {"valid": valid, "answer": valid, "type": "VOICE_ACTIVATION_CRITERIUM", "ADD_INFO": ""}
		return result

	def request_answer(self, data, intro):
		text = {"child_name": "Hoe heet jij?", "child_age": ", Hoe oud ben je dan?",
				"english_words_known": ", Ken je ook engelse woorden?", "words_known": ",Welke woorden ken je dan?",
				"like_circus": " Vind je ook het circus zo leuk?", "child_prepared": ", ben je er klaar voor?",
				"child_go_on": ", wil je doorgaan?", "next_animal": ", om het volgende dier te zien moet je op de groene pijn klikken.",
				"post_test_ready": ", heb je dat begrepen?", "reengage_continue": ", möchtest du noch weiter spielen?",
				"understand_game_intro": ", snap je dat?"}
		self._request_answer = True
		if intro and "child_name" in data["word"]:
			self.s.ALAnimatedSpeech.say(text[data["word"]])
		elif intro and data["word"] not in text:
			self.s.ALAnimatedSpeech.say("$toggle_facetracking=True %s,Kan je %s %s een druif geven? $toggle_facetracking=False" % (self._child_name, self.target_words[data['word']]['Article'], self.target_words[data['word']]['SoundSetName']))
		elif intro:
			self.s.ALAnimatedSpeech.say(self._child_name + text[data["word"]])
		else:
			self.s.ALAnimatedSpeech.say(self._child_name + ", kan je ook \\pau=300\\ " + self.target_words[data['word']]['SoundSetName'] + " \\pau=200\\ zeggen?")
		self._request_answer = False

	def next_word(self):
		if not self.isTestRun:
			if self._word_first_time:
				pass
			self.round_number = self.round_number + 1
			if self.round_number <= self.num_rounds:
				self.s.ALMemory.raiseEvent("round_nr", self.round_number)        
		if self._finished[0]:
			print("myservice, self._finished[0]:", self._finished[0], " and [1]:", self._finished[1])
			if self._finished[1]:
				pass
				# time.sleep(2)
				# self.s.ALTextToSpeech.say("Puh. Das ist aber anstrengend und ich bin schon richtig kaputt. "
				#                           "Ich glaube ich muss mich etwas ausruhen. Lass uns ein andermal weiterspielen.")
				# self.s.ALTextToSpeech.stopAll()
				# self.s.ALBehaviorManager.stopAllBehaviors()
				# self.s.ALMotion.rest()
				# self.s.ALMemory.raiseEvent("hide_images", "")
			else:
				# self.s.ALMemory.raiseEvent("confetti", "")
				self.s.ALAnimatedSpeech.say("$toggle_facetracking=True Ik vond dat je het heel goed deed en we kunnen stoppen voor vandaag! Ik vond het erg leuk om met jou te spelen")
				self.s.ALMemory.raiseEvent("logEnd", "systen_decision_good")
				# diff = datetime.datetime.now() - self.intro_start
				# self.s.ALMemory.raiseEvent("log", "[total_experiment_time_ms]" + str(int(diff.total_seconds() * 1000)))
				self.post_test = True
				# self.s.ALMemory.raiseEvent("experiment_done", "")
				# self.stop()        
		elif self.round_number <= self.num_rounds:
			if self.paused:
				return
			# print "check chunk_changed: %s" % self._chunk_changed
			# if self._chunk_changed:
			#     self.s.ALTextToSpeech.say("Ich glaube die Tiernamen kannst du nun schon ganz gut!")
			#     self.s.ALTextToSpeech.say("Lass uns das nun einmal mit den Farben der Tiere ausprobieren!")
			#     self._chunk_changed = False
			# elif self._recap:
			#     self.s.ALAnimatedSpeech.say("^start(gaze/child) Super! Du bist richtig gut! Lass uns aber noch"
			#                               " ein paar Wörter wiederholen bevor wir für heute schluss machen!")
			#     self._recap = False
			self.s.ALMemory.raiseEvent("hide_images", "")
			self.s.ALMemory.raiseEvent("describe_object", "")
		else:
			# POST TEST
			# self.s.ALMemory.raiseEvent("confetti", "")
			self.s.ALAnimatedSpeech.say("$toggle_facetracking=True Dat was het!")
			# diff = datetime.datetime.now() - self.intro_start
			# self.s.ALMemory.raiseEvent("log", "[total_experiment_time_ms]" + str(int(diff.total_seconds() * 1000)))
			self.post_test = True

	def choose_preferred_feedback(self, result):
		print ( "child name = "+ self._child_name)
		_replace = " je klikte op de  " +self.target_words[result['answer']]["Article"] +" "+ self.target_words[result['answer']]["Dutch"] + " "
		print("track_Feedback counter = " + str( self.track_feedback[result['answer']]))
		if len(self.track_feedback[result['answer']]) <1:
			print (str(self.target_words[result['answer']]["Dutch"])+ "s feedback is empty") 
			self.track_feedback[result['answer']].append( 0)

		elif self.track_feedback[result['answer']][-1] == 1:
			_replace = ''
		del self.track_feedback[result['answer']][-1]
		self.logger.info("provided_feedback: " + _replace)                       


		if result['is_correct'] == "True":
			self.happy_eyes()
			try:
				self.s.ALBehaviorManager.startBehavior("nod")
			except:
				pass			
			sentence = self.pos_feedback_picker() + _replace
			self.s.ALAnimatedSpeech.say("$toggle_facetracking=True " + sentence)
			self.s.ALMemory.raiseEvent("log", "[provided feedback]: " + sentence)

		else:
			sentence = "$toggle_facetracking=True " + self.feedback_picker('incorrect')
			sentence = sentence.replace("[explanation]",_replace )
			self.s.ALMemory.raiseEvent("log","[provided feedback]: " + sentence)

			self.s.ALAnimatedSpeech.say(sentence)

			if self.paused:
				return
			self.s.ALMemory.raiseEvent("explain_skill", "")    


	def show_validation_event(self, key, value):
		# if not self.post_test:
		self._val_arrived = True
		self._ra_thread.join()
		self.tts_set_language("Dutch")

		self.logger.info("show_validation_event " + key + " " + value)

		result = json.loads(value)

		if result['is_correct'] == 'True':
			self.isLastAnswerWrong = False
			if self.isFirstTestRun or self.isTestRun:
				self.s.ALAnimatedSpeech.say("Het engelse woord voor " + self.unicorn['Dutch']
											+ " is \\pau=500\\ " + self.unicorn['SoundSetName'])                
			if self.isTestRun and not self.isFirstTestRun:
				self.isTestRun = False
				self.s.ALMemory.raiseEvent("test_run", False)
				return  # Don't start the next assignment yet, start button first..

			if self.isFirstTestRun:
				practice_1 = ["Deze was wel makkelijk omdat ik het nederlandse woord gebruikte!",
							  "Laat ons het nog een keertje proberen!",
							  "Maar ik ga het nu wat moeilijker maken.",
							  "Ik ga nu het engelse woord voor het dierr gebruiken!",
							  "Laten we het proberen!"]

				for line in practice_1:
					print line
					self.s.ALTextToSpeech.say(line)
				self.isFirstTestRun = False  

			elif strategy == "preferred":
				self.choose_preferred_feedback(result)
			elif strategy == "dispreferred":
				self.s.ALAnimatedSpeech.say("$toggle_facetracking=True " + "goedzo")
	  

			self.next_word()
		else: 
			if strategy == "preferred":
				self.isLastAnswerWrong = True
				if self.isFirstTestRun or self.isTestRun:  # self.isDutchIntro:
					self.s.ALAnimatedSpeech.say("$toggle_facetracking=True dat is " + self.target_words[result['answer']]["UnArticle"] + " "
												+ self.target_words[result['answer']]['Dutch']
												+ ", maar ik bedoelde een \\pau=500\\, "
												+ self.unicorn['Dutch'] + " \\pau=300\\")
					self.s.ALMemory.raiseEvent("explain_skill", "")
				else: 
					self.choose_preferred_feedback(result)
   
			else:  #feedback == dispreferred or no               
				if strategy == "dispreferred":
					self.s.ALAnimatedSpeech.say("Helaas, dat is niet goed")
				self.next_word()
		time.sleep(1)




	def start(self):
		self.tts_set_language("Dutch")
		self.s.ALMemory.raiseEvent("log", "testText")

		while not self.running:
			time.sleep(0.1)
		print self._child_name
		self.logger.info("ppnr: " + str(self._child_name) )
		self.s.ALMemory.raiseEvent("log", "[child name, ppnr and robot's name]: " + self._child_name)        		

		if ';' in self._child_name:               	
			self.childNamePpnrRobotName = self._child_name.split(';')
			self._child_name = self.childNamePpnrRobotName[0].strip().lower()
			print "child_name:"+ self._child_name
			self.logger.info("ppnr: " + str(self.childNamePpnrRobotName[1].strip().lower())) 
			robot_name = self.childNamePpnrRobotName[2].strip().lower()
			if robot_name == 'luka':
				robot_name = 'loeka'


		else:
			print("---------------------------")
			print("you sure you've added the ppnr number? ")
			print("---------------------------")


		self._intro = True
		# tmp_str = "i" if self.intro else "ni"
		if self.intro:
			self.intro_start = datetime.datetime.now()
			if not is_test:
				self.s.ALAnimatedSpeech.say("$toggle_facetracking=True Hallo ik ben een vriendje van Robin, ik ben "+ robot_name +". Hoe heet jij?")
				self._output_finished = False
				_feedback_data = self._check_vad("child_name", intro=True)

				while self.paused:
					if self._exit_interaction:
						self.stop()
					time.sleep(0.1)

				intro = ["^start(nod) \\pau=300\\ dat is een mooie naam, leuk dat je met mij wil spelen!",
						 "Hoe oud ben jij?"]
				for line in intro:
					print line
					self.s.ALAnimatedSpeech.say(line)

				self._output_finished = False
				_feedback_data = self._check_vad("child_age", intro=True)

				while self.paused:
					if self._exit_interaction:
						self.stop()
					time.sleep(0.1)

				intro = ["^start(nod) \\pau=300\\ Ik ben 6 jaar oud. Dan ben ik ietjes ouder dan jij bent",
						 "Vandaag wil ik met jou engelse woorden leren.",
						 "Ken jij al wat engelse woorden?"]

				for line in intro:
					print line
					self.s.ALAnimatedSpeech.say(line)

				self._output_finished = False
				_feedback_data = self._check_vad("english_words_known", intro=True)

				if _feedback_data["valid"]:
					self.s.ALAnimatedSpeech.say("^start(nod) \\pau=300\\ Goed! Wellicht leer je wel een paar nieuwe!")
				else:
					self.s.ALAnimatedSpeech.say("^start(nod) \\pau=300\\ Goed, dan ga je er vandaag een aantal leren.")

				while self.paused:
					if self._exit_interaction:
						self.stop()
					time.sleep(0.1)

			self.s.ALMemory.raiseEvent("show_screen", "")

			if not is_test:
				self.s.ALAnimatedSpeech.say("$toggle_facetracking=False Zie je het circus op het scherm voor je? Oh ik houd van het circus, $toggle_facetracking=True jij ook?")
				self._output_finished = False
				_feedback_data = self._check_vad("like_circus", intro=True)
				if _feedback_data["valid"]:
					self.happy_eyes()
					self.s.ALAnimatedSpeech.say("^start(nod) \\pau=300\\ Fijn!, dan gaan we iets leuks doen!")
				else:
					self.s.ALAnimatedSpeech.say("^start(nod) \\pau=300\\ Ohh, naja gelukkig is het een spelletje.")

				while self.paused:
					if self._exit_interaction:
						self.stop()
					time.sleep(0.1)

				intro = ["Vandaag gaan we naar dieren kijken.",
						 "Ik zal je dieren laten zien en vertellen hoe ze in het Engels heten.",
						 "Wil je het eerste dier zien?"]

				for line in intro:
					print line
					self.s.ALTextToSpeech.say(line)

			# introduce animals
			first_animal = True
			if not is_test :
				animals = self.target_words.keys()
				print("--------------------")
				print("animals" , animals)
				random.shuffle(animals)
			else:
				animals = []
			self.s.ALMemory.raiseEvent("show_screen", "spotlight")
			for _animal in animals:
				while self.paused:
					if self._exit_interaction:
						self.stop()
					time.sleep(0.1)

				# introduce a new animal with img + name + text + gesture
				c_word = self.target_words[_animal]
				if first_animal:
					self._output_finished = False
					_feedback_data = self._check_vad("child_prepared", intro=True)
					self.s.ALMemory.raiseEvent("show_animal_intro", c_word["English"])
					if _feedback_data["valid"]:
						self.s.ALAnimatedSpeech.say("^start(nod) \\pau=300\\ Klasse $toggle_facetracking=False hier komt het eerste dier.")
					else:
						self.s.ALAnimatedSpeech.say("^start(nod) \\pau=300\\ $toggle_facetracking=False Kijk er is een dier op het scherm. $toggle_facetracking=True Ik kan je vertellen hoe dat dier in het engels heet. Maar alleen als je het wilt")
						self._output_finished = False
						_feedback_data = self._check_vad("child_go_on", intro=True)
						if not _feedback_data["valid"]:
							self.s.ALAnimatedSpeech.say("^start(nod) \\pau=300\\ Geen probleem, ik was blij om je eventjes te zien.")
							return
				else:
					self.s.ALMemory.raiseEvent("show_animal_intro", c_word["English"])
				#self.s.ALBehaviorManager.runBehavior(c_word['Behavior'])
				self.tts_set_language("Dutch")
				self.s.ALAnimatedSpeech.say("$toggle_facetracking=True %s \\pau=100\\ is in het Engels \\pau=500\\ %s"
											% (c_word['Dutch'], c_word['SoundSetName']))

				speech_intro = ["Zeg mij maar na", "Kan je dit nazeggen"]
				random.shuffle(speech_intro)
				self.s.ALAnimatedSpeech.say("%s \\pau=500\\ %s" % (speech_intro[0], c_word['SoundSetName']))
				self._output_finished = False
				_feedback_data = self._check_vad(_animal)
				if strategy == "preferred":
					self.happy_eyes()
					if first_animal:
						first_animal = False
						self.s.ALAnimatedSpeech.say("^start(nod) \\pau=300\\ " + self.pos_feedback_picker() + " $toggle_facetracking=False Klik maar op de groene pijl om het volgende dier te zien.")
						if (self.s.ALBehaviorManager.isBehaviorInstalled("pointing/tablet")):
							self.s.ALBehaviorManager.startBehavior("pointing/tablet")
					else:
						self.s.ALAnimatedSpeech.say("^start(nod) \\pau=300\\ " + self.pos_feedback_picker() + " $toggle_facetracking=False")
				elif strategy == "dispreferred":
					if first_animal:
						first_animal = False
						self.s.ALAnimatedSpeech.say("^start(nod) \\pau=300\\ " + "goedzo" + " $toggle_facetracking=False Klik maar op de groene pijl om het volgende dier te zien.")
						if (self.s.ALBehaviorManager.isBehaviorInstalled("pointing/tablet")):
							self.s.ALBehaviorManager.startBehavior("pointing/tablet")
					else:
						self.s.ALAnimatedSpeech.say("^start(nod) \\pau=300\\ " + "goedzo" + " $toggle_facetracking=False")
				else:
					if first_animal:
						first_animal = False
						self.s.ALAnimatedSpeech.say("^start(nod) \\pau=300\\ " + " $toggle_facetracking=False Klik maar op de groene pijl om het volgende dier te zien.")
						if (self.s.ALBehaviorManager.isBehaviorInstalled("pointing/tablet")):
							self.s.ALBehaviorManager.startBehavior("pointing/tablet")
					else:
						self.s.ALAnimatedSpeech.say("^start(nod) \\pau=300\\ "  + " $toggle_facetracking=False")

				self.s.ALMemory.raiseEvent("val_animal_intro", "")

				self._output_finished = False
				_feedback_data = self._check_vad("next_animal", intro=True)

				self.s.ALMemory.raiseEvent("val_animal_intro_hide", "")

			self.tts_set_language("Dutch")
			while self.paused:
				if self._exit_interaction:
					self.stop()
				time.sleep(0.1)

			if self.intro:
				self.s.ALMemory.raiseEvent("show_screen", "game")
				self.s.ALAnimatedSpeech.say("So $toggle_facetracking=True dat waren ze allemaal geloof ik!")
				self.goto_crouch_with_breath()
				self.s.ALAnimatedSpeech.say("$toggle_facetracking=True")

				# self.pre_test()
				if not is_test:
					intro = ["Ik heb een idee!",
							 "Mijn lievelingsspel is 'ik zie, ik zie wat jij niet ziet'.",
							 "Laten we op de \prn=t E b l @ t \ spelen!",
							 "Ik zal je plaatjes van dieren laten zien",
							 "Als ik zeg 'ik zie, ik zie wat jij niet ziet en het is een puntje puntje puntje', moet je het aanraken."]
					
				else:
					intro=["test"]
				if self.word_set:
					intro.append(self.verbalize_actions["intro"])
				intro.append("snap je dat?")

				for line in intro:
					print line
					self.s.ALTextToSpeech.say(line)

				self._output_finished = False
				_feedback_data = self._check_vad("understand_game_intro", intro=True)
				if _feedback_data["valid"]:
					self.s.ALMemory.raiseEvent("test_run", "true")
				else:
					self.s.ALAnimatedSpeech.say("^start(nod) \\pau=300\\ Oke geen probleem, dan vertellen we het nog een keertje!")
					self.paused = True

				while self.paused:
					time.sleep(0.1)

			self._intro = False

			self.wait_post_test()
		else:
			self.intro_start = datetime.datetime.now()
			self.post_test = True
			self.s.ALMemory.raiseEvent("show_screen", "game")
			self.wait_post_test()

	def pre_test(self):
		return


	def goto_crouch_with_breath(self):
		self.s.ALRobotPosture.goToPosture("Crouch", 0.5)
		names = ['RKneePitch', 'LKneePitch', 'RAnklePitch', 'LAnklePitch', 'RAnkleRoll', 'LAnkleRoll']
		time.sleep(2)
		self.s.ALMotion.setStiffnesses(names, 0.0)
		self.s.ALMotion.setBreathEnabled("Arms", True)

	def wait_post_test(self):
		while not self.post_test:
			time.sleep(0.1)

		self.s.ALMemory.raiseEvent("start_post_test", True)
		first_animal = True
		counter = 1

		imgs = self.target_words.keys()
		random.shuffle(imgs)
		self.s.ALMemory.raiseEvent("set_images", json.dumps(imgs))
		self.s.ALMemory.raiseEvent("show_images", False)
		self.s.ALMemory.raiseEvent("show_fruits", "0")
		#if self.retention:
		#    # TODO: Change text
		#    self.s.ALTextToSpeech.say("\\pau=100\\ Hallo %s. Schön dich wieder zu sehen. Heute habe ich leider nicht so viel Zeit zum Spielen. Aber wir müssten mal wieder unsere Tiere füttern!" % self._child_name)
		#    self.s.ALTextToSpeech.say("Ich sage dir gleich wieder der Reihe nach die Tiernamen auf Englisch und du schiebst dann eine Traube mit deinem Finger dort hin, ok?")
		#else:
		self.s.ALTextToSpeech.say("\\pau=100\\ Nu moeten we alleen nog alle dieren voeren.Ik vertel je de engelse namen en dan mag jij een druif naar het dier slepen. Snap je dat?")
		self._output_finished = False
		_feedback_data = self._check_vad("post_test_ready", intro=True)
		if _feedback_data["valid"]:
			self.s.ALTextToSpeech.say("Super, laten we beginnen.")
		else:
			self.s.ALTextToSpeech.say("Oh dat lukt jou wel hoor. Laten we het gewoon proberen.")

		animals = self.target_words.keys()
		random.shuffle(animals)
		self.s.ALTextToSpeech.say("Oke hier komt het eerste dier!")
		for _animal in animals:
			if not first_animal:
				feedback_list = ["Okee!", "Laten we verder gaan!", "Als volgende dier:", "Nu komt:"]
				random.shuffle(feedback_list)
				self.s.ALAnimatedSpeech.say(feedback_list[0])

			c_word = self.target_words[_animal]
			self.s.ALMemory.raiseEvent("post_test_target_word", c_word["English"])
			while self.paused:
				if self._exit_interaction:
					self.stop()
				time.sleep(0.1)

			if not first_animal:
				counter += 1
				imgs = self.target_words.keys()
				random.shuffle(imgs)
				self.s.ALMemory.raiseEvent("set_images", json.dumps(imgs))
				self.s.ALMemory.raiseEvent("show_images", False)
				self.s.ALMemory.raiseEvent("show_fruits", str(counter))
			else:
				self.s.ALMemory.raiseEvent("show_fruits", "1")
				first_animal = False

			self.s.ALTextToSpeech.say(c_word['SoundSetName'])
			self.s.ALMemory.raiseEvent("activate_images", "False")
			self._output_finished = False
			_feedback_data = self._check_vad(_animal, intro=True, timeout=10000)
			# while not self.post_result:
			#     time.sleep(0.1)
			self.post_result = False

		self.s.ALMemory.raiseEvent("end_post_test", True)
		self.happy_eyes()
		self.s.ALAnimatedSpeech.say("$toggle_facetracking=True Nu hebben we alle dieren gevoerd")
		self.s.ALMemory.raiseEvent("hide_images", True)
		self.s.ALTextToSpeech.say("Ik vond het heel erg leuk om met jou te spelen. Tot de volgende keer.")
		diff = datetime.datetime.now() - self.intro_start
		self.s.ALMemory.raiseEvent("log", "[total_experiment_time_ms]" + str(int(diff.total_seconds() * 1000)))
		self.s.ALMemory.raiseEvent("experiment_done", "")
		self.stop()

	def _toggle_facetracking_callback(self, value):
		if value == 'True':
			if self.last_known_child_location == None:
				# Moving to default expected child location (first time only)
				self.s.ALMotion.angleInterpolationWithSpeed("Head", [0.704064, 0.0199001], 0.2)
			else:
				# Moving to the last known child location based on previous face tracking
				self.s.ALMotion.angleInterpolationWithSpeed("Head", self.last_known_child_location, 0.2)

			t = Thread(target=self._follow_face)
			t.start()
			self.is_face_tracking = True

		else:       
			try:    
				self.s.ALFaceTracker.stopTracker()
			except:
				pass
			self.is_face_tracking = False
			try: 
                                self.s.ALBehaviorManager.runBehavior('gaze/tablet')

                        except:
                                pass
				   

	def _follow_face(self):
		print "Starting face tracking.."
		try:
			self.s.ALFaceTracker.startTracker()
		except:
			pass

		initial_value = self.s.ALMotion.getAngles("Head", False)

		try:
			while self.s.ALFaceTracker.isActive():
				if self.s.ALFaceTracker.isNewData():                
					loc = self.s.ALMotion.getAngles("Head", False)

					if loc[0] != initial_value[0] and loc[1] != initial_value[1] and (self.last_known_child_location == None or (loc[0] != self.last_known_child_location[0] and loc[1] != self.last_known_child_location[1])):
						self.last_known_child_location = loc

				time.sleep(0.5)
		except:
			pass

		#print "No longer tracking face"

	# [JAN] You could use this method to reset the gaze to its original position, but there is currently no button on the control panel to trigger this...
	def reset_gaze(self):
		logging.debug("Resetting child location for gaze")
		self._toggle_facetracking_callback('False')
		self.last_known_child_location = None
		self._toggle_facetracking_callback('True')        

	@qi.bind(returnType=qi.Void, paramsType=[])
	def stop(self):
		"Stop the service."
		# TODO Proper ending sentence
		self.logger.info("ALMyService stopped by user request.")
		self.qiapp.stop()

	@qi.nobind
	def on_stop(self):
		"Cleanup (add yours if needed)"
		self.logger.info("ALMyService finished.")

####################
# Setup and Run
####################


if __name__ == "__main__":
	argv = sys.argv[1:]
	word_set = ""
	strategy = ""
	try:
	   opts, args = getopt.getopt(argv, "hi:v:", ["qi-url=", "word_set=", "strategy="])
	except getopt.GetoptError:
		print 'start.py -i <robot_ip> -v <1/0>'
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-v", "--word_set"):
			woordenset = arg
		if opt in ("-r", "--strategy"):
			strategy = arg
	sys.argv = sys.argv[:3]
	# sys.argv[2] = "127.0.0.1:61693"
	stk.runner.run_service(ALAnimalExperimentService)
