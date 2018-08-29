""" Abstraction of a full game of Tichu, consisting of several rounds. """

import time

class Game() :
    pass

class Round() :
    pass

class Trick() :
    combo_type = None
    played = []

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

    def start_trickloop(self) :
        while not self.trick_finished() :
            player = self.players[0]

            action = self.prompt_to_play(player)

            if action.name == 'pass' :
                print(player.name + ' passes.')
            elif action.name == 'play' :
                print(player.name + ' plays: ')
                print(action.combination)
            elif action.name == 'ragequit' :
                print(player.name + ' ragequits.')
                break

            # Rotate to the next player
            self.rotate_players()

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
        return False

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
            

