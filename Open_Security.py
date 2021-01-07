import cv2
import tweepy
from tkinter import *
import playsound
import pygame

class Output:
    def __init__(self, security_level, object_detection, object_boxing, no_trespassing):
        self.security_level = security_level
        self.object_detection = object_detection
        self.object_boxing = object_boxing
        self.no_trespassing = no_trespassing

    """
    Main
    - start_video_processing takes care of video processing and object detection
    """
    def start_video_processing(self):

        # the video capture object (responsible for getting raw video data)
        capture = cv2.VideoCapture(0)

        # the objects we want to detect (cascades)
        gun_cascade = cv2.CascadeClassifier("cascades/m9.xml")
        knife_cascade = cv2.CascadeClassifier("cascades/knife.xml")
        person_cascade = cv2.CascadeClassifier("cascades/face.xml")

        object_in_view_frames = 0  # this is keep track of how many frames a gun is in view for
        object_in_view_already_detected = False

        while True:
            feed_on, frame = capture.read()

            # Scan for guns and store the result if needed
            if self.object_detection:
                if self.no_trespassing:
                    person_in_view = person_cascade.detectMultiScale(frame, 1.3, 2)
                    gun_in_view = ()
                    knife_in_view = ()
                elif self.security_level == 1:  # 1 == high security
                    gun_in_view = gun_cascade.detectMultiScale(frame, 2, 2)
                    knife_in_view = knife_cascade.detectMultiScale(frame, 2, 2)
                    person_in_view = ()
                else:
                    gun_in_view = ()
                    person_in_view = ()
                    knife_in_view = knife_cascade.detectMultiScale(frame, 2, 2)
            else:
                gun_in_view = ()
                knife_in_view = ()
                person_in_view = ()

            # Outline any guns or knives in view and act accordingly
            if gun_in_view != () or knife_in_view != () or person_in_view != ():
                if self.object_boxing:
                    for (x, y, w, h) in gun_in_view:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    for (x, y, w, h) in knife_in_view:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    for (x, y, w, h) in person_in_view:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                object_in_view_frames += 1
                if object_in_view_frames > 4 and not object_in_view_already_detected:
                    cv2.imwrite("positive_detections/alert.jpg", frame)
                    self.send_tweet()
                    object_in_view_already_detected = True
            else:
                object_in_view_frames = 0
                object_in_view_already_detected = False

            # Output the video feed
            cv2.imshow("Video Feed", frame)

            # Define how to exit and halt the video feed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
        capture.release()

    """
    send_tweet
    - Resonsible for sending a tweet when a gun us detected
    """
    def send_tweet(self):
        # Api keys required
        consumer_key = "VvPlmI6w4sdg3AdQ055nW0Mq6"
        consumer_secret = "vlGOr8mwZly5FWucbVvqDarbiVYMv8GIk2uEuHvYXaFuo8ZMyO"
        access_key = "954725736790810627-0LIzKoQB26Ap4jgt3tS8Fiao3yZAjAM"
        access_secret = "XPgIM9G0uNhGxzCMMoEm3qiplMOuwGt4f4iSobEIhsyCB"

        # api setup
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)

        # make a sound
        pygame.init()
        pygame.mixer.init()
        dis = pygame.display.set_mode((1, 1))  ### import a sound file and play it using pygame
        sound = pygame.mixer.Sound("./assets/Alert_sound.wav")
        sound.play()

        # Send a tweet
        if self.no_trespassing:
            api.update_with_media("positive_detections/alert.jpg", "Alert!!! A trespasser has been caught")
        else:
            api.update_with_media("positive_detections/alert.jpg", "Alert!!! Someone in posession of a dangerous weapon has"
                                                    " been detected in Bahen! (THIS IS JUST A TEST AND IS NOT REAL)")
        pygame.quit()

