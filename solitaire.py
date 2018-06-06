import sys
import time
import copy
from termcolor import colored

class Game():
    def __init__(self):
        self.possible_moves = None
        self.table = {0:{'r':[],'h':[]},#       Tableau 1
                      1:{'r':[],'h':[]},#       Tableau 2
                      2:{'r':[],'h':[]},#       Tableau 3
                      3:{'r':[],'h':[]},#       Tableau 4
                      4:{'r':[],'h':[]},#       Tableau 5
                      5:{'r':[],'h':[]},#       Tableau 6
                      6:{'r':[],'h':[]},#       Tableau 7
                      7:[],8:[],9:[],10:[],#    Foundation
                      11:[],12:[]#              Stock and Waste
                     }
    def copy_game(self):
        return copy.deepcopy(self)
            
class Node():
    ''' Simple Node containing an instance of Game object for tree search, will add weights later '''
    def __init__(self, parent, children, game):
        self.parent = parent
        self.children = children
        self.game = game
        
class Play():
    ''' Klondike Solitaire '''
    def __init__(self):
        self.head = None
        self.tree_depth = None
        self.face_cards = ['T', 'J', 'Q', 'K']
        self.suites = {'1':'♠','2':'♢','3':'♣','4':'♡'}
    
    def setup(self, starting):
        g = Game()
        table_starting = starting[:56]
        stock = starting[56:]
        g.table[11] = [stock[i:i+2] for i in range(0, len(stock), 2)]
        for i in range(7):
            for j in range(i, 7):
                g.table[j]['h'].append(table_starting[:2])
                table_starting = table_starting[2:]
            g.table[i]['r'].append(g.table[i]['h'].pop())
        self.head = Node(None, None, g)
    
    def print_game(self, game):
        print(f"Stock: {self.map_to_print(game.table[11])}")
        print(f"Waste: {self.map_to_print(game.table[12])}")
        print(f"F1: {self.map_to_print(game.table[7])}")
#         print(colored('Hello, World!', 'red'))
        for i in range(7):
            print(f"{i}   {self.map_to_print(game.table[i]['h'])}   |  {self.map_to_print(game.table[i]['r'])}")
        print()
    
    # @TODO: print in reverse and add easier to read formatting (cards aligned)
    def map_to_print(self, cards):
        return ' '.join(list(map(lambda card: '[' + card[0] + self.suites[card[1]] + ']', cards)))
    
    def run_depth(self, depth):
        ''' Play the game to num depth '''        
        self.depth = depth
        self.make_tree(depth, self.head)
        self.print_tree()
    
    def make_tree(self, depth, current_node):
        ''' 🌲 '''
        if depth > 0:
            current_node.children = self.make_children(current_node)
            for child_node in current_node.children:
                self.make_tree(depth-1, child_node)
        
    def make_children(self, current_node):
        ''' 🌱 '''
        return [Node(current_node, None, self.do_move(current_node.game, move)) for move in self.get_possible_moves(current_node.game)]
              
    # This is fixed!
    def print_tree(self):
        depth_queue = []
        print("HEAD")
        self.print_game(self.head.game)
        depth_queue.append(self.head)
        for i in range(self.depth):
            print(f"DEPTH: {i+1}")
            next_queue = []
            for node in depth_queue:
                for child in node.children:
                    self.print_game(child.game)
                    next_queue.append(child)
            depth_queue = next_queue
    
    # Still need to check:
    #   - moving the King first to the foundation
    #   - move from foundation to tableau (only one card with normal rules)
    # Move => (from_card, to_card, num_cards)
    def get_possible_moves(self, game):
        moves = []
        # Move from waste to foundation or tableau
        if len(game.table[12]) > 0:
            for to_stack in range(7,11):
                move = self.check_foundation_move(game.table[12][-1], game.table[to_stack])
                if move is True:
                    moves.append((12, to_stack, 1))
            for to_stack in range(7):
                move = self.check_tableau_move(game.table[12][-1], game.table[to_stack]['r'][-1])
                if move is True:
                    moves.append((12, to_stack, 1))
        # Move from any pile to foundation
        for from_stack in range(7):
            if len(game.table[from_stack]['r']) > 0:
                for to_stack in range(7,11):
                    move = self.check_foundation_move(game.table[from_stack]['r'][-1], game.table[to_stack])
                    if move is True:
                        moves.append((from_stack, to_stack, 1))
        # Move from any pile to another
        for from_stack in range(7):
            for num_cards in range(len(game.table[from_stack]['r'])):
                for to_stack in range(7):
                    if to_stack == from_stack:
                        continue
                    move = self.check_tableau_move(game.table[from_stack]['r'][num_cards], game.table[to_stack]['r'][-1])
                    if move is True:
                        moves.append((from_stack, to_stack, num_cards+1))
        # Move from stock to waste
        if len(game.table[11]) > 0:
            moves.append((11,12,1))
        # Move from waste to stock
        else:
            moves.append((12,11,len(game.table[12])))
        return moves
    
    def check_tableau_move(self, from_card, to_card):
        if ((from_card[0] == 'Q' and to_card[0] == 'K') or (from_card[0] == 'J' and to_card[0] == 'Q') or
            (from_card[0] == 'T' and to_card[0] == 'J') or (from_card[0] == '9' and to_card[0] == 'T') or
            (from_card[0] not in self.face_cards and to_card[0] not in self.face_cards and int(from_card[0]) == int(to_card[0])-1)):
            if int(from_card[1]) % 2 != int(to_card[1]) % 2:
                return True
        return False
    
    def check_foundation_move(self, from_card, to_stack):
        if len(to_stack) == 0:
            if from_card[0] != 'K':
                return False
        to_card = to_stack[-1]
        if int(from_card[0]) == int(to_card[0])+1 and from_card[1] == to_card[1]:
            return True
        return False
    
    def do_move(self, game, move):
        g = game.copy_game()
        if move[0] == 11 and move[1] == 12:
            g.table[12].append(g.table[11].pop())
        elif move[0] == 12:
            if move[1] == 11:
                for i in range(len(g.table[12])):
                    g.table[11].append(g.table[12].pop())
            else:
                print(self.map_to_print(g.table[move[0]]))
                print(self.map_to_print(g.table[move[1]]['r']))
                g.table[move[1]]['r'].append(g.table[move[0]].pop())
        else:
            for i in range(move[2]):
                g.table[move[1]]['r'].append(g.table[move[0]]['r'].pop())
                # Flip cards over in tableau
                if len(g.table[move[0]]['r']) == 0 and len(g.table[move[0]]['h']) > 0:
                    g.table[move[0]]['r'].append(g.table[move[0]]['h'].pop())
        return g

if __name__ == '__main__':
    p = Play()
    p.setup('T412136463K3246282T2412143347214K1229394J28154K4T152113132K27392Q183J32342Q484715333T351J4Q2614491Q3J174')
    p.run_depth(7)

