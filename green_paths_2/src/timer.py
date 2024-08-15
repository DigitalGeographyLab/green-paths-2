""" Decorator to log the time taken by a function to execute """

import random
import threading
import time
from .logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.CYAN.value)


# this should be used as a decorator for functions
# e.g. @time_logger
def time_logger(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        if hours > 0:
            time_str = f"{int(hours)}h {int(minutes)}min {int(seconds)}s"
        elif minutes > 0:
            time_str = f"{int(minutes)}min {int(seconds)}s"
        else:
            time_str = f"{int(seconds)}s"

        LOG.info(f"Function {func.__name__} took {time_str} to complete")
        return result

    return wrapper


# funny
jokes = [
    "Calculating... Still finding the greenest path, hang tight!",
    "Calculating... routes with the least amount of cow traffic!",
    "Calculating your path to tranquility.",
    "Calculating... Routing through fields of green, just for you!",
    "Calculating... Hold on, ensuring your route has maximum oxygen!",
    "Calculating... Navigating the quietest streets, shhh...",
    "Calculating... Making sure you get the scenic route!",
    "Calculating... Still mapping out the healthiest path for you.",
    "Calculating... Checking for shortcuts through parks!",
    "Calculating... The trees are discussing the best route!",
    "Calculating... Plotting the least polluted route, breathe easy!",
    "Calculating... Avoiding polluted roads, just for you!",
    "Calculating... Do you know why scarecrows are great at math? Because they are outstanding in their fields!",
    "Calculating... Checking the weather along your route... looks like clear skies!",
    "Calculating... Hold tight, avoiding the noisy streets!",
    "Calculating... Mapping the route with the most bird songs!",
    "Calculating... Ensuring your path has the best views!",
    "Calculating... Avoiding all the traffic jams, hang on!",
    "Calculating... Finding the greenest grass for your journey!",
    "Calculating... Did you know? A day on Venus is longer than a year on Venus!",
    "Calculating... The shortest distance between two points is under construction.",
    "Calculating... Why don’t scientists trust atoms? Because they make up everything!",
    "Calculating... Did you know? Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible.",
    "Calculating... Why did the scarecrow become a successful neurosurgeon? He was outstanding in his field!",
    "Calculating... What do you call a lazy kangaroo? A pouch potato!",
    "Calculating... Did you know? The Great Wall of China is not visible from space with the naked eye, but it can be seen using radar.",
    "Calculating... Why did the mathematician refuse to go to the beach? Because he could never find the tangent!",
    "Calculating... Fun fact: Bananas are berries, but strawberries aren't!",
    "Calculating... How does a tree get on the internet? It logs in.",
    "Calculating... Did you know? There are more stars in the universe than grains of sand on all the world's beaches.",
    "Calculating... Why did the chicken join the band? Because it had the drumsticks!",
    "Calculating... Fun fact: A single teaspoon of honey represents the life work of 12 bees.",
    "Calculating... Why was the math book sad? It had too many problems.",
    "Calculating... Did you know? An octopus has three hearts, nine brains, and blue blood.",
    "Calculating... What’s the best way to plan a party in space? You planet.",
    "Calculating... Why don’t we ever tell secrets on a farm? Because the potatoes have eyes and the corn has ears!",
    "Calculating... Fun fact: A bolt of lightning contains enough energy to toast 100,000 slices of bread.",
    "Calculating... Why was the equal sign so humble? Because it knew it wasn’t less than or greater than anyone else.",
    "Calculating... Did you know? A group of flamingos is called a 'flamboyance'.",
    "Calculating... How do you organize a space party? You planet.",
    "Calculating... Why did the student eat his homework? Because the teacher said it was a piece of cake!",
    "Calculating... Fun fact: The Eiffel Tower can be 15 cm taller during the summer due to the expansion of iron in the heat.",
    "Calculating... Did you know? Some turtles can breathe through their butts.",
    "Calculating... What do you call fake spaghetti? An impasta!",
    "Calculating... Why did the computer go to the doctor? Because it had a virus!",
    "Calculating... Did you know? The inventor of the Pringles can is now buried in one.",
    "Calculating... How do scientists freshen their breath? With experi-mints!",
    "Calculating... Did you know? The world’s smallest reptile was discovered in 2021, and it’s only 28.9mm long.",
    "Calculating... Why don’t programmers like nature? It has too many bugs.",
    "Calculating... What do you call a bear with no teeth? A gummy bear!",
    "Calculating... Fun fact: The longest time between two twins being born is 87 days.",
    "Calculating... Did you know? A snail can sleep for three years at a time.",
    "Calculating... Why are frogs so happy? Because they eat whatever bugs them!",
    "Calculating... Did you know? Sea otters hold hands while sleeping to keep from drifting apart.",
    "Calculating... What did the buffalo say to his son when he left for college? Bison!",
    "Calculating... Did you know? The first oranges weren’t orange. The original oranges from Southeast Asia were a tangerine-pomelo hybrid, and they were green.",
    "Calculating... What’s the best way to plan a complex route? Just ask the Chinese postman!",
    "Calculating... Why did the green path cross the road? To get to the quieter side!",
]


def funny_process_logger():
    while True:
        time.sleep(600)  # 10 minutes
        LOG.info(random.choice(jokes))


def progress_still_alive_reporter_funny():
    process_thread = threading.Thread(target=funny_process_logger)
    process_thread.daemon = True
    process_thread.start()


# the idea is to log something to keep user updated that the program is still running
# so might as well make it funny logs...
def with_funny_process_reporter(func):
    def wrapper(*args, **kwargs):
        progress_still_alive_reporter_funny()
        result = func(*args, **kwargs)
        return result

    return wrapper
