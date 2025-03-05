import requests
import networkx as nx
import matplotlib.pyplot as plt
import os
from queue import PriorityQueue
import random
# Define word lists
beginner_words = ["cat", "dog", "sun", "car", "hat", "run", "top", "cup", "pen", "box"]
advanced_words = ["stone", "money", "apple", "happy", "beach", "green", "music", "water", "night", "light"]
challenge_words = ["paddle","bottle","cuddle","fiddle","rattle","toggle","handle","baffle","hurdle","doodle"]
banned_words = ["jumble","bundle","tangle","muddle","wobble","ripple","guzzle"]
restricted_letters = ['w', 'z']  

dict_source = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
local_file = "words_dictionary.txt"

MOVE_LIMIT = 20
ChallengeMode=False

# Function to load the word list from GitHub 
def load_words():
    if not os.path.exists(local_file):  
        print("Getting words list from GitHub")
        response = requests.get(dict_source)  
        if response.status_code == 200:  
            with open(local_file, "w", encoding="utf-8") as file:
                file.write(response.text)  
            print(f"Word list saved to {local_file}.")
        else:
            print("Failed to fetch dictionary from github")  
            exit()
    else:
        print("Using local word list file i.e words_dictionary.txt")  
    with open(local_file, "r", encoding="utf-8") as file:
        return set(file.read().splitlines())  

english_words = load_words()

# Node class to represent each word in the graph
class Node:
    def __init__(self, state, parent=None, g_cost=0, h_cost=0):
        self.state = state  
        self.parent = parent  
        self.g_cost = g_cost  
        self.h_cost = h_cost  
        self.f_cost = g_cost + h_cost  

    def __lt__(self, other):
        return self.f_cost < other.f_cost  


def heuristic(word, end):
    return sum(1 for a, b in zip(word, end) if a != b)

# Function to get all valid neighbors of a word (one letter apart)
def get_neighbor_words(word):
    neighbors_words = []
    for i in range(len(word)):  
        for j in range(97, 123):  
            if chr(j) != word[i]:  
                new_word = word[:i] + chr(j) + word[i + 1:]
                if new_word in english_words:  
                    neighbors_words.append(new_word)
    return neighbors_words

# A* algorithm to find the shortest path from start to end
def astar(start, end):
    open_set = PriorityQueue()  
    start_node = Node(start, g_cost=0, h_cost=heuristic(start, end))  
    open_set.put(start_node)  

    visited = set()  
    graph = {}  
    nx_graph = nx.Graph()  

    while not open_set.empty():
        current_node = open_set.get()  
        current_word = current_node.state

        if current_word == end:  
            path = []
            while current_node:  
                path.append(current_node.state)
                current_node = current_node.parent
            return path[::-1], graph, nx_graph  

        if current_word in visited:  
            continue
        visited.add(current_word)  

        graph[current_word] = current_node
        nx_graph.add_node(current_word)

        for neighbor in get_neighbor_words(current_word):
            if neighbor not in visited:
                g_cost = current_node.g_cost + 1  
                h_cost = heuristic(neighbor, end)  
                neighbor_node = Node(neighbor, parent=current_node, g_cost=g_cost, h_cost=h_cost)
                open_set.put(neighbor_node)  

                nx_graph.add_edge(current_word, neighbor)

    return None, graph, nx_graph  

def gbfs(start, end):
    open_set = PriorityQueue()
    start_node = Node(start, h_cost=heuristic(start, end))  
    open_set.put((start_node.h_cost, start_node))  

    visited = set()  
    graph = {}  
    nx_graph = nx.Graph()  

    while not open_set.empty():
        _, current_node = open_set.get()  
        current_word = current_node.state


        if current_word == end: 
            path = []
            while current_node:  
                path.append(current_node.state)
                current_node = current_node.parent
            return path[::-1], graph, nx_graph  

        if current_word in visited:  
            continue
        visited.add(current_word)  

        graph[current_word] = current_node
        nx_graph.add_node(current_word)

        for neighbor in get_neighbor_words(current_word):
            if neighbor not in visited:
                h_cost = heuristic(neighbor, end)  
                neighbor_node = Node(neighbor, parent=current_node, h_cost=h_cost)
                open_set.put((neighbor_node.h_cost, neighbor_node))  

                nx_graph.add_edge(current_word, neighbor)

    return None, graph, nx_graph  

