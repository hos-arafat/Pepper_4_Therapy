import qi
import argparse
import sys
import time
import os

import threading


def parse_args():
    """
    Parses and returns the command line arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--language", type=str, default="English",
                        help="language")
    parser.add_argument("--speed", type=int, default=100,
                        help="speed")

    return parser.parse_args()

def connect_to_pep(pip, pport):
    """
    Connects to Pepper robot and returns an app that runs the code on the robot
    """

    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        app = qi.Application(["Memory Read", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    return app

def check_event(touch_service):
    """
    Returns 0 or 1 to indicate if Pepper's left or right hands were touched
    """

    arm = -1
    # Get current status of touch sensors
    s = touch_service.getStatus()

    for e in s:
        # Return 0 if Left Arm sensor is touched
        if e[0]=='LArm' and e[1]:
             arm = 0
             print "Left arm touched!"
        
        # Return 1 if Right Arm sensor is touched
        if e[0]=='RArm' and e[1]:
            arm = 1
            print "Right arm touched!"
    return arm




def monitor_fist_bump(memory_service, touch_service, right_count, left_count, ex_num):
    """
    (RUN FOR THE DOCTOR / EXERCISE INSTRUCTOR ONLY.
    FOR THE PURPOSES OF RECORDING INSTRUCTIONAL VIDEO THAT PLAYS ON THE TABLET FOR USERS)

    Checks to see if the exercise instructor "fist-bumped" Pepepr, if so, it moves the joints in the 
    exercise position and starts the exercise countdown timer
    """

    global fist_bump
    global exercise_dict
    my_pos = [0.00, -0.21, 1.00, 0.13, -1.24, -0.52, 1.00, 1.00, -0.14, 1.22, 0.52, -1.00]

    t = threading.currentThread()
    
    print "Thread that while loops is", t.getName()

    while getattr(t, "do_run", True):

        # Check if either hand's tactile sensor was touched
        b = check_event(touch_service)

        if b==0 or b==1:
            print("Fist bumped!")
            fist_bump = True
            t.do_run = False  
            time.sleep(1)        

            # Unsubscribe from ASR as it is not needed right now
            asr_service.unsubscribe("Test_ASR")
            asr_on = False
        
            # Move joints to exercise configuration by calling the "move" function on its own thread
            exercise_thread = threading.Thread(name = "move_to_ex_1", target = move, args = (session, my_pos))
            exercise_thread.daemon = True
            exercise_thread.start()
            
            time.sleep(2)
            
            # Say string by calling "my_say" function on its own thread
            start_timer1_str = "^mode(disabled) Okay ! Starting timer"  
            say_st_time1_thread = threading.Thread(name = "say_timer_1", target = my_say, args = (app, start_timer1_str, language, speed))
            say_st_time1_thread.daemon = True
            say_st_time1_thread.start()
            say_st_time1_thread.do_run = False

            # Display 10 second countdown video on tablet by calling "vid_disp" function on its own thread
            timer1_display_timer_thread = threading.Thread(name = "diplay_ex_1_timer", target = vid_disp, args=(exercise_dict["timer"]["url"],))
            timer1_display_timer_thread.daemon = True        
            timer1_display_timer_thread.start()
            
            # Start the execution monitoring for exercise sequence by calling "run_exercise" function on its own thread
            monitorThread = threading.Thread(name = "monitor_hands_ex1", target = run_exercise, args = (memory_service, touch_service, right_count, left_count, ex_num))
            monitorThread.daemon = True
            monitorThread.start()


def get_doc(memory_service, touch_service, right_count, left_count, ex_num):
    """
    After asking the user if they need their doctor,
    This function checks to see if the user touched any of Peppers hands 
    to indicate that they do need their doctor
    """

    global exercise_dict
    global user_name

    t = threading.currentThread()
    
    print "Thread that while loops is", t.getName()

    # Initialize Flags that make Pepper say the strings ONLY ONCE inside the while loop
    said_calling = False
    said_done = False

    # While the thread is running, do
    while getattr(t, "do_run", True):

    
        # Check if either hand's tactile sensor was touched
        b = check_event(touch_service)

        if b==0 or b==1:
            
            # If either hand was touched, shut down thread to exit the while loop and update flags
            print("Getting Doctor!")
            t.do_run = False            


            time.sleep(1)
            in_pain = True
            print "value of in pain is", in_pain

            # If Pepper hasn't said the "Calling the doctor" string yet
            if said_calling == False:
                # Say "Calling Doctor" by calling the "my_say" function on its own thread
                doc_str = "^start(animations/Stand/Gestures/CalmDown_6) Calling the doctor now"  
                print doc_str
                doc_say_thread = threading.Thread(name = "say_getting_doc", target = my_say, args = (app, doc_str, language, speed))
                doc_say_thread.daemon = True
                doc_say_thread.start()
                doc_say_thread.do_run = False
    
                said_calling = True

                # Show an image to indicate that you are calling the doctor by calling "vid_disp" on its own thread
                video_display_dial_thread = threading.Thread(name = "diplay_dialing_video", target = vid_disp, args=(exercise_dict["dial"]["url"],))
                video_display_dial_thread.daemon = True        
                video_display_dial_thread.start()
                video_display_dial_thread.do_run = False   

                time.sleep(4)


            # If Pepper hasn't said the "Called the doctor" string yet
            if said_done == False:

                # Say the string by calling the "my_say" function on its own thread
                called_doc_str =  "^start(animations/Stand/Gestures/CalmDown_6) Done. Just relax. Doctor should be here shortly."
                print called_doc_str
                say_called_doc_thread = threading.Thread(name = "say_cald_doc", target = my_say, args = (app, called_doc_str, language, speed))
                say_called_doc_thread.start()
                say_called_doc_thread.do_run = False   

                # Update the flag
                said_done = True

                # Show an image to indicate that you are DONE calling the doctor by calling "vid_disp" on its own thread
                video_display_done_thread = threading.Thread(name = "diplay_done_video", target = vid_disp, args=(exercise_dict["done"]["url"],))
                video_display_done_thread.daemon = True
                time.sleep(2)
                video_display_done_thread.do_run = False           

            # UNsubscribe from ASR service and shut down the app / code running on Pepper
            asr_service.unsubscribe("Test_ASR")
            asr_on = False
            app.stop()            
            app.stop()


def run_exercise (memory_service, touch_service, right_count, left_count, ex_num):
    """
    Runs the first and second exercise; namely, it moves Pepper's joints in the exercise configuration,
    starts the countdown timer for the duration of the exercise and monitors execution.

    Also responsible for the speech after each exercise, as follows:
    - After the first exercise
        Pepper asks the user if they are physically okay to continue onwards to the second exercise
        
    - After the second exercise
        Pepper commends the user for finishing both exercises
    """

    global exercise_dict
    global user_name

    rhMemoryDataValue = "Device/SubDeviceList/RHand/Touch/Back/Sensor/Value"
    lhMemoryDataValue = "Device/SubDeviceList/LHand/Touch/Back/Sensor/Value"

    t = threading.currentThread()
    default_pos = [0.00, -0.21, 1.55, 0.13, -1.24, -0.52, 0.01, 1.56, -0.14, 1.22, 0.52, -0.01]

    # Get current time
    start_time = time.time()
    
    print "Thread that while loops is", t.getName()

    # Initialize Flags that make Pepper say the strings ONLY ONCE inside the while loop
    said_gj = False
    said_keepup = False


    while getattr(t, "do_run", True):

        # Check if either hand's tactile sensor was touched
        b = check_event(touch_service)

        # If the tactile sensor on the LEFT hand was touched
        if b==0:      
            # Increment counter that keeps track of exercise execution and print value for debugging 
            left_count +=1
            print "Left Hand value thread=", memory_service.getData(lhMemoryDataValue)

            # Say the number of times user touched the LEFT sensor so far (count) by calling "my_say" on its own threads
            strsay = "^mode(disabled)" + str(left_count) + "^mode(disabled) Left"
            print strsay
            sayThread = threading.Thread(name = "say_L_hand_touched", target = my_say, args = (app, strsay, language, speed))
            sayThread.daemon = True
            sayThread.start()
            time.sleep(1)

        # If the tactile sensor on the RIGHT hand was touched
        elif b==1:
            # Increment counter that keeps track of exercise execution and print value for debugging
            print "Right Hand value thread=", memory_service.getData(rhMemoryDataValue)
            right_count +=1 

            # Say the number of times user touched the RIGHT sensor so far (count) by calling "my_say" on its own threads
            strsay = "^mode(disabled)" + str(right_count) + "^mode(disabled) Right" 
            print strsay
            say2Thread = threading.Thread(name = "say_R_hand_touched", target = my_say, args = (app, strsay, language, speed))
            say2Thread.daemon = True
            say2Thread.start()
            time.sleep(1)
        
        # Get elapsed time since the start of the exercise
        elapsed_time =  time.time() - start_time

        # If 5 seconds have passed since the exercise began
        if elapsed_time >= 5 and said_keepup == False:   
            
            # Motivate the user and say "Keep going" by calling the "my_say" function on its own thread
            keepup_str =  "^mode(disabled) Keep going, almost there ! "
            print keepup_str
            say_keepup_thread = threading.Thread(name = "say_keepup", target = my_say, args = (app, keepup_str, language, speed))
            say_keepup_thread.start()
            say_keepup_thread.do_run = False
            # Update the flag to reflect that Pepper already said the string
            said_keepup = True

        # If around 10 ~ 12 seconds have passed
        elif elapsed_time >= 12:     
   
            # The 10 seconds of exercise are done
            print "Exercise time is done"

            # Say exercise is done by calling the "my_say" function on its own thread
            end_timer2_str = "^start(animations/Stand/Gestures/Far_2) Time's up! ^wait(animations/Stand/Gestures/Far_2) Well done %s !" %user_name  
            say_e_time2_thread = threading.Thread(name = "say_time_up", target = my_say, args = (app, end_timer2_str, language, speed))
            say_e_time2_thread.daemon = True
            say_e_time2_thread.start()
            say_e_time2_thread.do_run = False

            # Wait for 2 seconds until Pepper finsihes saying the above string
            time.sleep(2)

            # Move joints to exercise configuration by calling the "move" function on its own thread
            move_thread = threading.Thread(name = "move_to_def", target = move, args = (session, default_pos))
            move_thread.start()
            time.sleep(1)
            move_thread.do_run = False
            time.sleep(1)

            # Shut down thread to exit the while loop
            t.do_run = False
            

    # Prompt for debugging purposes   
    print "Exited the while loop of the Thread"

    # If we just finished the first exercise
    if ex_num == 1:
        # Update global flag
        exercise_dict["first"]["isDone"] = True
        print "First exercise just finished", exercise_dict["first"]["isDone"]

        # Ask if user is okay to continue onwards to the second exercise by calling "my_say" function on its own thread
        ask_second_str = "^start(animations/Stand/Gestures/Think_1) Let's keep going ? ^wait(animations/Stand/Gestures/Think_1)"
        print ask_second_str
        ask_ready42_thread = threading.Thread(name = "ask_2nd_ex", target = my_say, args = (app, ask_second_str, language, speed))
        ask_ready42_thread.daemon = True
        ask_ready42_thread.start()
        ask_ready42_thread.dorun = False

        asr_service.subscribe("Test_ASR")
        asr_on = True

    # If we just finished the second exercise
    elif ex_num == 2:
        # Update global flag
        exercise_dict["second"]["isDone"] = True
        
        # Commend the user on doing a good job by calling "my_say" function on its own thread
        all_done_str = "^start(animations/Stand/Gestures/Happy_4) That was a great session! Great job! ^wait(animations/Stand/Gestures/Happy_4) See you in our next scheduled appointment. Have a great day!"
        print all_done_str
        all_done_thread = threading.Thread(name = "say_all_done_gj", target = my_say, args = (app, all_done_str, language, speed))
        all_done_thread.daemon = True
        all_done_thread.start()
        time.sleep(4)
        all_done_thread.dorun = False
        
        # After both exercise are done, shut down the app
        app.stop()

    

    return


def my_say(app, strsay, language, speed):
    """
    Makes Pepper say / utter a text with a given speed and "Animated Speech" configuration
    """

    app.start()
    session = app.session

    # Get the service ALAnimatedSpeech.
    asr_service = session.service("ALAnimatedSpeech")

    # set the local configuration
    configuration = {"bodyLanguageMode":"contextual"}

    # say the text with the local configuration
    asr_service.say(strsay, configuration)

    # Get the service ALTextToSpeech and set the speaking volume
    tts_service = session.service("ALTextToSpeech")
    tts_service.setVolume(0.8)    
    
    # Print the uttered string for debugging purposes
    print "  -- Say: " + strsay

    return

def move(session, pos):
    """
    Moves Pepper's shoulders, arms, and hands joints to either the "default" or the "exercise" configurations
    """

    # List of Pepper's joints we are want to move
    jointsNames = ["HeadYaw", "HeadPitch",
               "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw",
               "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]


    # If we passed an invalid configuration to this function, exit and raise error
    if (pos==None):
        print 'No joint values.'
        sys.exit(0)

    print "Set joint values: ", pos
    isAbsolute = True

    # Get Motion service 
    motion_service  = session.service("ALMotion")

    # Set the stiffness of the joints 
    names = ["Head", "LArm", "RArm"]
    stiffnessLists = 0.8
    timeLists = 1.0
    motion_service.stiffnessInterpolation(names, stiffnessLists, timeLists)        
    
    # Print the position we are about to move to for debugging
    if pos == [0.00, -0.21, 1.00, 0.13, -1.24, -0.52, 1.00, 1.00, -0.14, 1.22, 0.52, -1.00]:
        print "moving to my pos"
    elif pos == [0.00, -0.21, 1.55, 0.13, -1.24, -0.52, 0.01, 1.56, -0.14, 1.22, 0.52, -0.01]:
        print "moving to default pos"

    # Move the joints
    motion_service.angleInterpolation(jointsNames, pos, 1.0, isAbsolute)

    return

def onNameRecognized(value):
    """
    Callback function that runs whenever the Automatic Speech Recognition (ASR) module 
    detects that the user said their name (in this case, the name "Luca")

    The fucntion makes Pepper greet the user and ask them if they are ready to start the entire session
    """

    # Print string detected by ASR for debugging
    print "value on NAME recog=",value
    
    # Global flags
    global greeting_done
    global first_exercise_done
    
    global idNameRecognized

    global user_name

    # If ASR detects "YES" and we are yet to greet the user
    if  greeting_done == False and value[0] != "yes" and value[0] != "pain" and value [0] != "no" and value [0] != "rest" and value[1] > 0.45:
        # Say "Hello USER" by calling "my_say" on its dedicated thread
        user_name = value[0]
        intro_str = "Hello, %s" %user_name
        print intro_str
        intro_say_thread = threading.Thread(name = "say_hello_user", target = my_say, args = (app, intro_str, language, speed))
        intro_say_thread.start()
        intro_say_thread.do_run = False

        # Update global flag to reflect that we already did the greeting
        greeting_done = True

        time.sleep(1)

        # Disconnect this callback function so that it is not called whenever the ASR detects "Yes/No"
        nameRecognized.signal.disconnect(idNameRecognized)

        # Ask the user if they are ready to start by calling "my_say" on its dedicated thread
        start_str = "^start(animations/Stand/Gestures/Think_1) Are you ready to start our session ?"  
        print start_str
        start_say_thread = threading.Thread(name = "say_r_u_ready", target = my_say, args = (app, start_str, language, speed))
        start_say_thread.daemon = True
        start_say_thread.start()
        start_say_thread.do_run = False


def onPainRecognized(value):
    """
    Callback function that runs whenever the Automatic Speech Recognition (ASR) module 
    detects that the user said "Yes" or "No" to indicate that they need their doctor

    - If the user says "Yes":
        The fucntion makes Pepper say that she is calling the doctor, comforts the user to relax as
        their doctor will be here soon
    
    - If the user says "No":
        The fucntion makes Pepper tell the user they should take a long rest, Pepper then
        displays 30 second timer on the tablet and come back when they are feeling back to full fitness 
    """
    
    # Print string detected by ASR for debugging
    print "value in PAIN Recog=",value

    # Global flags
    global greeting_done
    global in_pain
    global ask_pain
    global asr_on
    global exercise_dict

    global not_ready

    # Joint poistions that will make Pepper's hands closer to the user to touch
    my_pos = [0.00, -0.21, 1.00, 0.13, -1.24, -0.52, 1.00, 1.00, -0.14, 1.22, 0.52, -1.00]

    # If ASR detects "YES" and greeting, first exercise are done and we already aksed if the user needs the doctor
    if greeting_done == True and value[0] == "yes" and value[1] >= 0.42:
        if exercise_dict["first"]["isDone"] == True and exercise_dict["second"]["isDone"] == False and ask_pain == True and not_ready == False:    
            # Update flag and print its value for debugging
            in_pain = True
            print "value of in pain is", in_pain

            # Say "Calling Doctor" by calling the "my_say" function on its own thread
            doc_str = "^start(animations/Stand/Gestures/CalmDown_6) Okay, calling the doctor now."  
            print doc_str
            doc_say_thread = threading.Thread(name = "say_getting_doc", target = my_say, args = (app, doc_str, language, speed))
            doc_say_thread.daemon = True
            doc_say_thread.start()
            doc_say_thread.do_run = False

            # Show an image to indicate that you are calling the doctor by calling "vid_disp" on its own thread
            video_display_dial_thread = threading.Thread(name = "diplay_dialing_video", target = vid_disp, args=(exercise_dict["dial"]["url"],))
            video_display_dial_thread.daemon = True        
            video_display_dial_thread.start()
            video_display_dial_thread.do_run = False   

            time.sleep(4)

            # Say the "Just relax" string by calling the "my_say" function on its own thread
            called_doc_str =  "^start(animations/Stand/Gestures/CalmDown_6) Done, just relax, the doctor will be here shortly."
            print called_doc_str
            say_called_doc_thread = threading.Thread(name = "say_cald_doc", target = my_say, args = (app, called_doc_str, language, speed))
            say_called_doc_thread.start()
            say_called_doc_thread.do_run = False   

            # Show an image to indicate that you are DONE calling the doctor by calling "vid_disp" on its own thread
            video_display_done_thread = threading.Thread(name = "diplay_done_video", target = vid_disp, args=(exercise_dict["done"]["url"],))
            video_display_done_thread.daemon = True        
            video_display_done_thread.start()
            time.sleep(2)
            video_display_done_thread.do_run = False           

            # UNsubscribe from ASR service and shut down the app / code running on Pepper
            asr_service.unsubscribe("Test_ASR")
            asr_on = False
            app.stop()

    # If ASR detects "NO" and greeting, first exercise are done and we already aksed if the user needs the doctor
    elif greeting_done == True and value[0] == "no" and value[1] >= 0.51:
        if exercise_dict["first"]["isDone"] == True and exercise_dict["second"]["isDone"] == False and ask_pain == True:
            
            # Say the string by calling the "my_say" function on its own thread
            inquire_str = "^start(animations/Stand/Gestures/Explain_7) Okay, no problem. You deserve the rest anyway. ^wait(animations/Stand/Gestures/Explain_7)"
            print inquire_str
            say_inquiry_thread = threading.Thread(name = "say_inquiry", target = my_say, args = (app, inquire_str, language, speed))
            say_inquiry_thread.daemon = True
            say_inquiry_thread.start()
            say_inquiry_thread.do_run = False

            # Wait until Pepper finishes saying the string and update flag
            time.sleep(6)
            not_ready = True

            # Default joint configuration that puts minimum / no load on joint motors
            default_pos = [0.00, -0.21, 1.55, 0.13, -1.24, -0.52, 0.01, 1.56, -0.14, 1.22, 0.52, -0.01]

            # Move joints to default joint configuration by calling the "move" function on its own thread
            move_def_thread = threading.Thread(name = "move_to_def", target = move, args = (session, default_pos))
            move_def_thread.daemon = True
            move_def_thread.start()   
        
            # Get current time
            start_time = time.time()

            # Unsubscribe from ASR it is not needed right now
            asr_service.unsubscribe("Test_ASR")
            asr_on = False

            # Display 30 second countdown video by calling "vid_disp" function on its own thread
            video_display_2_thread = threading.Thread(name = "diplay_timer_video", target = vid_disp, args=(exercise_dict["timer2"]["url"],))
            video_display_2_thread.daemon = True        
            video_display_2_thread.start()
        
            # Wait until 30 second countdown video is done
            while (time.time() - start_time < 32):
                pass

            # Say string by calling "my_say" function on its own thread
            rest_str = "^start(animations/Stand/Gestures/CalmDown_6) Hope you feel better. Let's re-schedule our session for when you're back at a 100 percent. See you!"  
            print rest_str
            rest_say_thread = threading.Thread(name = "say_rest_done", target = my_say, args = (app, rest_str, language, speed))
            rest_say_thread.daemon = True
            rest_say_thread.start()
            rest_say_thread.do_run = False

            # Wait until Pepper is done saying the string
            time.sleep(3)

            # Shut down the app / code running on Pepper
            app.stop()

    return


def onWordRecognized(value):
    """
    Callback function that runs whenever the Automatic Speech Recognition (ASR) module detects that the
    user said "Yes" or "No" to indicate whether or not they are ready to start the entire session and each exercise

    *** For starting the entire session
        - If the user says "Yes":
            Pepper says "Let's start" and displays instructional video for the first exercise on the tablet
            by calling the "vid_disp" function
        
        - If the user says "No":
            Pepper ends the interaction and informs the user to re-schedule when they are feeling better

    *** For starting the first exercise
        - If the user says "Yes":
            Pepper displays the countdown timer for the first exercise on the tablet and calls the
            "run_exercise" function 
        
        - If the user says "No":
            Pepper ends the interaction and informs the user to re-schedule when they are feeling better

    *** For starting the second exercise
        - If the user says "Yes":
            Pepper gives the user some rest by displaying a countdown timer for rest period.
            Afterwards, it displays the instructional video for the second exercise on the tablet 
            by calling the "vid_disp" function
        
        - If the user says "No":
            Pepper asks if the user is not okay to start due to being in pain and if they
            need it to call their doctor, it then runs the "get_doc" function to monitor either hands
            in case the user touches them to indicate they do indeed want their doctor
    """
    # Print string detected by ASR for debugging
    print "value on WORD recog=",value
    
    # Global flags
    global greeting_done
    global showed_first_video
    global showed_second_video
    
    global asr_on
    

    global exercise_dict
    print "First exercise done ", exercise_dict["first"]["isDone"]
    global in_pain
    global ask_pain

    global not_ready

    global vid2_after_long_rest

    global fist_bump

    # Default and Exercise joint positions
    default_pos = [0.00, -0.21, 1.55, 0.13, -1.24, -0.52, 0.01, 1.56, -0.14, 1.22, 0.52, -0.01]
    my_pos = [0.00, -0.21, 1.00, 0.13, -1.24, -0.52, 1.00, 1.00, -0.14, 1.22, 0.52, -1.00]

    # If ASR detects "YES" and greeting the user is done
    if greeting_done == True and showed_first_video == False and showed_second_video == False and value[0] == "yes" and value[1] >= 0.41:
        if exercise_dict["first"]["isDone"] == False and in_pain == False:
            print "Starting First exercise!"

            # Say "Video for first exercise" string by calling "my_say" function on its own thread
            strsay = "^start (animations/Stand/Gestures/ShowTablet_3) Okay, let's get started! Here is a demonstration of our first exercise ^wait(animations/Stand/Gestures/ShowTablet_3)"
            print strsay
            say_vid_1 = threading.Thread(name = "say_disp_vid_1", target = my_say, args = (app, strsay, language, speed))
            say_vid_1.daemon = True
            say_vid_1.start()
            say_vid_1.do_run = False
            
            # Display instructions video for the first exercise by calling "vid_disp" function on its own thread
            video_display_thread = threading.Thread(name = "diplay_video_1", target = vid_disp, args=(exercise_dict["first"]["url"],))
            video_display_thread.daemon = True        
            video_display_thread.start()

            # Update flag and wait 5 seconds
            showed_first_video = True
            time.sleep(5)

            # Move joints to exercise configuration by calling the "move" function on its own thread
            move_def_thread = threading.Thread(name = "move_to_def", target = move, args = (session, default_pos))
            move_def_thread.daemon = True
            move_def_thread.start()

            
            #monitor_fb_thread = threading.Thread(name = "monitor_fb_ex1", target = monitor_fist_bump, args = (memory_service, touch_service, right_count, left_count, 1))
            #monitor_fb_thread.daemon = True
            #monitor_fb_thread.start()

    # If ASR detects "YES" and greeting the user AND showing them the instructions video for first exercise are done
    elif greeting_done == True and showed_first_video == True and showed_second_video == False and value[0] == "yes" and value[1] >= 0.41:
        if exercise_dict["first"]["isDone"] == False and in_pain == False:
        # Start the fist exercise timer, move joints, and monitor tactile sensors on both hands

            # Unsubscribe from ASR service as it is no longer needed
            asr_service.unsubscribe("Test_ASR")
            asr_on = False
        
            # Move joints to exercise joint configuration by calling the "move" function on its own thread
            exercise_thread = threading.Thread(name = "move_to_ex_1", target = move, args = (session, my_pos))
            exercise_thread.daemon = True
            exercise_thread.start()
            
            # Wait until motion is done
            time.sleep(2)
            
            # Say "Starting now" string by calling "my_say" function on its own thread
            start_timer1_str = "^mode(disabled) Okay ! Starting timer"  
            say_st_time1_thread = threading.Thread(name = "say_timer_1", target = my_say, args = (app, start_timer1_str, language, speed))
            say_st_time1_thread.daemon = True
            say_st_time1_thread.start()
            say_st_time1_thread.do_run = False

            # Display 10 second countdown video on tablet by calling "vid_disp" function on its own thread
            timer1_display_timer_thread = threading.Thread(name = "diplay_ex_1_timer", target = vid_disp, args=(exercise_dict["timer"]["url"],))
            timer1_display_timer_thread.daemon = True        
            timer1_display_timer_thread.start()
            
            # Start the execution monitoring for exercise sequence by calling "run_exercise" function on its own thread
            monitorThread = threading.Thread(name = "monitor_hands_ex1", target = run_exercise, args = (memory_service, touch_service, right_count, left_count, 1))
            monitorThread.daemon = True
            monitorThread.start()
        
        # If ASR detects "YES" and greeting the user AND the first exercise is done AND user is NOT in pain / doesn't need doctor
        elif exercise_dict["first"]["isDone"] == True and exercise_dict["second"]["isDone"] == False and in_pain == False and ask_pain == False:
        # Give them some rest and show them the instruction video for the second exercise

            # Say "Let's rest" string by calling "my_say" function on its own thread
            count_30_str = "Great! \\pau=300\\. ^start(animations/Stand/Gestures/ShowTablet_3) Let's rest before the next exercise. ^wait(animations/Stand/Gestures/ShowTablet_3)"
            print count_30_str
            say_c30_thread = threading.Thread(name = "say_counting_10", target = my_say, args = (app, count_30_str, language, speed))
            say_c30_thread.daemon = True
            say_c30_thread.start()
            say_c30_thread.do_run = False

            # Wait until Pepper is saying the string
            time.sleep(5)            

            # Move joints to default joint configuration by calling the "move" function on its own thread
            move_def_thread = threading.Thread(name = "move_to_def", target = move, args = (session, default_pos))
            move_def_thread.daemon = True
            move_def_thread.start()
            
            # Get current time
            start_time = time.time()

            # Display 10 second REST countdown video on tablet by calling "vid_disp" function on its own thread
            video_display_2_thread = threading.Thread(name = "diplay_timer_video", target = vid_disp, args=(exercise_dict["timer"]["url"],))
            video_display_2_thread.daemon = True        
            video_display_2_thread.start()
            
            # Wait until REST countdown video is done
            while (time.time() - start_time < 12):
                pass

            # Say "Let's get back" string by calling "my_say" function on its own thread
            rest_str = "^start(animations/Stand/Gestures/Give_1) Let's get back to work!"  
            print rest_str
            rest_say_thread = threading.Thread(name = "say_rest_done", target = my_say, args = (app, rest_str, language, speed))
            rest_say_thread.daemon = True
            rest_say_thread.start()
            rest_say_thread.do_run = False

            # Say "Video for second exercise" string by calling "my_say" function on its own thread
            say_video_2_str = "^start (animations/Stand/Gestures/ShowTablet_3) Here is a demonstration of the second exercise ^wait(animations/Stand/Gestures/ShowTablet_3)"
            print say_video_2_str
            say_vid_2 = threading.Thread(name = "say_disp_vid_2", target = my_say, args = (app, say_video_2_str, language, speed))
            say_vid_2.daemon = True
            say_vid_2.start()
            time.sleep(1)
            say_vid_2.do_run = False

            # Display instructions video for the first exercise by calling "vid_disp" function on its own thread
            video_display_2_thread = threading.Thread(name = "diplay_video_2", target = vid_disp, args=(exercise_dict["second"]["url"],))
            video_display_2_thread.daemon = True        
            video_display_2_thread.start()

            # Wait until Pepper finishes saying the string and update flag
            time.sleep(6)        
            showed_second_video = True
            time.sleep(2)

            # Move joints to default joint configuration by calling the "move" function on its own thread
            move_def_thread = threading.Thread(name = "move_to_def", target = move, args = (session, default_pos))
            move_def_thread.daemon = True
            move_def_thread.start()   

            #monitor_fb_thread = threading.Thread(name = "monitor_fb_ex2", target = monitor_fist_bump, args = (memory_service, touch_service, right_count, left_count, 2))
            #monitor_fb_thread.daemon = True
            #monitor_fb_thread.start()         
        
    # If ASR detects "YES" and greeting the user AND the first exercise is done AND user is NOT in pain / doesn't need doctor
    elif greeting_done == True and showed_first_video == True and showed_second_video == True and value[0] == "yes" and value[1] >= 0.41:
        # If we already showed the user instructions video for the second exercise
        if exercise_dict["first"]["isDone"] == True and exercise_dict["second"]["isDone"] == False and (ask_pain == False or vid2_after_long_rest == True) and in_pain == False:
            
            # Unsubscribe from ASR service as it is no longer needed
            asr_service.unsubscribe("Test_ASR")
            asr_on = False

            print "Doing exercise 2 now!"
            
            # Move joints to exercise joint configuration by calling the "move" function on its own thread
            exercise_2_thread = threading.Thread(name = "move_to_ex_2", target = move, args = (session, my_pos))
            exercise_2_thread.daemon = True
            exercise_2_thread.start()

            # Wait until motion is done
            time.sleep(3)

            # Say "Starting now" string by calling "my_say" function on its own thread
            start_timer2_str = "^mode(disabled) Okay ! Starting timer"  
            say_st_time2_thread = threading.Thread(name = "say_timer_2", target = my_say, args = (app, start_timer2_str, language, speed))
            say_st_time2_thread.daemon = True
            say_st_time2_thread.start()
            say_st_time2_thread.do_run = False

            # Display 10 second countdown video on tablet by calling "vid_disp" function on its own thread
            timer2_display_timer_thread = threading.Thread(name = "diplay_ex_2_timer", target = vid_disp, args=(exercise_dict["timer"]["url"],))
            timer2_display_timer_thread.daemon = True        
            timer2_display_timer_thread.start()

            # Start the execution monitoring for exercise sequence by calling "run_exercise" function on its own thread
            monitorThread = threading.Thread(name = "monitor_hands_ex2", target = run_exercise, args = (memory_service, touch_service, right_count, left_count, 2))
            monitorThread.daemon = True
            monitorThread.start()
        
    # If ASR detects "NO" and greeting the user is done
    elif greeting_done == True and value[0] == "no" and value[1] >= 0.51:
        # If NO exercises are done yet
        if exercise_dict["first"]["isDone"] == False and exercise_dict["second"]["isDone"] == False and in_pain == False:
        # End the interaction and tell the user to re-schdule

            print "Exiting..."

            # Unsubscribe from ASR service as it is no longer needed
            asr_service.unsubscribe("Test_ASR")
            asr_on = False
        
            # Say "Reschedule" string by calling "my_say" function on its own thread
            shut_down_str = "^mode(disabled) Shutting down, please reshcdule when you're feeling better"
            say_shut_thread = threading.Thread(name = "say_shut_down", target = my_say, args = (app, shut_down_str, language, speed))
            say_shut_thread.start()
            say_shut_thread.do_run = False
            app.stop()

        # If ONLY the first exercise is done
        elif exercise_dict["first"]["isDone"] == True and exercise_dict["second"]["isDone"] == False and ask_pain == False:
        # Ask the user if they said NO to the second exercise because they are in pain and want to see their doctor

            # Say "Are you in pain" string by calling "my_say" function on its own thread
            pain_str =  "^start(animations/Stand/Gestures/Choice_1) Is everything alright ? Do you need me to call the doctor ? ^wait(animations/Stand/Gestures/Choice_1) If so, say \"Yes\" or touch any of my hands."
            print pain_str

            say_pain_thread = threading.Thread(name = "say_in_pain", target = my_say, args = (app, pain_str, language, speed))
            say_pain_thread.start()
            say_pain_thread.do_run = False
            time.sleep(2)
            ask_pain = True

            # Move Pepper's hands closer to the user to allow them touch by calling "move" function on its own thread
            monitorThread = threading.Thread(name = "monitor_hands_for_doc", target = get_doc, args = (memory_service, touch_service, right_count, left_count, 1))
            monitorThread.daemon = True
            monitorThread.start()

    return

def vid_disp(url_to_disp):
    """
    This function is responsible for displaying images and videos on the on-board tablet, more specifically:

    - For the first and second exercises:
        Pepper displays the instructional video for each exercise, gives the user verbal instructions to
        touch its hands it in order for it to monitor execution, and asks the user if they are ready to go after
        having finished watching the instructions. It also displays countdowns for the duration of each exercise

    - For any other case:
        Pepper simply displays the image / video
    
    """

    # Global variables
    global exercise_dict

    # Get the service ALTabletService and connect to on-board tablet
    session = qi.Session()
    try:
        session.connect("tcp://" + os.environ['PEPPER_IP'] + ":" + "9559")
    except RuntimeError:
        print ("Can't connect to TABLET at ip \"" + "10.0.1.204" + "\" on port " + "9559" +".\n"
               "Please check the values.")
        sys.exit(1)

    try:
        tabletService = session.service("ALTabletService")

        # Ensure that the tablet wifi is enabled
        tabletService.enableWifi()

        print "Displaying video now"

        # If we want to display instructions video for either exercise
        if url_to_disp == exercise_dict["first"]["url"] or url_to_disp == exercise_dict["second"]["url"]:

            # Say instructions for either exercise by calling "my_say" function on its own thread
            motivate_str = "Touch the outside of my hand as many times as you can in 10 seconds!"
            print motivate_str
            motivate_say_thread = threading.Thread(name = "say_touch_hands", target = my_say, args = (app, motivate_str, language, speed))
            motivate_say_thread.start()
            time.sleep(3)
            motivate_say_thread.do_run = False

            # Say instructions for either exercise by calling "my_say" function on its own thread
            instruct_str = "Remember, always use proper form, as my friend in the video."
            print instruct_str
            instuct_say_thread = threading.Thread(name = "say_instruct_ex_1", target = my_say, args = (app, instruct_str, language, speed))
            instuct_say_thread.start()
            instuct_say_thread.do_run = False
            
            # Play instructions video and wait until video is done
            tabletService.playVideo(url_to_disp)
            time.sleep(5)            

            # Say "ready to go" string by calling "my_say" function on its own thread
            ready_4_1_str = "Ready to go ?"
            print ready_4_1_str
            say_ready_1 = threading.Thread(name = "ask_ready_4_1", target = my_say, args = (app, ready_4_1_str, language, speed))
            say_ready_1.daemon = True
            say_ready_1.start()
            say_ready_1.do_run = False

            time.sleep(4)
        
        # In case we want to display anything else other than the instructions video for the exercises
        elif url_to_disp == exercise_dict["dial"]["url"]:
            tabletService.showImage(url_to_disp)

        elif url_to_disp == exercise_dict["done"]["url"]:
            tabletService.showImage(url_to_disp)

        elif url_to_disp == exercise_dict["robot_coach"]["url"]:
            tabletService.showImage(url_to_disp)

        elif url_to_disp == exercise_dict["timer"]["url"] or url_to_disp == exercise_dict["timer2"]["url"]:
            tabletService.playVideo(url_to_disp)

    # If we failed to connect to the tablet service for a specific error, print that error
    except Exception, e:
        print "Error was: ", e
    return


if __name__ == "__main__":
"""
Main function responsible for connecting to Pepper and all relevant modules, subscribing to all events
and callback functions as well as defining all relevant global variables.

