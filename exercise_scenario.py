import qi
import argparse
import sys
import time
import os

import threading


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--language", type=str, default="English",
                        help="language")
    parser.add_argument("--speed", type=int, default=100,
                        help="speed")
    print(asr_on)
    # Parse the command line
    return parser.parse_args()

def connect_to_pep(pip, pport):
    #Starting application
    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        app = qi.Application(["Memory Read", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    return app

def check_event(touch_service):
    # larm = False
    # rarm = False
    arm = -1
    s = touch_service.getStatus()
    #print s

    for e in s:
        if e[0]=='LArm' and e[1]:
             #larm = True
             arm = 0
             print "Left arm touched!"
        if e[0]=='RArm' and e[1]:
            #rarm = True
            arm = 1
            print "Right arm touched!"
    return arm




def monitor_fist_bump(memory_service, touch_service, right_count, left_count, ex_num):

    global fist_bump
    global exercise_dict
    my_pos = [0.00, -0.21, 1.00, 0.13, -1.24, -0.52, 1.00, 1.00, -0.14, 1.22, 0.52, -1.00]

    rhMemoryDataValue = "Device/SubDeviceList/RHand/Touch/Back/Sensor/Value"
    lhMemoryDataValue = "Device/SubDeviceList/LHand/Touch/Back/Sensor/Value"

    t = threading.currentThread()
    
    print "Thread that while loops is", t.getName()

    while getattr(t, "do_run", True):

        b = check_event(touch_service)

        if b==0 or b==1:
            print("Fist bumped!")
            fist_bump = True
            t.do_run = False  
            time.sleep(1)        

            asr_service.unsubscribe("Test_ASR")
            asr_on = False
        
            exercise_thread = threading.Thread(name = "move_to_ex_1", target = move, args = (session, my_pos))
            exercise_thread.daemon = True
            exercise_thread.start()
            
            time.sleep(2)
            
            start_timer1_str = "^mode(disabled) Okay ! Starting timer"  
            say_st_time1_thread = threading.Thread(name = "say_timer_1", target = my_say, args = (app, start_timer1_str, language, speed))
            say_st_time1_thread.daemon = True
            say_st_time1_thread.start()
            say_st_time1_thread.do_run = False

            timer1_display_timer_thread = threading.Thread(name = "diplay_ex_1_timer", target = vid_disp, args=(exercise_dict["timer"]["url"],))
            timer1_display_timer_thread.daemon = True        
            timer1_display_timer_thread.start()
            
            if ex_num == 1:

                monitorThread = threading.Thread(name = "monitor_hands_ex1", target = rhMonitorThread, args = (memory_service, touch_service, right_count, left_count, 1))
                monitorThread.daemon = True
                monitorThread.start()

            elif ex_num ==2:

                monitorThread = threading.Thread(name = "monitor_hands_ex2", target = rhMonitorThread, args = (memory_service, touch_service, right_count, left_count, 2))
                monitorThread.daemon = True
                monitorThread.start()


def get_doc(memory_service, touch_service, right_count, left_count, ex_num):

    global exercise_dict
    global user_name

    rhMemoryDataValue = "Device/SubDeviceList/RHand/Touch/Back/Sensor/Value"
    lhMemoryDataValue = "Device/SubDeviceList/LHand/Touch/Back/Sensor/Value"

    t = threading.currentThread()
    
    print "Thread that while loops is", t.getName()

    said_calling = False
    said_done = False

    while getattr(t, "do_run", True):
        
        #print "Running exercise\n"

    
        b = check_event(touch_service)

        if b==0 or b==1:
            print("Getting Doctor!")
            t.do_run = False            


            time.sleep(1)
            in_pain = True
            print "value of in pain is", in_pain

            if said_calling == False:
                doc_str = "^start(animations/Stand/Gestures/CalmDown_6) Calling the doctor now"  
                print doc_str
                doc_say_thread = threading.Thread(name = "say_getting_doc", target = my_say, args = (app, doc_str, language, speed))
                doc_say_thread.daemon = True
                doc_say_thread.start()
                doc_say_thread.do_run = False
    
                said_calling = True

                # Show a video or image to indicate that you are calling the doctor
                video_display_dial_thread = threading.Thread(name = "diplay_dialing_video", target = vid_disp, args=(exercise_dict["dial"]["url"],))
                video_display_dial_thread.daemon = True        
                video_display_dial_thread.start()
                video_display_dial_thread.do_run = False   

                time.sleep(4)

            if said_done == False:

                called_doc_str =  "^start(animations/Stand/Gestures/CalmDown_6) Done. Successfully Called the Doctor. Doctor should be here soon"
                print called_doc_str
                say_called_doc_thread = threading.Thread(name = "say_cald_doc", target = my_say, args = (app, called_doc_str, language, speed))
                say_called_doc_thread.start()
                say_called_doc_thread.do_run = False   

                said_done = True

                video_display_done_thread = threading.Thread(name = "diplay_done_video", target = vid_disp, args=(exercise_dict["done"]["url"],))
                video_display_done_thread.daemon = True        
                video_display_done_thread.start()
                time.sleep(2)
                video_display_done_thread.do_run = False           

            asr_service.unsubscribe("Test_ASR")
            asr_on = False
            app.stop()            
            app.stop()


def rhMonitorThread (memory_service, touch_service, right_count, left_count, ex_num):

    global exercise_dict
    global user_name

    rhMemoryDataValue = "Device/SubDeviceList/RHand/Touch/Back/Sensor/Value"
    lhMemoryDataValue = "Device/SubDeviceList/LHand/Touch/Back/Sensor/Value"

    t = threading.currentThread()
    default_pos = [0.00, -0.21, 1.55, 0.13, -1.24, -0.52, 0.01, 1.56, -0.14, 1.22, 0.52, -0.01]

    start_time = time.time()
    
    print "Thread that while loops is", t.getName()

    said_gj = False
    said_keepup = False

    while getattr(t, "do_run", True):
        
        #print "Running exercise\n"

    
        b = check_event(touch_service)

        if b==0:       
            left_count +=1
            print "Left Hand value thread=", memory_service.getData(lhMemoryDataValue)

            strsay = "^mode(disabled)" + str(left_count) + "^mode(disabled) Left"
            print strsay
            sayThread = threading.Thread(name = "say_L_hand_touched", target = my_say, args = (app, strsay, language, speed))
            sayThread.daemon = True
            sayThread.start()
            time.sleep(1)

        elif b==1:
            print "Right Hand value thread=", memory_service.getData(rhMemoryDataValue)
            right_count +=1 

            strsay = "^mode(disabled)" + str(right_count) + "^mode(disabled) Right" 
            print strsay
            say2Thread = threading.Thread(name = "say_R_hand_touched", target = my_say, args = (app, strsay, language, speed))
            say2Thread.daemon = True
            say2Thread.start()
            time.sleep(1)


        #print "Any hand touched: ", b
        

        elapsed_time =  time.time() - start_time
        #print "time elapsed is", elapsed_time

        if elapsed_time >= 4 and said_gj == False:
            # say "Good job !"
            gj_str =  "^mode(disabled) Good job %s ! " %user_name
            print gj_str
            say_gj_thread = threading.Thread(name = "say_gj", target = my_say, args = (app, gj_str, language, speed))
            say_gj_thread.start()
            say_gj_thread.do_run = False
            said_gj = True 

        elif elapsed_time >= 7 and said_keepup == False:   
            # say "Keep it up ! Just 10 seconds left!"  
            keepup_str =  "^mode(disabled) Keep it up %s, Just 4 seconds left!" %user_name
            print keepup_str
            say_keepup_thread = threading.Thread(name = "say_keepup", target = my_say, args = (app, keepup_str, language, speed))
            say_keepup_thread.start()
            say_keepup_thread.do_run = False
            said_keepup = True

        elif elapsed_time >= 12:     
            #exercise_thread.do_run = False   
            print "Time is up !"

            end_timer2_str = "^start(animations/Stand/Gestures/Far_2) Time's up! ^wait(animations/Stand/Gestures/Far_2) Well done %s !" %user_name  
            say_e_time2_thread = threading.Thread(name = "say_time_up", target = my_say, args = (app, end_timer2_str, language, speed))
            say_e_time2_thread.daemon = True
            say_e_time2_thread.start()
            say_e_time2_thread.do_run = False

            time.sleep(2)

            move_thread = threading.Thread(name = "move_to_def", target = move, args = (session, default_pos))
            move_thread.start()
            time.sleep(1)
            move_thread.do_run = False
            #sayThread.do_run = False
            #say2Thread.do_run = False
            time.sleep(1)
            #motion_service.angleInterpolation(jointsNames, default_pos, 3.0, isAbsolute)
            t.do_run = False
            print "If condition is met ! Exiting while loop"
            #break
                    
    print "Exited the while loop of the Thread"
    if ex_num == 1:
        exercise_dict["first"]["isDone"] = True
        print "First exercise just finished", exercise_dict["first"]["isDone"]

        ask_second_str = "^start(animations/Stand/Gestures/Think_1) Are you okay to keep going %s ? Ready for the next exercise ? ^wait(animations/Stand/Gestures/Think_1)" %user_name
        print ask_second_str
        ask_ready42_thread = threading.Thread(name = "ask_2nd_ex", target = my_say, args = (app, ask_second_str, language, speed))
        ask_ready42_thread.daemon = True
        ask_ready42_thread.start()
        ask_ready42_thread.dorun = False

        asr_service.subscribe("Test_ASR")
        asr_on = True

        #subWordRecognized.signal.connect(onWordRecognized)

    elif ex_num == 2:
        exercise_dict["second"]["isDone"] = True
        
        all_done_str = "^start(animations/Stand/Gestures/Happy_4) All exercises done. Good work ^wait(animations/Stand/Gestures/Happy_4) %s !" %user_name
        print all_done_str
        all_done_thread = threading.Thread(name = "say_all_done_gj", target = my_say, args = (app, all_done_str, language, speed))
        all_done_thread.daemon = True
        all_done_thread.start()
        time.sleep(4)
        all_done_thread.dorun = False
        
        #asr_service.unsubscribe("Test_ASR")
        #asr_on = False
        app.stop()

    

    return


def my_say(app, strsay, language, speed):

    app.start()
    session = app.session


    """
    Say a text with a local configuration.
    """
    # Get the service ALAnimatedSpeech.

    asr_service = session.service("ALAnimatedSpeech")

    # set the local configuration
    configuration = {"bodyLanguageMode":"contextual"}

    # string to say
    #strsay = "Hello, I am a robot !"

    # say the text with the local configuration
    asr_service.say(strsay, configuration)

    tts_service = session.service("ALTextToSpeech")
    tts_service.setVolume(0.2)    
    #tts_service.setLanguage(language)
    #tts_service.setParameter("speed", speed)
    #tts_service.say(strsay)
    print "  -- Say: "+strsay

    return

def move(session, pos):

    jointsNames = ["HeadYaw", "HeadPitch",
               "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw",
               "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]

    #my_pos =      [0.00, -0.21, 0.00, 0.13, 0.00, -0.52, 0.01, 0.00, -0.14, 0.00, 0.52, -0.01]
    #default_pos = [0.00, -0.21, 1.55, 0.13, -1.24, -0.52, 0.01, 1.56, -0.14, 1.22, 0.52, -0.01]

    if (pos==None):
        print 'No joint values.'
        sys.exit(0)

    print "Set joint values: ", pos
    isAbsolute = True

    #Starting services
    motion_service  = session.service("ALMotion")

    names = ["Head", "LArm", "RArm"]
    stiffnessLists = 0.8
    timeLists = 1.0
    motion_service.stiffnessInterpolation(names, stiffnessLists, timeLists)        
    
    if pos == [0.00, -0.21, 1.00, 0.13, -1.24, -0.52, 1.00, 1.00, -0.14, 1.22, 0.52, -1.00]:
        print "moving to my pos"
    elif pos == [0.00, -0.21, 1.55, 0.13, -1.24, -0.52, 0.01, 1.56, -0.14, 1.22, 0.52, -0.01]:
        print "moving to default pos"
    else:
        print "fist bump pos"

    motion_service.angleInterpolation(jointsNames, pos, 1.0, isAbsolute)
    #time.sleep(2)

    return

def onNameRecognized(value):

    print "value on NAME recog=",value
    global greeting_done
    global first_exercise_done
    
    global idNameRecognized

    global user_name
    

    #print "(onNameRecog) Is greeting done yet ?", greeting_done
    #global asr_on

    if  greeting_done == False and value[0] != "yes" and value[0] != "pain" and value [0] != "no" and value [0] != "rest" and value[1] > 0.42:
        user_name = value[0]
        intro_str = "Hello, %s" %user_name
        print intro_str
        intro_say_thread = threading.Thread(name = "say_hello_user", target = my_say, args = (app, intro_str, language, speed))
        intro_say_thread.start()
        intro_say_thread.do_run = False

        greeting_done = True
        #print "greeting done in function", greeting_done

        time.sleep(1)

        #global asr_on
        #if asr_on == True:
        #asr_service.unsubscribe("Test_ASR")
        #asr_on = False
        nameRecognized.signal.disconnect(idNameRecognized)
        #app.stop()
        start_str = "^start(animations/Stand/Gestures/Think_1) Are you ready to start the session ?"  
        print start_str
        start_say_thread = threading.Thread(name = "say_r_u_ready", target = my_say, args = (app, start_str, language, speed))
        start_say_thread.daemon = True
        start_say_thread.start()
        start_say_thread.do_run = False

        #idNameRecognized = nameRecognized.signal.connect(onNameRecognized)


def onPainRecognized(value):

    print "value in PAIN Recog=",value
    global greeting_done
    global in_pain
    global ask_pain
    global asr_on
    global exercise_dict
    #in_pain = True

    global not_ready


    my_pos = [0.00, -0.21, 1.00, 0.13, -1.24, -0.52, 1.00, 1.00, -0.14, 1.22, 0.52, -1.00]
    
    if greeting_done == True and value[0] == "yes" and value[1] >= 0.42:
        if exercise_dict["first"]["isDone"] == True and exercise_dict["second"]["isDone"] == False and ask_pain == True and not_ready == False:    
            in_pain = True
            print "value of in pain is", in_pain
            doc_str = "^start(animations/Stand/Gestures/CalmDown_6) Calling the doctor now"  
            print doc_str
            doc_say_thread = threading.Thread(name = "say_getting_doc", target = my_say, args = (app, doc_str, language, speed))
            doc_say_thread.daemon = True
            doc_say_thread.start()
            doc_say_thread.do_run = False

            # Show a video or image to indicate that you are calling the doctor
            video_display_dial_thread = threading.Thread(name = "diplay_dialing_video", target = vid_disp, args=(exercise_dict["dial"]["url"],))
            video_display_dial_thread.daemon = True        
            video_display_dial_thread.start()
            video_display_dial_thread.do_run = False   

            time.sleep(4)

            called_doc_str =  "^start(animations/Stand/Gestures/CalmDown_6) Done. Successfully Called the Doctor. Doctor should be here soon"
            print called_doc_str
            say_called_doc_thread = threading.Thread(name = "say_cald_doc", target = my_say, args = (app, called_doc_str, language, speed))
            say_called_doc_thread.start()
            say_called_doc_thread.do_run = False   

            video_display_done_thread = threading.Thread(name = "diplay_done_video", target = vid_disp, args=(exercise_dict["done"]["url"],))
            video_display_done_thread.daemon = True        
            video_display_done_thread.start()
            time.sleep(2)
            video_display_done_thread.do_run = False           

            asr_service.unsubscribe("Test_ASR")
            asr_on = False
            app.stop()

    elif greeting_done == True and value[0] == "no" and value[1] >= 0.51:
        if exercise_dict["first"]["isDone"] == True and exercise_dict["second"]["isDone"] == False and ask_pain == True:
            

            inquire_str = "^start(animations/Stand/Gestures/Explain_7) You are not ready for exercise 2. Let's rest for 30 seconds and end this session. ^wait(animations/Stand/Gestures/Explain_7)"
            print inquire_str
            say_inquiry_thread = threading.Thread(name = "say_inquiry", target = my_say, args = (app, inquire_str, language, speed))
            say_inquiry_thread.daemon = True
            say_inquiry_thread.start()
            say_inquiry_thread.do_run = False

            time.sleep(6)
            
            not_ready = True

            #monitorThread = threading.Thread(name = "monitor_hands_for_doc", target = get_doc, args = (memory_service, touch_service, right_count, left_count, 1))
            #monitorThread.daemon = True
            #monitorThread.do_run = False
            #monitorThread.start()

            count_30_str = "^start(animations/Stand/Gestures/ShowTablet_3) Counting 30 seconds of rest now ^wait(animations/Stand/Gestures/ShowTablet_3)"  
            print count_30_str
            say_c30_thread = threading.Thread(name = "say_counting_30", target = my_say, args = (app, count_30_str, language, speed))
            say_c30_thread.daemon = True
            say_c30_thread.start()
            say_c30_thread.do_run = False
        
            start_time = time.time()

            asr_service.unsubscribe("Test_ASR")
            asr_on = False

            video_display_2_thread = threading.Thread(name = "diplay_timer_video", target = vid_disp, args=(exercise_dict["timer2"]["url"],))
            video_display_2_thread.daemon = True        
            video_display_2_thread.start()
        
            #time.sleep(5)            
            while (time.time() - start_time < 32):
                pass

            rest_str = "Rest is done! Schedule a new session when you feel better. See you!"  
            print rest_str
            rest_say_thread = threading.Thread(name = "say_rest_done", target = my_say, args = (app, rest_str, language, speed))
            rest_say_thread.daemon = True
            rest_say_thread.start()
            rest_say_thread.do_run = False

            time.sleep(3)

            app.stop()

    return


def onWordRecognized(value):
    
    print "value on WORD recog=",value
    global greeting_done
    global showed_first_video
    global showed_second_video
    #print "(onWORDrecog) Is greeting done yet ?", greeting_done
    global asr_on
    #print "(onWORDrecog) Is greeting done yet ?", greeting_done
    global exercise_dict
    print "First exercise done ", exercise_dict["first"]["isDone"]
    global in_pain
    global ask_pain

    global not_ready

    global vid2_after_long_rest

    global fist_bump

    #old # my_pos = [0.00, -0.21, 0.00, 0.13, 0.00, -0.52, 0.01, 0.00, -0.14, 0.00, 0.52, -0.01]
    default_pos = [0.00, -0.21, 1.55, 0.13, -1.24, -0.52, 0.01, 1.56, -0.14, 1.22, 0.52, -0.01]
    my_pos = [0.00, -0.21, 1.00, 0.13, -1.24, -0.52, 1.00, 1.00, -0.14, 1.22, 0.52, -1.00]

    if greeting_done == True and showed_first_video == False and showed_second_video == False and value[0] == "yes" and value[1] >= 0.41:
        if exercise_dict["first"]["isDone"] == False and in_pain == False:
            print "Starting First exercise!"

            #asr_service.unsubscribe("Test_ASR")
            #asr_on = False
            

            #subWordRecognized.signal.disconnect(idSubWordRecognized)
                
            #t = threading.currentThread()

            #while getattr(t, "do_run", True):
            strsay = "^start (animations/Stand/Gestures/ShowTablet_3) Here is a video of exercise ^wait(animations/Stand/Gestures/ShowTablet_3)" + exercise_dict["first"]["number"]
            print strsay
            say_vid_1 = threading.Thread(name = "say_disp_vid_1", target = my_say, args = (app, strsay, language, speed))
            say_vid_1.daemon = True
            say_vid_1.start()
            say_vid_1.do_run = False
            
            #time.sleep(1)
            video_display_thread = threading.Thread(name = "diplay_video_1", target = vid_disp, args=(exercise_dict["first"]["url"],))
            video_display_thread.daemon = True        
            video_display_thread.start()

            showed_first_video = True

            time.sleep(5)

            # vid_1_start_time = time.time()
            #while (time.time() - vid_1_start_time < 7):
                #pass
            
            ready_4_1_str = "Ready to start the first exercise ?"
            print ready_4_1_str
            say_ready_1 = threading.Thread(name = "ask_ready_4_1", target = my_say, args = (app, ready_4_1_str, language, speed))
            say_ready_1.daemon = True
            say_ready_1.start()
            say_ready_1.do_run = False

            time.sleep(4)

            move_def_thread = threading.Thread(name = "move_to_def", target = move, args = (session, default_pos))
            move_def_thread.daemon = True
            move_def_thread.start()

            
            monitor_fb_thread = threading.Thread(name = "monitor_fb_ex1", target = monitor_fist_bump, args = (memory_service, touch_service, right_count, left_count, 1))
            monitor_fb_thread.daemon = True
            monitor_fb_thread.start()

    elif greeting_done == True and showed_first_video == True and showed_second_video == False and value[0] == "yes" and value[1] >= 0.41:
        if exercise_dict["first"]["isDone"] == False and in_pain == False:

            asr_service.unsubscribe("Test_ASR")
            asr_on = False
        
            exercise_thread = threading.Thread(name = "move_to_ex_1", target = move, args = (session, my_pos))
            exercise_thread.daemon = True
            exercise_thread.start()
            
            time.sleep(2)
            
            start_timer1_str = "^mode(disabled) Okay ! Starting timer"  
            say_st_time1_thread = threading.Thread(name = "say_timer_1", target = my_say, args = (app, start_timer1_str, language, speed))
            say_st_time1_thread.daemon = True
            say_st_time1_thread.start()
            say_st_time1_thread.do_run = False

            timer1_display_timer_thread = threading.Thread(name = "diplay_ex_1_timer", target = vid_disp, args=(exercise_dict["timer"]["url"],))
            timer1_display_timer_thread.daemon = True        
            timer1_display_timer_thread.start()
            

            monitorThread = threading.Thread(name = "monitor_hands_ex1", target = rhMonitorThread, args = (memory_service, touch_service, right_count, left_count, 1))
            monitorThread.daemon = True
            monitorThread.start()
        
            
            #monitorThread.do_run = False

        elif exercise_dict["first"]["isDone"] == True and exercise_dict["second"]["isDone"] == False and in_pain == False and ask_pain == False:

            #subWordRecognized.signal.disconnect(idSubWordRecognized)
            

            count_30_str = " Great! \\pau=300\\. Let's rest before the second exercise. \\pau=500\\. ^start(animations/Stand/Gestures/ShowTablet_3) Counting 10 seconds of rest now ^wait(animations/Stand/Gestures/ShowTablet_3)"  
            print count_30_str
            say_c30_thread = threading.Thread(name = "say_counting_10", target = my_say, args = (app, count_30_str, language, speed))
            say_c30_thread.daemon = True
            say_c30_thread.start()
            say_c30_thread.do_run = False

            time.sleep(5)            

            move_def_thread = threading.Thread(name = "move_to_def", target = move, args = (session, default_pos))
            move_def_thread.daemon = True
            move_def_thread.start()
            
            start_time = time.time()

            video_display_2_thread = threading.Thread(name = "diplay_timer_video", target = vid_disp, args=(exercise_dict["timer"]["url"],))
            video_display_2_thread.daemon = True        
            video_display_2_thread.start()
            
            
            while (time.time() - start_time < 12):
                pass

            rest_str = "^start(animations/Stand/Gestures/Give_1) Rest is done!"  
            print rest_str
            rest_say_thread = threading.Thread(name = "say_rest_done", target = my_say, args = (app, rest_str, language, speed))
            rest_say_thread.daemon = True
            rest_say_thread.start()
            rest_say_thread.do_run = False


            say_video_2_str = "^start (animations/Stand/Gestures/ShowTablet_3) Here is a video of exercise ^wait(animations/Stand/Gestures/ShowTablet_3)" + exercise_dict["second"]["number"]
            print say_video_2_str
            say_vid_2 = threading.Thread(name = "say_disp_vid_2", target = my_say, args = (app, say_video_2_str, language, speed))
            say_vid_2.daemon = True
            say_vid_2.start()
            time.sleep(1)
            say_vid_2.do_run = False

            video_display_2_thread = threading.Thread(name = "diplay_video_2", target = vid_disp, args=(exercise_dict["second"]["url"],))
            video_display_2_thread.daemon = True        
            video_display_2_thread.start()

            time.sleep(6)        

            showed_second_video = True

            ready_4_2_str = "Ready to start ?"
            print ready_4_2_str
            say_ready_2 = threading.Thread(name = "ask_ready_4_2", target = my_say, args = (app, ready_4_2_str, language, speed))
            say_ready_2.daemon = True
            say_ready_2.start()
            say_ready_2.do_run = False

            time.sleep(2)

            move_def_thread = threading.Thread(name = "move_to_def", target = move, args = (session, default_pos))
            move_def_thread.daemon = True
            move_def_thread.start()   

            monitor_fb_thread = threading.Thread(name = "monitor_fb_ex2", target = monitor_fist_bump, args = (memory_service, touch_service, right_count, left_count, 2))
            monitor_fb_thread.daemon = True
            monitor_fb_thread.start()         
        
    elif greeting_done == True and showed_first_video == True and showed_second_video == True and value[0] == "yes" and value[1] >= 0.41:
        print "Passed first condition"
        if exercise_dict["first"]["isDone"] == True and exercise_dict["second"]["isDone"] == False and (ask_pain == False or vid2_after_long_rest == True) and in_pain == False:
            
            asr_service.unsubscribe("Test_ASR")
            asr_on = False

            print "Doing exercise 2 now!"
            
            exercise_2_thread = threading.Thread(name = "move_to_ex_2", target = move, args = (session, my_pos))
            exercise_2_thread.daemon = True
            exercise_2_thread.start()

            time.sleep(6)

            start_timer2_str = "^mode(disabled) Okay ! Starting timer"  
            say_st_time2_thread = threading.Thread(name = "say_timer_2", target = my_say, args = (app, start_timer2_str, language, speed))
            say_st_time2_thread.daemon = True
            say_st_time2_thread.start()
            say_st_time2_thread.do_run = False

            timer2_display_timer_thread = threading.Thread(name = "diplay_ex_2_timer", target = vid_disp, args=(exercise_dict["timer"]["url"],))
            timer2_display_timer_thread.daemon = True        
            timer2_display_timer_thread.start()


            monitorThread = threading.Thread(name = "monitor_hands_ex2", target = rhMonitorThread, args = (memory_service, touch_service, right_count, left_count, 2))
            monitorThread.daemon = True
            monitorThread.start()
            
            #asr_service.unsubscribe("Test_ASR")
            #asr_on = False
            #subWordRecognized.signal.disconnect(idSubWordRecognized)
            #app.stop()

    elif greeting_done == True and value[0] == "no" and value[1] >= 0.51:
        if exercise_dict["first"]["isDone"] == False and exercise_dict["second"]["isDone"] == False and in_pain == False:
            print "Exiting..."

            asr_service.unsubscribe("Test_ASR")
            asr_on = False
            #subWordRecognized.signal.disconnect(idSubWordRecognized)
        
            shut_down_str = "Shutting down"
            say_shut_thread = threading.Thread(name = "say_shut_down", target = my_say, args = (app, shut_down_str, language, speed))
            say_shut_thread.start()
            say_shut_thread.do_run = False
            app.stop()

        elif exercise_dict["first"]["isDone"] == True and exercise_dict["second"]["isDone"] == False and ask_pain == False:
            
            pain_str =  "^start(animations/Stand/Gestures/Choice_1) Are you Okay ? Should I call the doctor ? ^wait(animations/Stand/Gestures/Choice_1) Say \"Yes\" or touch any of my hands and I will call the doctor."
            print pain_str

            say_pain_thread = threading.Thread(name = "say_in_pain", target = my_say, args = (app, pain_str, language, speed))
            say_pain_thread.start()
            say_pain_thread.do_run = False
            time.sleep(2)
            ask_pain = True

            monitorThread = threading.Thread(name = "monitor_hands_for_doc", target = get_doc, args = (memory_service, touch_service, right_count, left_count, 1))
            monitorThread.daemon = True
            monitorThread.start()

    return

def vid_disp(url_to_disp):
    """
    This example uses the playVideo method.
    To Test ALTabletService, you need to run the script ON the robot.
    """

    global exercise_dict

    # Get the service ALTabletService.
    session = qi.Session()
    try:
        session.connect("tcp://" + os.environ['PEPPER_IP'] + ":" + "9559")
    except RuntimeError:
        print ("Can't connect to TABLET at ip \"" + "10.0.1.204" + "\" on port " + "9559" +".\n"
               "Please check the values.")
        sys.exit(1)

    try:
        tabletService = session.service("ALTabletService")

        # Ensure that the tablet wifi is enable
        tabletService.enableWifi()

        # Play a video from the web and display the player
        # If you want to play a local video, the ip of the robot from the tablet is 198.18.0.1
        # Put the video in the HTML folder of your behavior
        # "http://198.18.0.1/apps/my_behavior/my_video.mp4"

        print "Displaying video now"
        #https://cmeimg-a.akamaihd.net/640/ppds/3ed04e1e-c4de-4f73-83ff-1923fa6e56bd.gif
        #tabletService.playVideo("https://media.giphy.com/media/hXD7h0AFIX3poVuFV3/giphy.mp4")
        #tabletService.playVideo("https://media.giphy.com/media/JSjfefFkzyTuQLykfz/giphy.mp4")
        
        #tabletService.playVideo("https://media.giphy.com/media/5t9IcXiBCyw60XPpGu/giphy.mp4")
        #tabletService.playVideo("http://clips.vorwaerts-gmbh.de/big_buck_bunny.mp4")

 
        #time.sleep(2)

        # Display the time elapse / the total time of the video
        #print tabletService.getVideoPosition(), " / ", tabletService.getVideoLength()
  
        # Pause the video
        #tabletService.pauseVideo()

        if url_to_disp == exercise_dict["first"]["url"] or url_to_disp == exercise_dict["second"]["url"]:
            instruct_str = "I will be your partner, just like the person on the left is."
            print instruct_str
            instuct_say_thread = threading.Thread(name = "say_instruct_ex_1", target = my_say, args = (app, instruct_str, language, speed))
            instuct_say_thread.start()
            instuct_say_thread.do_run = False
            time.sleep(3)
            

            motivate_str = "Touch the outside of my hand as many times as you can in 30 seconds!"
            print motivate_str
            motivate_say_thread = threading.Thread(name = "say_touch_hands", target = my_say, args = (app, motivate_str, language, speed))
            motivate_say_thread.start()
            time.sleep(3)
            motivate_say_thread.do_run = False
            

            #time.sleep(3)
        
            tabletService.playVideo(url_to_disp)

        elif url_to_disp == exercise_dict["dial"]["url"]:
            tabletService.showImage(url_to_disp)
            #time.sleep(5) 
            #tabletService.hideImage()

            #time.sleep(3)
            # resume the video
            #tabletService.resumeVideo()
            """  
            time.sleep(3)
            """
            # stop the video and hide the player
            #tabletService.stopVideo()

        elif url_to_disp == exercise_dict["done"]["url"]:
            tabletService.showImage(url_to_disp)
            #time.sleep(5) 
            #tabletService.hideImage()

        elif url_to_disp == exercise_dict["robot_coach"]["url"]:
            tabletService.showImage(url_to_disp)

        elif url_to_disp == exercise_dict["timer"]["url"] or url_to_disp == exercise_dict["timer2"]["url"]:
            tabletService.playVideo(url_to_disp)
            


    except Exception, e:
        print "Error was: ", e
    return


def play_audio():

    session = qi.Session()
    ap_service = session.service("ALAudioPlayer")

    try:
        #Loads a file and launchs the playing 5 seconds later
        fileId = ap_service.loadFile(os.path.abspath(afile))
        fileLength =ap_service.getFileLength(fileId)
        print 'Playing '+afile+'. Duration: '+ str(fileLength) +' secs. Press Ctrl+C to stop'
        ap_service.play(fileId, _async = True)
    except KeyboardInterrupt:
        ap_service.stopAll()
        print('Quitting')
        sys.exit(0)

    return


if __name__ == "__main__":


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



    args = parse_args()

    pip = args.pip
    pport = args.pport
    language = args.language
    speed = args.speed

    app = connect_to_pep(pip, pport)

    app.start()  
    session = app.session

    asr_service = session.service("ALSpeechRecognition")
    asr_service.setLanguage("English")

    #asr_service.unsubscribe("Test_ASR")

    memory_service  = session.service("ALMemory")
    touch_service = session.service("ALTouch")

    #establishing test vocabulary
    vocabulary = ["yes", "no", "John"]
    asr_service.setVocabulary(vocabulary, False)

    intro_str = "^start(animations/Stand/Gestures/Hey_6) Hello ^wait(animations/Stand/Gestures/Hey_6), ^start(animations/Stand/Gestures/Me_1) I am Pepper. ^wait(animations/Stand/Gestures/Me_1) If I don't respond to your answers, ^start(animations/Stand/Gestures/Please_1) please repeat what you said ^wait(animations/Stand/Gestures/Please_1), ^start(animations/Stand/Gestures/Think_1) What's your name? ^wait(animations/Stand/Gestures/Think_1)"  
    print intro_str
    intro_say_thread = threading.Thread(name = "saying_intro", target = my_say, args = (app, intro_str, language, speed))
    intro_say_thread.start()
    intro_say_thread.do_run = False


    video_display_2_thread = threading.Thread(name = "diplay_video_2", target = vid_disp, args=(exercise_dict["robot_coach"]["url"],))
    video_display_2_thread.daemon = True        
    video_display_2_thread.start()


    # Start the speech recognition engine with user Test_ASR
    asr_service.subscribe("Test_ASR")
    asr_on = True
    print 'Speech recognition engine started'

    nameRecognized = memory_service.subscriber("WordRecognized")
    global idNameRecognized
    idNameRecognized = nameRecognized.signal.connect(onNameRecognized)

    #if greeting_done == True:
    #subscribe to event WordRecognized
    subWordRecognized = memory_service.subscriber("WordRecognized")
    global idSubWordRecognized
    idSubWordRecognized = subWordRecognized.signal.connect(onWordRecognized)

    # Do I need a 3rd function for the 2nd exercises ??
    painRecognized = memory_service.subscriber("WordRecognized")
    global idPainRecognized
    idPainRecognized = painRecognized.signal.connect(onPainRecognized)

    restRecognized = memory_service.subscriber("WordRecognized")
    global idRestRecognized
    idRestRecognized = painRecognized.signal.connect(onRestRecognized)


    #let it run
    app.run()

    #move_thread.do_run = False

    if asr_on == True:
        asr_service.unsubscribe("Test_ASR")
        subWordRecognized.signal.disconnect(idSubWordRecognized)
        pass
    elif asr_on == False:
        pass


    jointsNames = ["HeadYaw", "HeadPitch",
               "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw",
               "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]

    motion_service  = session.service("ALMotion")
    isAbsolute = True

    default_pos = [0.00, -0.21, 1.55, 0.13, -1.24, -0.52, 0.01, 1.56, -0.14, 1.22, 0.52, -0.01]
    motion_service.angleInterpolation(jointsNames, default_pos, 3.0, isAbsolute)


    print "Finished"


