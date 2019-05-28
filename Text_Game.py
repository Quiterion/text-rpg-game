#!/usr/bin/python3

import random
import time
import json
import os

def printslow(text):
    # helper function for outputting text one character at a time
    print('')
    for char in text:
        print(char, end='')
        time.sleep(0.005)


class Character:

    def __init__(self, kwargs):
        """ class takes max_health, name """
        self._max_health = kwargs.get("max_health")
        self._current_health = kwargs.get("max_health")
        self._name = kwargs.get("name")

    def get_max_health(self):
        return self._max_health

    def change_max_health(self, amount):
        self._max_health += amount

    def get_health(self):
        return self._current_health

    def change_health(self, amount):
        if self._current_health + amount >= 0:
            if self._current_health + amount <= self._max_health:
                self._current_health += amount
            else:
                self._current_health += (self._max_health - self._current_health)
        else:
            self._current_health = 0

    def get_name(self):
        return self._name


class Monster(Character):

    def __init__(self, kwargs):
        """ class takes max_health, attack_damage, name """
        self._attack_damage = kwargs.get("attack_damage")
        self._dmgtype = kwargs.get("dmgtype")
        super().__init__(kwargs)

    def get_dmgtype(self):
        return self._dmgtype

    def get_attack_damage(self):
        return self._attack_damage


class Player(Character):

    def __init__(self, kwargs):
        """ class takes max_health, items, name, start_coords """
        self._items = [[x, 1] for x in list(kwargs.get("items"))]
        self._x = kwargs.get('start_coords')[0]
        self._y = kwargs.get('start_coords')[1]
        self._victory = False
        super().__init__(kwargs)

    def get_items(self):
        return self._items

    def add_item(self, item):
        if isinstance(item, Items):
            for x in self._items:
                if x[0] == item:
                    x[1] += 1
                    return
            self._items.append([item, 1])
        else:
            printslow("ERROR, " + str(item) + " is not an instance of the Items class")

    def remove_item(self, item):
        for x in self._items:
            if x[0] == item:
                x[1] -= 1
                if x[1] < 1:
                    self._items.remove(x)
                return
        printslow("ERROR, " + str(item) + " is not in self._items")

    def change_xy(self, delta_tupl):
        self._x += delta_tupl[0]
        self._y += delta_tupl[1]

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def has_won(self):
        return self._victory

    def change_win_state(self, state):
        self._victory = state


class Room:

    def __init__(self, kwargs):
        """ class takes effect_text, move_dict, location_text, after_text """
        self._visited = False
        self._effect_text = kwargs.get("effect_text")
        self._moves_dict = kwargs.get("moves_dict")
        self._location_text = kwargs.get("location_text")
        self._after_text = kwargs.get("after_text")

    def effect(self, player):
        if not self._visited:
            printslow(self._effect_text)
            self._visited = True
        else:
            printslow(self._after_text)

    def print_location(self, player):
        printslow(self._location_text)

    def get_moves(self):
        return self._moves_dict


class EnemyRoom(Room):

    def __init__(self, kwargs):
        """ class takes effect_text, enemy, move_dict, location_text, after_text, dmgtype """
        self._enemy = kwargs.get("enemy")
        super().__init__(kwargs)

    def effect(self, player):
        if not self._visited:
            printslow(self._effect_text)
            self._visited = True
            return fight(self._enemy, player)
        else:
            printslow(self._after_text)


class LootRoom(Room):

    def __init__(self, kwargs):
        """ class takes effect_text, item, quantity, move_dict, location_text, after_text """
        self._item = kwargs.get("item")
        self._quantity = kwargs.get("quantity")
        super().__init__(kwargs)

    def effect(self, player):
        if not self._visited:
            printslow(self._effect_text)
            for x in range(self._quantity):
                player.add_item(self._item)
            self._visited = True
            printslow("You picked an item: '" + self._item.get_name() + "'" if self._quantity == 1 else
                      "You picked up " + str(self._quantity) + " of the following: '" +  self._item.get_name() + "'")
        else:
            printslow(self._after_text)


class WinningRoom(Room):

    def __init__(self, kwargs):
        """ class takes effect_text, move_dict, location_text """
        super().__init__(kwargs)

    def effect(self, player):
        printslow(self._effect_text)
        player.change_win_state(True)


class WizardRoom(Room):

    def __init__(self, kwargs):
        """ class takes effect_text, move_dict, location_text, after_text, win_text, item, quantity """
        self._win_text = kwargs.get("win_text")
        self._item = kwargs.get("item")
        self._quantity = kwargs.get("quantity")
        self._keys = kwargs.get("keys")
        super().__init__(kwargs)

    def effect(self, player):
        if not self._visited:
            printslow(self._effect_text)
            for x in range(self._quantity):
                player.add_item(self._item)
            self._visited = True
            printslow("You picked an item! Item name: '" + self._item.get_name() + "'" if self._quantity == 1 else
                      "You picked up " + str(self._quantity) + " items! Item name: '" +  self._item.get_name() + "'")
        else:
            item_names = set([x[0].get_name() for x in player.get_items()])
            if set(self._keys).issubset(item_names):
                printslow(self._win_text)
                player.change_win_state(True)
            else:
                printslow(self._after_text)