# Uniform Cost Search (UCS) algorithm
def ucs(start, end):
    open_set = PriorityQueue()  
    start_node = Node(start, g_cost=0)  
    open_set.put((start_node.g_cost, start_node))  

    visited = set()  
    graph = {}  
    nx_graph = nx.Graph()  

    while not open_set.empty():
        _, current_node = open_set.get()  
        current_word = current_node.state


        if current_word == end:  
            path = []
            while current_node:  
                path.append(current_node.state)
                current_node = current_node.parent
            return path[::-1], graph, nx_graph

        if current_word in visited:  
            continue
        visited.add(current_word)  

        graph[current_word] = current_node
        nx_graph.add_node(current_word)

        for neighbor in get_neighbor_words(current_word):
            if neighbor not in visited:
                g_cost = current_node.g_cost + 1
                neighbor_node = Node(neighbor, parent=current_node, g_cost=g_cost)
                open_set.put((neighbor_node.g_cost, neighbor_node))  

                nx_graph.add_edge(current_word, neighbor)
    return None, graph, nx_graph  

# Function to select two different random words from a list
def select_random_words(word_list):
    start, end = random.sample(word_list, 2)
    return start, end

# Predefined challenge selection
def predefined_challenge():
    global MOVE_LIMIT,ChallengeMode
    print("\nSelect Difficulty Level:")
    print("1. Beginner Mode")
    print("2. Advanced Mode")
    print("3. Challenge Mode")

    difficulty = input("Enter 1, 2, or 3: ").strip()

    if difficulty == "1":
        MOVE_LIMIT=10
        start, end = select_random_words(beginner_words)
        
    elif difficulty == "2":
        MOVE_LIMIT=15
        start, end = select_random_words(advanced_words)
        
    elif difficulty == "3":
        ChallengeMode = True
        MOVE_LIMIT=20
        start, end = select_random_words(challenge_words)
        while end in banned_words and start in banned_words:
            start, end = select_random_words(challenge_words)
    else:
        print("Invalid choice. Please enter 1, 2, or 3....")
        return predefined_challenge()

    print(f"\nYour challenge: Transform '{start}' to '{end}'")
    return start, end

def visualize_graph(graph, path=None, title="Word Transformation Graph", highlight_user_path=False):
    plt.figure(figsize=(18, 12)) 
    
    if highlight_user_path:
        G = nx.Graph()
        path_edges = []

        for i in range(len(graph) - 1):
            G.add_edge(graph[i], graph[i + 1])
            path_edges.append((graph[i], graph[i + 1]))

        for word in graph:
            neighbors = get_neighbor_words(word)
            for neighbor in neighbors:
                if neighbor in english_words:
                    G.add_edge(word, neighbor)

        pos = nx.kamada_kawai_layout(G)  

        node_colors = ["lightblue" if node in graph else "lightgray" for node in G.nodes]
        node_sizes = [800 if node in graph else 300 for node in G.nodes]  # Larger nodes for path

        nx.draw(G, pos, with_labels=False, node_color=node_colors, edge_color="gray",
                font_size=10, node_size=node_sizes, alpha=0.6, width=0.5)

        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color="red", width=2)

        labels = {node: node for node in G.nodes}  
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight="bold", alpha=0.8)
    
    else:
        G = graph  
        pos = nx.fruchterman_reingold_layout(G, k=0.7)  

        nx.draw(G, pos, with_labels=False, node_color="lightgray", edge_color="gray",
                font_size=10, node_size=300, alpha=0.5, width=0.3)

        if path:
            path_edges = list(zip(path, path[1:]))
            nx.draw(G, pos, nodelist=path, node_color="lightblue", edge_color="red",
                    edgelist=path_edges, width=2, node_size=800)

            labels = {node: node for node in G.nodes}
            nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight="bold", alpha=0.8)

    plt.title(title, fontsize=16, fontweight="bold")
    plt.axis("off")  
    plt.show()


# Custom word ladder challenge
def custom_word_ladder():
    while True:
        start = input("\nEnter the starting word: ").strip().lower()
        end = input("Enter the ending word: ").strip().lower()
        if start in english_words and end in english_words:
            break
        print("Invalid word or words entered. Please try again")
    print(f"\nYour custom challenge: Transform '{start}' to '{end}'")
    return start, end


# Main menu function
def main_menu():
    print("Welcome to Word Ladder Adventure!")

    print("\nMain Menu:")
    print("1. Start Game")
    print("2. Exit")

    choice = input("Enter your choice: ").strip()

    if choice == "1":
        game_mode()
    elif choice == "2":
        print("Exiting the game. Goodbye....")
        exit()
    else:
        print("Invalid choice. Please enter 1 or 2.")
        main_menu()
        