It is the function that runs the "app" that runs the entire code on Pepper
"""

    # Initialize all global variables that will be needed by all functions
    global asr_on
    asr_on = False
    global greeting_done
    greeting_done = False
    global user_name
    print "greeting done in main is", greeting_done

    global showed_first_video
    showed_first_video = False

    global showed_second_video
    showed_second_video = False
    
    global fist_bump
    fist_bump = False

    global first_exercise_done
    first_exercise_done = False

    right_count = 0
    left_count = 0
    
    global in_pain
    in_pain = False
    
    global ask_pain
    ask_pain = False

    global not_ready 
    not_ready = False

    global vid2_after_long_rest
    vid2_after_long_rest = False

    # Dictionary that includes the URLS for all vidoes and images we want to display
    global exercise_dict
    exercise_dict = {"first": {"number": "1", "url": "https://media.giphy.com/media/ZC60rOP0m9p7lPEqML/giphy.mp4" \
                              , "isDone": False, "pos": [0.00, -0.21, 1.00, 0.13, -1.24, -0.52, 1.00, 1.00, -0.14, 1.22, 0.52, -1.00]}, \
                              "second": {"number": "2", "url": "https://media.giphy.com/media/Zdlpss4k84BcKisa2R/giphy.mp4" \
                              , "isDone": False, "pos": [0.00, -0.21, 0.00, 0.13, 0.00, -0.52, 0.01, 0.00, -0.14, 0.00, 0.52, -0.01]}, \
                                "timer": {"url": "https://media.giphy.com/media/TjSUmJm6Bh39MlES2q/giphy.mp4"}, \
                                "timer2": {"url": "https://media.giphy.com/media/huhFBSwoQkuSyFUV9W/giphy.mp4"}, \
                                "dial": {"url": "http://www.myiconfinder.com/uploads/iconsets/12918a9f351955eb3242ce0e52198993.png"} ,\
             "robot_coach": {"url": "https://cdn.designbyhumans.com/product_images/p/744966.f56.fff9fS7ay1Cm2MjUAAA-650x650-b-p.jpg"} ,\
                               "done": {"url": "https://www.axcelora.com/uploads/1/9/3/0/19308813/1427170805.png"}    } 


    # Get all command line arguments
    args = parse_args()

    pip = args.pip
    pport = args.pport
    language = args.language
    speed = args.speed

    # Connect to Pepper
    app = connect_to_pep(pip, pport)

    # Start the session
    app.start()  
    session = app.session

    # Set English language and subscribe to Automatic Speech Recognition module
    asr_service = session.service("ALSpeechRecognition")
    asr_service.setLanguage("English")

    # Get Touch and Memory services
    memory_service  = session.service("ALMemory")
    touch_service = session.service("ALTouch")

    # Establishing vocabulary for the ASR
    vocabulary = ["yes", "no", "Luca"]
    asr_service.setVocabulary(vocabulary, False)

    # Pepper introduces itself by calling "my_say" function on its own thread
    intro_str = "^start(animations/Stand/Gestures/Hey_6) Hello ^wait(animations/Stand/Gestures/Hey_6), ^start(animations/Stand/Gestures/Me_1) I am Pepper. ^wait(animations/Stand/Gestures/Me_1) If I don't respond to your answers, ^start(animations/Stand/Gestures/Please_1) please repeat what you said ^wait(animations/Stand/Gestures/Please_1), ^start(animations/Stand/Gestures/Think_1) What's your name? ^wait(animations/Stand/Gestures/Think_1)"  
    print intro_str
    intro_say_thread = threading.Thread(name = "saying_intro", target = my_say, args = (app, intro_str, language, speed))
    intro_say_thread.start()
    intro_say_thread.do_run = False

    # Display Image that is shown throughout the interaction on tablet by calling "vid_disp" function on its own thread
    video_display_2_thread = threading.Thread(name = "diplay_video_2", target = vid_disp, args=(exercise_dict["robot_coach"]["url"],))
    video_display_2_thread.daemon = True        
    video_display_2_thread.start()


    # Start the speech recognition engine with user Test_ASR
    asr_service.subscribe("Test_ASR")
    asr_on = True
    print 'Speech recognition engine started'

    # Subscribe to event "WordRecognized" and set callback function
    nameRecognized = memory_service.subscriber("WordRecognized")
    global idNameRecognized
    idNameRecognized = nameRecognized.signal.connect(onNameRecognized)

    # Subscribe to event "WordRecognized" and set callback function
    subWordRecognized = memory_service.subscriber("WordRecognized")
    global idSubWordRecognized
    idSubWordRecognized = subWordRecognized.signal.connect(onWordRecognized)

    # Subscribe to event "WordRecognized" and set callback function
    painRecognized = memory_service.subscriber("WordRecognized")
    global idPainRecognized
    idPainRecognized = painRecognized.signal.connect(onPainRecognized)

    # Run the app
    app.run()

    # When the app stops running, ensure that we UNsubscribe from the ASR module
    if asr_on == True:
        asr_service.unsubscribe("Test_ASR")
        subWordRecognized.signal.disconnect(idSubWordRecognized)
        pass
    elif asr_on == False:
        pass

    # List of Pepper's joints that we need to move
    jointsNames = ["HeadYaw", "HeadPitch",
               "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw",
               "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]

    # Get motion service
    motion_service  = session.service("ALMotion")
    isAbsolute = True

    # Ensure joints move to default position once the app / code / interaction is done
    default_pos = [0.00, -0.21, 1.55, 0.13, -1.24, -0.52, 0.01, 1.56, -0.14, 1.22, 0.52, -0.01]
    motion_service.angleInterpolation(jointsNames, default_pos, 3.0, isAbsolute)

    # Print all done for debugging
    print "Finished"


