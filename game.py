""" Abstraction of a full game of Tichu, consisting of several rounds. """

import logging
import time
from multiprocessing.dummy import Process

#_Set_up_logging________________________________________________________________

logger = logging.getLogger('tichu')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s][%(name)s] %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.propagate = False

# Create a custom log level
level = 25 # WARN=30, INFO=20, DEBUG=10
levelname = 'GAME'
methodname = levelname.lower()
def log_for_level(self, message, *args, **kwargs) :
    self._log(level, message, args, **kwargs)
logging.addLevelName(level, levelname)
setattr(logging, levelname, level)
setattr(logging.getLoggerClass(), methodname, log_for_level)

#_Game__________________________________________________________________________

class Game() :
    pass

#_Round_________________________________________________________________________

class Round() :
    pass

#_Trick_________________________________________________________________________

class Trick() :
    # The type of combination that will be played in this trick
    combo_type = None
    # List keeping track of played combinations
    played_combinations = []
    # Set keeping track of players that have passed
    passed = set()
    # Track if anything happens that makes it impossible for this trick to 
    # properly finish (e.g. ragequit of a player)
    trick_unplayable = False

    def __init__(self, players, starting_player=0) :
        """
        ===============  =======================================================
        players          list of :class: `Player <tichu.player.Player>` 
                         objects; representing the players in their turn 
                         order.  
        starting_player  int; todo
        ===============  =======================================================
        """
        self.players = players
        self.trick_process = Process(target=self._trickloop)

    def start_trickloop(self) :
        logger.info('Starting trickloop.')
        self.trick_process.start()

    def _trickloop(self) :
        while not self.trick_finished() :
            player = self.players[0]

            action = self.prompt_to_play(player)
            action_handled = self.handle_action(action, player)
    
            # Rotate to the next player
            if action_handled :
                self.rotate_players()

    def handle_action(self, action, player) :
        """ Determine what action was taken and respond appropriately. """
        if action.name == 'pass' :
            logger.game('%s passes.', player.name)
            # TODO Starting player may not pass.
            # Add this player to the set off passing players
            self.passed.add(player)
            return True
            
        elif action.name == 'play' :
            logger.game('%s plays: %s.', player.name, action.combination)
            # Remove the player from the set of passing players, if necessary
            try :
                self.passed.remove(player)
            except KeyError :
                pass
            # Check if the player is allowed to play this combo
            valid_play = self.check_valid_play(action.combination)
            if not valid_play :
                logger.game('Play invalid: %s', action.combination)
                return False
            else :
                self.played_combinations.append(action.combination)
                return True

        elif action.name == 'ragequit' :
            logger.game('%s ragequits.', player.name)
            self.trick_unplayable = True
            return True

    def check_valid_play(self, combination) :
        """ Verify that a played combination 
        i) matches the combo type of the starting player's combo
        ii) is higher than the previous play
        """
        # i) Check if the combination matches this trick's combo type
        if not self.check_combo_type(combination) : return False
        
        # ii) Check if the combination is higher than the current highest
        if not self.check_strength(combination) : return False

        return True

    def check_combo_type(self, combination) :
        """ Check if *combination* matches *self.combo_type*. Bombs can be 
        played on all other combinations except for higher bombs. If this is 
        the first combination played in this trick, just set the *combo_type*.
        """
        combo_type = combination.combo_type
        # If this is the first combination, set combo_type and exit
        if not self.combo_type :
            self.comby_type = combo_type
            return True
        # TODO Special cases for bombs
        elif combo_type in ['bomb', 'straight_bomb'] :
            return False
        elif combo_type == self.combo_type :
            return True
        else :
            return False

    def check_strength(self, combination) :
        """ Compare the strength of the played *combination* to the last played 
        one and return *True* if the new *combination* is stronger.
        """
        try :
            highest = self.played_combinations[-1]
        except IndexError :
            # If nothing has been played, any combo is good enough
            return True

        # Bombs are automatically covered as they get a higher rank internally
        logger.debug('%d > %d? %s', combination.rank, highest.rank, 
                     combination.rank>highest.rank)
        return combination.rank > highest.rank

    def rotate_players(self, n=1) :
        for i in range(n) :
            self.players.append(self.players.pop(0))

    def trick_finished(self) :
        """ Check whether this trick is over, which is the case if:
            1) All but the current *winning_player* passed or
            2) The game is over
        The dog is not counted as a separate trick but just implemented as a 
        change in player order.
        """
        return False or self.trick_unplayable

    def prompt_to_play(self, player) :
        """ Query the next action of the current player. """
        player.release_play_lock()
        query_interval = 0.03 #s
        while True :
            action = player.next_action
            if action is None :
                time.sleep(query_interval)
                continue
            # If an action was found lock the player and reset her 'next_action'
            player.close_play_lock()
            player.next_action = None
            return action
            