def game_mode():
    print("\nChoose Game Mode:")
    print("1. Predefined Word Ladder Challenge")
    print("2. Custom Word Ladder")

    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        start, end = predefined_challenge()
    elif choice == "2":
        start, end = custom_word_ladder()
    else:
        print("Invalid choice. Please enter 1 or 2.")
        return game_mode()

    print(f"Solving Word Ladder from '{start}' to '{end}'...")  

    score = 1000
    user_path = [start]  
    moves_taken = 0  

    while start != end:
        if moves_taken == MOVE_LIMIT:
            print("No more moves available. You lose!")
            return score
        print(f"\nCurrent word: {start}")
        print(f"Goal Word : {end}")
        print(f"Moves remaining: {MOVE_LIMIT - moves_taken}")  
        print("1. Transform the word")
        print("2. Get AI hint")
        print("3. Visualize Graph")
        choice = input("Enter 1, 2, or 3: ").strip()
        
        if choice == "1":
            print("Enter the word to transform:")
            
            new_word = input().strip().lower()
            if ChallengeMode:
                if new_word in banned_words or any(letter in new_word for letter in restricted_letters):
                    print("Invalid transformation. Word not allowed (banned word or restricted letters in word)")
                    continue

            if len(new_word) != len(start):
                print("Length of the new word should be the same as the current word.")
                continue
            diff = 0
            for i in range(len(start)):
                if start[i] != new_word[i]:
                    diff += 1
                    if diff > 1:
                        break
            if diff != 1:
                print("New word must differ by exactly one character.")
                continue
            if new_word not in get_neighbor_words(start):
                print("Invalid transformation. No such word in Dictionary.")
                continue
            start = new_word
            user_path.append(start)  
            moves_taken += 1  
            score -= 10  
        elif choice == "2":
            print("\nChoose an algorithm:")
            print("1. A* (A-Star)")
            print("2. GBFS (Greedy Best-First Search)")
            print("3. UCS (Uniform Cost Search)")
            ai_choice = input("Enter 1, 2, or 3: ").strip()
            if ai_choice == "1":
                astar_path, astar_graph, astar_nx_graph = astar(start, end)
                if astar_path and len(astar_path) > 1:
                    next_word = astar_path[1]
                    print(f"Suggested next word (A*): {next_word}")
                    moves_taken -= 1 
                else:
                    print("No valid next word found.")
            elif ai_choice == "2":
                gbfs_path, gbfs_graph, gbfs_nx_graph = gbfs(start, end)
                if gbfs_path and len(gbfs_path) > 1:
                    next_word = gbfs_path[1]
                    print(f"Suggested next word (GBFS): {next_word}")
                    moves_taken -= 1
                else:
                    print("No valid next word found.")
            elif ai_choice == "3":
                ucs_path, ucs_graph, ucs_nx_graph = ucs(start, end)
                if ucs_path and len(ucs_path) > 1:
                    next_word = ucs_path[1]
                    print(f"Suggested next word (UCS): {next_word}")
                    moves_taken -= 1
                else:
                    print("No valid next word found.")
            else:
                print("Invalid choice. Please try again.")
                continue
        elif choice == "3":
            # Visualize the graph
            print("\nChoose an algorithm to visualize:")
            print("1. A* (A-Star)")
            print("2. GBFS (Greedy Best-First Search)")
            print("3. UCS (Uniform Cost Search)")
            algo_choice = input("Enter 1, 2, or 3: ").strip()
            if algo_choice == "1":
                if 'astar_nx_graph' in locals():
                    visualize_graph(astar_nx_graph, astar_path, "Word Transformation Graph (A*)")
                else:
                    print("No A* graph available. Please request an A* hint first.")
            elif algo_choice == "2":
                if 'gbfs_nx_graph' in locals():
                    visualize_graph(gbfs_nx_graph, gbfs_path, "Word Transformation Graph (GBFS)")
                else:
                    print("No GBFS graph available. Please request a GBFS hint first.")
            elif algo_choice == "3":
                if 'ucs_nx_graph' in locals():
                    visualize_graph(ucs_nx_graph, ucs_path, "Word Transformation Graph (UCS)")
                else:
                    print("No UCS graph available. Please request a UCS hint first.")
            else:
                print("Invalid choice. Please enter 1,2 or 3.")
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

    print("Congratulations! You have reached the goal word.")
    print(f"Final score: {score} points")  

    print("\nTransformation path:")
    print(" -> ".join(user_path))

    visualize_graph(user_path, title="User's Word Ladder Path with Possible Neighbors", highlight_user_path=True)
    exit()

if __name__ == "__main__":
    main_menu()
    
