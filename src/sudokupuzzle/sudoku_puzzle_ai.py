'''
This Python program solves Sudoku puzzles using two different algorithms:
    -Back-Tracking algorithm
    -Forward-Checking algorithm with heuristics.

Created on Feb. 9, 2019

@author: Dylan Calado
'''
import copy
import os
import sys
import timeit

#Initialize the global variables.
initial_puzzle_state = list()
puzzle = list()
counter = 0
nodes_visited = 0
time_initial = 0
time_final = 0

#Prints the main menu.
def print_menu():
    print("""\n---------Sudoku Puzzle Solver: Main Menu---------      
\n1. Solve Sudoku using Back-Tracking Algorithm
2. Solve Sudoku using Forward-Checking Algorithm
3. Terminate Program\n""")


#Main user interface logic.
def execute_program_loop():
    global puzzle, time_initial, time_final, nodes_visited
        
    while True:
        print_menu()
        nodes_visited = 0
        selected_option = input("Enter an option (1-3): ")
        
        
        if selected_option == "1":
                read_input_file()
                time_initial = timeit.default_timer()
                if back_tracking_algorithm(0, 0):
                    time_final = timeit.default_timer()
                    output_results_to_console()
                else:
                    print("\nPuzzle is unsolvable.")
             
             
        elif selected_option == "2":
                read_input_file()
                time_initial = timeit.default_timer()
                if forward_checking_algorithm():
                    time_final = timeit.default_timer()
                    output_results_to_console()
                else:
                    print("\nPuzzle is unsolvable.")
         
         
        elif selected_option == "3":
            
            choice = input("""\nTerminating the program will empty the 'Puzzle Solutions' folder.
\nType y to terminate or hit Enter to go back to the main menu: """)
            
            if choice == "y":
                
                #Clears the "puzzle solutions" folder on exit to keep things organized.
                filelist = [f for f in os.listdir(os.path.join(sys.path[0], "Puzzle Solutions (Program Output)"))]
                for f in filelist:
                    os.remove(os.path.join(os.path.join(sys.path[0], "Puzzle Solutions (Program Output)"), f))
                
                print("\n***Program Terminated***")
                
                sys.exit(0)


        else:
            print("Error: Invalid Input. You can only select option (1-3).")

#Allows the user to select a text file containing the puzzle data and also checks if the data is valid.     
def read_input_file():
    global puzzle, initial_puzzle_state
    
    filename = input("Enter name of a valid puzzle file (e.g. puzzle7.txt): ")
    
    if os.path.exists(os.path.join(sys.path[0], filename)): 

        with open(os.path.join(sys.path[0], filename), "r") as input_file:
            initial_puzzle_state = [[int(data) for data in row if data.strip()] for row in input_file]
            puzzle = copy.deepcopy(initial_puzzle_state)
            
        #Checks several conditions to make sure initial state is proper size.
        #9x9 Sudoku board = 81 numbers. 
        valid_initial_state = True
        if sum(len(x) for x in puzzle) != 81:
            valid_initial_state = False 
        
        if valid_initial_state:
            print("\nSaving initial state selected as:\n")
            print_puzzle(initial_puzzle_state)
        else:
            print("\nThe file selected contains invalid data for Sudoku.")
            read_input_file() 
    else:
        print("\nInput Error: You must select a valid Sudoku text file.")
        read_input_file() 
     
#Solves a Sudoku puzzle using a back-tracking algorithm.  
def back_tracking_algorithm(x_coord, y_coord):
    global puzzle, nodes_visited
    
    x_coord, y_coord = get_next_unassigned_cell(x_coord, y_coord)
    
    #The puzzle is solved.
    if x_coord == None and y_coord == None:
        return True
        
    #Iterates through numbers 1 to 9 and checks if any are valid moves.
    #If the number is valid, it gets placed in that location on the puzzle board and 
    #the process repeats for the next empty cell.
    for num in range(1,10):
        if is_valid_choice(num, x_coord, y_coord):
            puzzle[x_coord][y_coord] = num
            
            if back_tracking_algorithm(x_coord, y_coord):
                return True
            
            #If no valid moves exist for the current variable, we need to back track to the last valid state.
            #This is where we increment our visited_node counter.
            puzzle[x_coord][y_coord] = 0
            nodes_visited = nodes_visited + 1
    return False

#Returns the coordinates of the next empty cell found in the puzzle.
def get_next_unassigned_cell(i, j, is_last_cell=True):
    global puzzle
    
    #Iterates through the puzzle to find the coordinates of the next empty cell.
    for x in range(i,9):
        for y in range(j,9):
            if puzzle[x][y] == 0:
                return x,y
                        
    #Start at the first cell once the last cell is reached.                 
    if is_last_cell:
        return get_next_unassigned_cell(0, 0, False)

    #If there are no more empty cells, return None.
    return None, None

