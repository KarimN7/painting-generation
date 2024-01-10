from Colour_Painting import *
from collections import Counter
import copy
import pickle
import cv2
import os
from datetime import datetime
import argparse
import math
import random
import time

def simulatedannealing(painting, evaluations, filename):
    # Start overall timer
    overall_start_time = time.time()

    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    today = str(dt_string)

    # Create a folder for the current script run
    run_folder = f"output_dir/{filename}/{dt_string}"
    os.makedirs(run_folder, exist_ok=True)

    logger = f"{run_folder}/log-SA-{len(painting.strokes)}-{evaluations}-{today}"
    os.makedirs(os.path.dirname(logger), exist_ok=True)
    f = open(logger, "w")

    for evaluation in range(evaluations):
        mutated_strokes = painting.mutate()

        # Calculate the error of the mutated painting
        current_error, current_img = painting.calcError(mutated_strokes)

        # If the error is lower, accept the mutation
        if current_error < painting.current_error:
            painting.strokes = mutated_strokes
            painting.current_error = current_error
            painting.canvas_memory = current_img

            painting.current_best_error = current_error
            painting.current_best_canvas = current_img

            print(f"Generation: {evaluation} Accepted mutation with error {painting.current_error}")
            logwriter(f, evaluation, painting.current_error, analyzeStrokes(painting)[0], analyzeStrokes(painting)[1], 0)
            cv2.imwrite(f"{run_folder}/SA-best.png", painting.canvas_memory)
        elif current_error > painting.current_error:
            # Calculate the probability of accepting the mutation even if the error is higher
            probability = calculateProbability(painting.current_error, current_error, evaluation)
            if probability > random.random():
                painting.strokes = mutated_strokes
                painting.current_error = current_error
                painting.canvas_memory = current_img

                print(f"Generation: {evaluation} SA new error: {painting.current_error} with probability {probability}")
                logwriter(f, evaluation, painting.current_error, analyzeStrokes(painting)[0], analyzeStrokes(painting)[1], 1)
                cv2.imwrite(f"{run_folder}/SA-best.png", painting.canvas_memory)

        # Output painting every 1000 evaluations and the final evaluation
        if evaluation % 10 == 0 or evaluation == evaluations - 1:
            cv2.imwrite(f"{run_folder}/SA-{evaluation}.png", painting.canvas_memory)

    # Output final pickle file and image
    cv2.imwrite(f"{run_folder}/SA-final-{len(painting.strokes)}-{today}.png", painting.canvas_memory)
    pickle.dump(painting, open(f"{run_folder}/SA-final-{len(painting.strokes)}-{today}.pkl", "wb"))

    overall_end_time = time.time()
    print(f"Overall Time: {overall_end_time - overall_start_time} seconds")
    f.write(f"Overall Time: {overall_end_time - overall_start_time} seconds")
    # Close file handle
    f.close()
        



# Calculate probability using a cooling function
def calculateProbability(current_error, new_error, temperature):
    c = 1
    temp = c/(math.log(temperature+1))
    change = new_error - current_error
    probability = math.exp(-change/temp)
    return probability


def logwriter(f, evaluations, current_error, countedStrokes, averageStrokeSize, SA):
    # Add evaluations
    log = str(evaluations)
    log = log + "," + str(current_error)
    log = log + ", Brushes: " + str(countedStrokes[1]) + "," + str(countedStrokes[2]) + "," + str(countedStrokes[3]) + "," + str(countedStrokes[4])
    log = log + ", Average Stroke Size: " + str(averageStrokeSize)
    log = log + ", SA: " + str(SA)
    f.write(log + "\n")

def analyzeStrokes(individual):
    # Calculate the average stroke size
    strokeSizes = [stroke.size for stroke in individual.strokes]
    averageStrokeSize = sum(strokeSizes) / len(strokeSizes)
    
    # Stroke brush type used
    strokeTypes = []
    for stroke in individual.strokes:
        strokeTypes.append(stroke.brush_type)
    countedStrokes = Counter(strokeTypes)

    return countedStrokes, averageStrokeSize

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('argfilename', metavar='N', nargs='+', help='painting name')
    args = parser.parse_args()

    filename = str(args.argfilename[0])
    imagePath = f"imgs/{filename}"

    # Setup parameters
    evaluations = 1000
    strokeCount = 25

    canvas = Painting(imagePath)
    canvas.init_strokes(strokeCount)

    simulatedannealing(canvas, evaluations, filename)