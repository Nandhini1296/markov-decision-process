import time
import copy
import numpy as np

global directions


directions = [0,1,2,3]


def read_inputs():
    with open('input.txt') as input_file:
        inputs = [line.strip() for line in input_file.readlines()]
    #print inputs
    return inputs


def write_output(output_data):
    with open('output.txt', 'w') as f:
        for item in output_data:
            f.write("%s\n" % item)


def turn_left(move):
    if move == 3:
        return 2
    elif move == 2:
        return 1
    elif move == 1:
        return 0
    else:
        return 3


def turn_right(move):
    if move == 3:
        return 0
    elif move == 2:
        return 3
    elif move == 1:
        return 2
    else:
        return 1


def get_new_position(move, pos):

    x = pos[0]
    y = pos[1]

    if move == 0:
        if (x-1) < 0:
            return pos
        else:
            return (x - 1, y)

    if move == 1:
        if (y+1) > grid_size - 1:
            return pos
        else:
            return (x, y+1)

    if move == 2:
        if (x + 1) > grid_size - 1:
            return pos
        else:
            return (x+1, y)

    if move == 3:
        if (y-1) < 0:
            return pos
        else:
            return (x, y-1)


def get_possible_probablities(current_position, move):
    possible_probabilities = list()
    for direction in directions:
        new_position = get_new_position(direction, current_position)
        if direction == move:
            probability = 0.7
        else:
            probability = 0.1
        possible_probabilities.append((direction, new_position, probability))

    return possible_probabilities


def policy_evaluation(optimal_policy, final_position):
    # print "Optimal policy", optimal_policy
    # print "Utility matrix", utility_matrix
    utility_matrix = [[0.0 for x in range(grid_size)] for y in range(grid_size)]

    minimum_difference = 0.01111111

    while True:
        updated_utility_matrix = copy.deepcopy(utility_matrix)
        current_difference = 0.0
        for i in range(grid_size):
            for j in range(grid_size):
                utility_value = 0.0
                if (i,j) == final_position:
                    utility_value = 99
                else:
                    temp_list = get_possible_probablities([i, j], optimal_policy[i][j])
                    # print "Temp list", temp_list
                    for val in temp_list:
                        prob = val[2]
                        next_pos = val[1]
                        utility_value += prob * (cost_matrix[i][j] + (0.9 * updated_utility_matrix[next_pos[0]][next_pos[1]]))
                    #print "Utitlity value", utility_value
                utility_matrix[i][j] = utility_value
                current_difference = max(current_difference, abs(utility_value - updated_utility_matrix[i][j]))
        if minimum_difference > current_difference:
            break

    #print "Utilities", updated_utility_matrix
    return updated_utility_matrix


def policy_iteration(u_matrix, final_position):
    sample_policy_matrix = [[0 for x in range(grid_size)] for y in range(grid_size)]
    for i in range(grid_size):
        for j in range(grid_size):
            if (i,j) == final_position:
                continue
            find_action_states = [0,0,0,0]
            for val in range(4):
                temp_list = get_possible_probablities([i, j], val)
                for x in temp_list:
                    prob = x[2]
                    next_pos = x[1]
                    find_action_states[val] += prob * (cost_matrix[i][j] + (
                                0.9 * u_matrix[next_pos[0]][next_pos[1]]))
                    # print "Value", find_action_states[val]
            sample_policy_matrix[i][j] = find_action_states.index(max(find_action_states))
            # print "i,j,",i, j, "Find action states", find_action_states

    return sample_policy_matrix


def get_optimal_policy(final_position):
    optimal_policy = [[0 for x in range(grid_size)] for y in range(grid_size)]
    while True:
        updated_matrix = policy_evaluation(optimal_policy, final_position)
        generated_policy = policy_iteration(updated_matrix, final_position)
        if generated_policy == optimal_policy:
            break
        optimal_policy = generated_policy
    # print "Optimal Policy", optimal_policy
    return optimal_policy


if __name__ == "__main__":
    start = time.time()

    input = read_inputs()

    grid_size = int(input[0])
    cars = int(input[1])
    obstacles = int(input[2])
    o_locations= input[3:3+obstacles]
    car_init = input[3+obstacles:3+obstacles+cars]
    car_final = input[-cars:]

    obstacle_locations = []
    car_initial_positions = []
    car_final_positions = []

    for each_coordinate in o_locations:
        o = each_coordinate.split(",")
        obstacle_locations.append((int(o[1]), int(o[0])))

    #print obstacle_locations

    for each_coordinate in car_init:
        o = each_coordinate.split(",")
        car_initial_positions.append((int(o[1]), int(o[0])))

    #print car_initial_positions

    for each_coordinate in car_final:
        o = each_coordinate.split(",")
        car_final_positions.append((int(o[1]), int(o[0])))

    #print car_final_positions

    #create cost_matrix

    cost_matrix = [[-1 for x in range(grid_size)] for y in range(grid_size)]

    for tuple in obstacle_locations:
        x_coord = tuple[0]
        y_coord = tuple[1]
        cost_matrix[x_coord][y_coord] = -101

    #print('\n'.join(' '.join(map(str, sl)) for sl in cost_matrix))

    # N - 0 | E - 1 | S - 2 | W - 3

    optimal_policy = [[0 for x in range(grid_size)] for y in range(grid_size)]

    #random seed
    avg_list = []
    for i in range(cars):
        final_pos = car_final_positions[i]
        cost_matrix[final_pos[0]][final_pos[1]] = 99
        policy = get_optimal_policy(final_pos)
        score_list = []
        for j in range(10):
            score = 0
            pos = list(car_initial_positions[i])
            np.random.seed(j)
            swerve = np.random.random_sample(1000000)
            # print "Swerve", swerve
            k = 0
            while pos != car_final_positions[i]:
                move = policy[pos[0]][pos[1]]
                if swerve[k] > 0.7:
                    if swerve[k] > 0.8:
                        if swerve[k] > 0.9:
                            move = turn_right(turn_right(move))
                        else:
                            move = turn_right(move)
                    else:
                        move = turn_left(move)
                pos = get_new_position(move, pos)
                score += cost_matrix[pos[0]][pos[1]]
                k += 1

            score_list.append(score)

        cost_matrix[final_pos[0]][final_pos[1]] = -1

        avg_list.append(sum(score_list)/10)

    print "Average List", avg_list
    write_output(avg_list)
    print "Took", time.time() - start,"seconds to finish"