#Checks if target move is allowed.
def is_valid_choice(move, i, j):
    global puzzle
    
    #Use the "all" function to make sure that the proposed choice is not in the row or column yet.
    #Returns false if the choice is already in a row or column (i.e. the move is invalid).
    if all([move != puzzle[i][x] for x in range(9)]):                
        if all([move != puzzle[x][j] for x in range(9)]): 
            
            #Variables used to iterate through the sub squares that contain the i,j cell.
            sub_box_x_val = (3 * int(i // 3))
            sub_box_y_val = (3 * int(j // 3))
            
            #Checks if the proposed choice is already in the sub square.
            #If not, the choice is a valid move.                  
            for x in range(sub_box_x_val, sub_box_x_val + 3):
                for y in range(sub_box_y_val, sub_box_y_val + 3):
                    if puzzle[x][y] == move:
                        return False
            
            return True
    return False

#Solves a Sudoku puzzle using the forward-checking algorithm
#with Minimum Remaining Values heuristic.  
def forward_checking_algorithm():
    global puzzle, nodes_visited
    
    possible_values = []
    acquired_possible_values = False
    
    #Maintain a list of the legal values that each cell can have given the numbers
    #already on the board.
    for x_coord in range(0,9):
        for y_coord in range(0,9):
            if puzzle[x_coord][y_coord] == 0:
                empty_cell_locations = []
                empty_cell_locations.append([x_coord, y_coord])
                candidate_values = []
                
                for num in range(1,10):
                    if is_valid_choice(num, x_coord, y_coord):
                        candidate_values.append(num)
                        
                empty_cell_locations.append(len(candidate_values))
                possible_values.append(empty_cell_locations)
                acquired_possible_values = True
    
    #If there are no more empty cells, the puzzle is solved.
    if not acquired_possible_values:
        return True


    most_constrained_variable = possible_values[0][0]

    #Minimum Remaining Values current variable.
    mrv_current = possible_values[0][1]
    
    for i in range(0,len(possible_values)):
        
        #Iterate through the list of possible values generated from the above code.
        #Choose the cell with the least number of possible values (MRV heuristic).
        if possible_values[i][1] < mrv_current:
            mrv_current = possible_values[i][1]
            most_constrained_variable = possible_values[i][0]
    
    #We calculated the most constrained variable. Assign it to coordinate variables.
    x_coord = most_constrained_variable[0]
    y_coord = most_constrained_variable[1]
    
    for num in range(1,10):
        if is_valid_choice(num, x_coord, y_coord):
            puzzle[x_coord][y_coord] = num
            if forward_checking_algorithm():
                return True
            
            #If no valid moves exist for the current variable, we need to back track
            #to the last valid state.
            puzzle[x_coord][y_coord] = 0
            nodes_visited = nodes_visited + 1
    return False

#Prints the puzzle list as a Sudoku board for display.
def print_puzzle(puzzle): 
    for i in range(9):
        if (i) % 3 == 0 and i != 0:
            print("------+-------+------")
        for j in range(9):
            print(puzzle[i][j], end = " ")
            if (j+1) % 3 == 0 and j != 8:
                print("|", end = " ") 
        print(" ")

#Writes solved puzzles to a solutions file.
def write_solution_to_file():
    global counter
    
    #Keeps count of how many output files have been created (used for file naming purposes).
    counter = counter + 1
    with open(os.path.join(sys.path[0], "Puzzle Solutions (Program Output)\output for last executed puzzle(" + str(counter) + ").txt"), "w") as output_file:
        output_file.truncate(0)

        for i in range(9):
            if (i) % 3 == 0 and i != 0:
                output_file.write("------+-------+------\n")
            for j in range(9):
                output_file.write(str(puzzle[i][j]) + " ")
                if (j+1) % 3 == 0 and j != 8:
                    output_file.write("| ")
            output_file.write("\n")

#Writes the results to the console and to a file.
def output_results_to_console():
    global puzzle, time_initial, time_final, nodes_visited
    
    print("\nPuzzle solved! The solution is:\n")
    print_puzzle(puzzle)
    
    print("\nClock Time: " + str(format(time_final - time_initial, '.9f')) + " seconds")
    print("\nTotal Nodes Visited: ", nodes_visited)
    
    write_solution_to_file()
        
#Begin running the program by calling the execute_program_loop() function.
if __name__ == "__main__":
    execute_program_loop()
        

