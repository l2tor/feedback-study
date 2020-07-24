from naoqi import ALBroker, ALProxy


class Robot:
    """
     This is an abstract class for connecting and "speaking" with the robot over its proxies.
    """
    _broker = None
    memoryProxy = None
    motionProxy = None
    robotPostureProxy = None
    animatedTTSProxy = None
    TTSProxy = None
    trackerProxy = None

    @staticmethod
    def connect(ip, port, sysip):
        try:
            Robot._broker = ALBroker("pythonBroker", sysip, 0, ip, port)
            Robot.memoryProxy = ALProxy("ALMemory")
            Robot.motionProxy = ALProxy("ALMotion")
            Robot.robotPostureProxy = ALProxy("ALRobotPosture")
            Robot.animatedTTSProxy = ALProxy("ALAnimatedSpeech")
            Robot.TTSProxy = ALProxy("ALTextToSpeech")
            Robot.trackerProxy = ALProxy("ALTracker")
        except Exception as ex:
            print ex