class Items:

    def __init__(self, kwargs):
        """ class takes name, hpdelta, dmgtype, heal_bool, effect_text """
        self._name = kwargs.get("name")
        self._hpdelta = kwargs.get("hpdelta")
        self._dmgtype = kwargs.get("dmgtype")
        self._heal_bool = kwargs.get("heal_bool")
        self._effect_text = kwargs.get("effect_text")

    def get_name(self):
        return self._name

    def get_hpdelta(self):
        return self._hpdelta

    def get_dmgtype(self):
        return self._dmgtype

    def get_healbool(self):
        return self._heal_bool

    def get_effect_text(self):
        return self._effect_text

    def action(self, player):
        if self._heal_bool:
            printslow(self._effect_text)
            player.change_health(self._hpdelta)
            printslow("Your new health is: " + str(player.get_health()) + ' HP (max HP)' if \
            player.get_health() == player.get_max_health() else \
            "Your new health is: " + str(player.get_health() + ' HP'))
            player.remove_item(self)


def attack(monster, player, item):
    printslow("The " + monster.get_name() + " has health: " + str(monster.get_health()))
    printslow("You attack the " + monster.get_name() + " with: " + item.get_name())
    if (item.get_dmgtype() == monster.get_dmgtype()) and (item.get_dmgtype() != None):
        roll = 1000
        printslow("You damage the " + monster.get_name() + " by " + str(roll) + " HP")
        printslow(item.get_effect_text())
    else:
        roll = random.randrange(1, item.get_hpdelta() + 1)
        if not roll == 0:
            printslow("You damage the " + monster.get_name() + " by " + str(roll) + " HP")
        else:
            printslow("You missed!")
    monster.change_health(-roll)
    printslow("The " + monster.get_name() + " has health: " + str(monster.get_health()))
    if monster.get_health() > 0:
        return False
    return True


def attacked(monster, player):
    printslow("\nYou have health: " + str(player.get_health()))
    printslow("The " + monster.get_name() + " attacks you.")
    roll = random.randrange(monster.get_attack_damage() + 1)
    if not roll == 0:
        printslow("The " + monster.get_name() + " damages you by " + str(roll) + " HP")
    else:
        printslow("The " + monster.get_name() + " missed!")
    player.change_health(-roll)
    printslow("You have health: " + str(player.get_health()))
    if player.get_health() > 0:
        return False
    return True


def fight(monster, player):
    printslow("A wild " + monster.get_name() + " appears!")
    printslow("==================== Fight ====================")
    while True:
        while True:

            items_str = ''
            for item_lst in player.get_items():
                items_str += "'" + item_lst[0].get_name()
                if item_lst[1] != 1:
                    items_str += ' (x' + str(item_lst[1]) + ')'
                items_str += "', "
            printslow("Select one item:\n" + items_str[:-2] + "\n")

            inp = input("> ")
            if inp in [str(i) for  i in range(1, len(player.get_items())+1)]:
                item = player.get_items()[int(inp)-1][0]
                break
            item = get_obj(inp, player)
            if item:
                break

        if item.get_healbool():
            item.action(player)
        elif attack(monster, player, item):
            printslow("You have the defeated the " + monster.get_name() + "!")
            return

        if attacked(monster, player):
            printslow("Your vision fades to black, and you feel only a dull thud as your head hits the floor.")
            printslow("\nYou died!")
            return
        printslow("The " + monster.get_name() + " is still alive!")


def get_obj(name, player):
    # helper function that takes an item's name and returns its corresponding object
    # note that items should always be named uniquely
    for item_tupl in player.get_items():
        if item_tupl[0].get_name() == name:
            return item_tupl[0]
    else:
        return False


def get_available_moves(room, player, gmap):
    # helper function that takes a room's move list and returns the legal moves
    # in a command-friendly (func, args) format.
    moves = {}
    for name, delta in room.get_moves().items():
         if gmap.get((player.get_x() + delta[0], player.get_y() + delta[1])):
            moves[name] = (player.change_xy, (delta[0], delta[1]))
    return moves


def load_world(var_name, vals):
    # recursive helper function that takes class kwargs and converts them into objects
    translate = {"monster_obj":Monster, "item_obj":Items, "basic_room":Room,
    "enemy_room":EnemyRoom, "loot_room":LootRoom, "win_room":WinningRoom,
    "wizard_room":WizardRoom}

    class_type = translate[vals["type"]]
    params_clone = dict(vals["params"])
    for key, args in vals["params"].items():
        if type(args) == type({}) and (key == "item" or key == "enemy"):
            arg2 = load_world(key, args)
            params_clone[key] = arg2
    return class_type(params_clone)


