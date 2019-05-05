from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
from os import path
from pynput.keyboard import Key, Controller
from math import floor
from selenium.common.exceptions import NoSuchElementException
from sys import exit

BASE_URL = "https://www.messenger.com/t/"
FILE_NAME = "login_details.txt"
DATETIME_NEXT_EPISODE = datetime.datetime(2019, 5, 6, 3)

driver = webdriver.Firefox(executable_path=r'..\geckodriver.exe')


def init_details_file():
    with open('login_details', 'w') as f:
            print("email=", file=f)
            print("password=", file=f)
            print("CHAT_ID=", file=f)


def read_details_from_file(file_name):
    if not path.isfile("login_details.txt"):
        init_details_file()
        raise FileNotFoundError("Please fill in file login_details.txt")

    with open(file_name, 'r') as f:
        var = [x for x in f.readlines()]

    details = [x[x.index("=") + 1:] for x in var]
    return details


configs = read_details_from_file(FILE_NAME)

email = configs[0]
password = configs[1]
GOT_CHAT_ID = configs[2]

def log_in():
    time.sleep(3)
    print("Loaded")
    # adding email
    input_em = driver.find_element_by_id("email")
    input_em.clear()
    input_em.send_keys(email)

    # adding password
    input_pw = driver.find_element_by_id("pass")
    input_pw.send_keys(password)

    print("Added email and password. Logging in")
    input_pw.send_keys(Keys.ENTER)


def change_title(time_left):
    # Logged in. Changing title of chat.

    new_title = "GoT - {}".format(time_left)

    time.sleep(10)
    alter_group_name = driver.find_element_by_class_name("_2jnt")
    alter_group_name.click()

    text_field = alter_group_name.find_element_by_class_name("_2jnu")
    text_field.click()
    print("\tClicked textfield")
    time.sleep(1)

    keyboard = Controller()
    print("\tRemoving previous text")

    # TODO Change to CTRL + a, then delete
    for x in range(len(new_title) + 20):
        keyboard.press(Key.right)
        keyboard.release(Key.right)

    for x in range(len(new_title) + 20):
        keyboard.press(Key.backspace)
        keyboard.release(Key.backspace)
    keyboard.type(new_title)
    keyboard.press(Key.enter)
    # text_field.send_keys(new_title)

    print("\tEntered text")


def determine_time_string():
    time_diff = calculate_remaining_time()
    if time_diff.days > 1:
        return str(time_diff.days) + " dager"
    if time_diff.days == 1:
        return str(time_diff.days) + " dag"

    # If there is less than a day left. Continue with hours below

    important_hours = [  # NOTE: hour - 1     ---- don't ask
        11, 8, 5, 2, 1
    ]

    tot = time_diff.total_seconds()
    tot /= 60
    tot /= 60  # to get hours
    tot = floor(tot)
    if tot in important_hours:
        return str(tot + 1) + " timer"
    if tot == 1:
        return str(tot + 1) + " time"

    return -1


def calculate_remaining_time():
    current_time = datetime.datetime.today()
    time_diff = datetime.timedelta(days=DATETIME_NEXT_EPISODE.day-current_time.day,
                                   hours=DATETIME_NEXT_EPISODE.hour-current_time.hour,
                                   minutes=DATETIME_NEXT_EPISODE.minute-current_time.minute)
    return time_diff


def perform_alteration(episode_out=False):
    time_left = determine_time_string()
    if time_left == -1:  # check if necessary to log in and change
        return

    driver.get(BASE_URL + GOT_CHAT_ID)
    log_in()
    if episode_out:
        change_title("!!!")
        return
    change_title(time_left)
    print("Successfully changed title")
    time.sleep(2)
    driver.delete_all_cookies()
    driver.refresh()


def main():
    print("Started program for updating the countdown.")

    diff_day = 6

    while True:
        current_time = datetime.datetime.today()

        if current_time > DATETIME_NEXT_EPISODE:
            print("Episode is out")
            perform_alteration(episode_out=True)
            print("Shutting down")
            exit()

        print(current_time)
        if current_time.weekday() != diff_day:
            print(current_time.weekday())
            print("Day changed")
            perform_alteration()
            diff_day = current_time.weekday()

        current_minute = current_time.minute
        if current_minute == 1:
            try:
                perform_alteration()
                print("Waiting 1 hour for the next run")
                time.sleep(61)
            except NoSuchElementException as e:
                print("ERROR: Could not load in time. Trying again..")
            finally:
                print("~~~~~~~~~~~~~~~~~")
        time.sleep(30)


main()