class OptionMenu:
    def __init__(self):
        # Creating output screens and basic setup
        self.master_screen = Tk()
        self.master_screen.minsize(width=600, height=400)
        self.master_screen.maxsize(width=600, height=400)
        self.master_screen.title("Open Security")
        self.master_screen.configure(bg="Gray")
        # variables to keep track of user preference
        self.security_level_input = 1  # 1 = High Security(guns, knife)   2 = Low Security(just knife)
        self.object_detection_input = True  # toggle the object detection feature
        self.object_boxing_input = True  # toggle the object boxing feature
        self.no_trespassing = False
        # Place (print) user prederences on the screen
        security_message = self.determine_option_message()
        boxing_message = self.determine_boxing_message()
        self.security_label = Label(self.master_screen, text=security_message, bg="Gray", fg="green", font=("Helvetica", 20))
        self.security_label.place(x=110, y=270)
        self.boxing_label = Label(self.master_screen, text=boxing_message, bg="Gray", fg="green",
                                    font=("Helvetica", 20))
        self.boxing_label.place(x=170, y=310)


    def start(self):
        self.master_screen.destroy()

    def start_no_trespassing(self):
        self.no_trespassing = True
        self.object_detection_input = True
        self.master_screen.destroy()

    def exit_app(self):
        self.master_screen.destroy()
        quit()

    def set_to_low_security(self):
        self.security_level_input = 2
        self.display_option_message()

    def set_to_high_security(self):
        self.security_level_input = 1
        self.display_option_message()

    def toggle_object_detection(self):
        self.object_detection_input = not self.object_detection_input
        self.display_option_message()

    def toggle_object_boxing(self):
        self.object_boxing_input = not self.object_boxing_input
        self.display_boxing_message()

    def determine_option_message(self):
        if not self.object_detection_input:
            security_message = "Selected Option = All object detection is off"
        elif self.security_level_input == 1:
            security_message = "Selected Option = High Security"
        else:
            security_message = "Selected Option = Low Security"
        return security_message

    def display_option_message(self):
        security_message = self.determine_option_message()
        self.security_label.destroy()
        self.security_label = Label(self.master_screen, text=security_message, bg="Gray", fg="green",
                                    font=("Helvetica", 20))
        if security_message != "Selected Option = All object detection is off":
            self.security_label.place(x=110, y=270)
        else:
            self.security_label.place(x=30, y=270)

    def determine_boxing_message(self):
        if self.object_boxing_input:
            return "Object boxing is on "
        else:
            return "Object boxing is off"

    def display_boxing_message(self):
        self.boxing_label = Label(self.master_screen, text=self.determine_boxing_message(), bg="Gray", fg="green",
                                  font=("Helvetica", 20))
        self.boxing_label.place(x=170, y=310)

    def options_menu(self):
        # Declaring all widgets
        # Labels
        app_title = Label(self.master_screen, text="Open Security", bg="Gray", fg="green", font=("Helvetica", 30))
        # buttons
        start_button = Button(self.master_screen, text="Start", command=self.start, font=("Helvetica", 15),
                             height=1, width=10)
        exit_button = Button(self.master_screen, text="Exit", command=self.exit_app, font=("Helvetica", 15),
                             height=1, width=10)
        low_button = Button(self.master_screen, text="Low Security", command=self.set_to_low_security,
                            font=("Helvetica", 15),
                             height=1, width=10)
        high_button = Button(self.master_screen, text="High Security", command=self.set_to_high_security,
                             font=("Helvetica", 15),
                             height=1, width=10)
        dectection_button = Button(self.master_screen, text="Toggle Object Detection", command=self.toggle_object_detection,
                             font=("Helvetica", 15),
                             height=1, width=25)
        object_boxing_button = Button(self.master_screen, text="Toggle Object Boxing", command=self.toggle_object_boxing,
                              font=("Helvetica", 15),
                              height=1, width=25)
        no_trespassing_button = Button(self.master_screen, text="No Trespassing Mode",
                                      command=self.start_no_trespassing,
                                      font=("Helvetica", 15),
                                      height=1, width=18)

        # Outputting all widgets
        # Labels
        app_title.place(x=175, y=30)
        # buttons
        start_button.place(x=0, y=355)
        exit_button.place(x=480, y=355)
        low_button.place(x=160, y=110)
        high_button.place(x=325, y=110)
        dectection_button.place(x=160, y=170)
        object_boxing_button.place(x=160, y=230)
        no_trespassing_button.place(x=140, y=355)

        self.master_screen.mainloop()

if __name__ == "__main__":
    while True:
        options_menu = OptionMenu()
        options_menu.options_menu()
        output = Output(options_menu.security_level_input, options_menu.object_detection_input,
                        options_menu.object_boxing_input, options_menu.no_trespassing)
        output.start_video_processing()