def play(devmode=False):

    while True:

        print(
"""

 .d8b.  d8888b. db    db d88888b d8b   db d888888b db    db d8888b. d88888b       .d88b.  db    db d88888b .d8888. d888888b
d8' `8b 88  `8D 88    88 88'     888o  88 `~~88~~' 88    88 88  `8D 88'          .8P  Y8. 88    88 88'     88'  YP `~~88~~'
88ooo88 88   88 Y8    8P 88ooooo 88V8o 88    88    88    88 88oobY' 88ooooo      88    88 88    88 88ooooo `8bo.      88
88~~~88 88   88 `8b  d8' 88~~~~~ 88 V8o88    88    88    88 88`8b   88~~~~~      88    88 88    88 88~~~~~   `Y8b.    88
88   88 88  .8D  `8bd8'  88.     88  V888    88    88b  d88 88 `88. 88.          `8P  d8' 88b  d88 88.     db   8D    88
YP   YP Y8888D'    YP    Y88888P VP   V8P    YP    ~Y8888P' 88   YD Y88888P       `Y88'Y8 ~Y8888P' Y88888P `8888Y'    YP

"""
        )

        intro_text = "A Text-Based Adventure Game by <author>\n(c) 2019 - See GPLv3 license for details\n\n\
==============================================\nPlease select one of the following questlines by name:\n"
        worlds_list = []
        for file in os.scandir('worlds/'):
            filename = os.path.basename(file).split('.')[0]
            if filename == "formats":
                continue  # ignore formats file
            worlds_list.append(filename)

        worlds_text = ''
        for filename in worlds_list:
             worlds_text += "'" + filename + "', "
        worlds_text = worlds_text[:-2]
        printslow(intro_text + worlds_text + '\n')

        while True:
            inp = input('> ')
            if inp in worlds_list:
                break
            printslow("Please select one of the following questlines:\n" + worlds_text + "\n")

        config = json.loads(open('worlds/'+inp+'.json', 'r').read())
        gmap = {}
        for key, val in config.items():
            gmap[tuple(val["coords"])] = load_world(key, val)

        printslow("Game loaded succesfully!\n")
        coords = [0, 0]

        if devmode:
            while True:
                printslow("Please enter start coordinates in the form x,y (default is 0,0)\n")
                coords = input('> ').split(',')
                try:
                    coords = [int(x) for x in coords]
                    assert len(coords) == 2
                    assert gmap.get((coords[0], coords[1])) != None
                    printslow("Coordinates loaded succesfully! Please note that some items and changes from previous game states may be inaccessible.\n\n")
                    break
                except:
                    printslow("Error: invalid coordinates")

        p = Player({"max_health":10, "items":[
        Items({"name":"fists", "hpdelta":3, "dmgtype":None, "heal_bool":False, "effect_text":None})
                                ], "name":"Player", "start_coords":(coords[0], coords[1])})

        while True:

            current_room = gmap.get((p.get_x(), p.get_y()))
            current_room.effect(p)

            if p.get_health() > 0 and not p.has_won():
                while True:

                    inv_str = ""
                    possible_actions = {}
                    for item_lst in p.get_items():  # contruct inventory string each time the game state changes
                        inv_str += "item: " + item_lst[0].get_name() + ", quantity: " + str(item_lst[1])
                        inv_str += ', max damage: ' + str(item_lst[0].get_hpdelta()) + ' HP' if item_lst[0].get_healbool() == False else \
                        ', heal effect: ' + str(item_lst[0].get_hpdelta()) + ' HP'
                        inv_str += '\n'
                    possible_actions["look around"] = (current_room.print_location, p)
                    if p.get_health() == p.get_max_health():
                        possible_actions["check health"] = (printslow, "Your health is: " + str(p.get_health()) + " HP (max health)")
                    else:
                        possible_actions["check health"] = (printslow, "Your health is: " + str(p.get_health()) + " HP")
                    possible_actions["check inventory"] = (printslow, "Inventory for "+p.get_name()+":\n" + inv_str)
                    possible_actions.update(get_available_moves(current_room, p, gmap))
                    for item_lst in p.get_items():
                        if item_lst[0].get_healbool():
                            key = "consume " + item_lst[0].get_name()
                            possible_actions[key] = (item_lst[0].action, p)

                    pa_words = ''
                    pa_list = list(possible_actions.keys())
                    for k in pa_list:
                        pa_words += "'" + k + "', "

                    if devmode:
                        printslow("Current game coords: " + str(p.get_x()) + ',' + str(p.get_y()))

                    printslow("You can perform the following actions:\n" + pa_words[:-2] + "\n")

                    inp = input("> ")
                    if inp in possible_actions or inp in [str(i) for i in range(1, len(possible_actions)+1)]:
                        if inp in possible_actions:
                            func, args = possible_actions[inp][0], possible_actions[inp][1]
                        else:
                            func, args = possible_actions[pa_list[int(inp)-1]][0], possible_actions[pa_list[int(inp)-1]][1]
                        func(args)
                        if func == p.change_xy:
                            break
            else:
                while True:
                    printslow("Would you like to play again? You may select a different questline.\nPossible actions (please select by name):\n'yes', 'no'\n")
                    inp = input("> ")
                    if inp in ['yes', 'no']:
                        break

                if inp == 'yes':
                    break
                if inp == 'no':
                    printslow("Thank you for playing!")
                    exit()


if __name__ == "__main__":
    play()
