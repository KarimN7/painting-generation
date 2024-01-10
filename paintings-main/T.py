from Colour_Painting import *
from collections import Counter
import copy
import pickle
import cv2
import os
from datetime import datetime
import argparse

def tabu_search(painting, evaluations, filename, tabu_size=10):
    overall_start_time = time.time()

    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    today = str(dt_string)

    run_folder = f"output_dir/{filename}/{dt_string}"
    os.makedirs(run_folder, exist_ok=True)

    logger = f"{run_folder}/log-Tabu-{len(painting.strokes)}-{evaluations}-{today}"
    os.makedirs(os.path.dirname(logger), exist_ok=True)
    f = open(logger, "w")

    # Initialize the tabu list
    tabu_list = []
    tabu_size = tabu_size
    max_tabu_size = 100

    for evaluation in range(evaluations):
        mutated_strokes = painting.mutate()

        # Calculate error
        calculated_error, calculated_canvas = painting.calcError(mutated_strokes)

        # Check if the mutated strokes are in the tabu list
        if mutated_strokes in tabu_list:
            continue

        # Add the mutated strokes to the tabu list
        tabu_list.append(mutated_strokes)

        # If the tabu list is full, remove the oldest strokes
        if len(tabu_list) > tabu_size:
            tabu_list.pop()
        
        # Adjust tabu tenure dynamically (change it to increment based on whether the error hasnt changed in x evaluations perhaps?)
        """if evaluation % 100 == 0 and evaluation != 0 and tabu_size < max_tabu_size:
            tabu_size += 1
            # The evaluation at which the tabu size is increased and the tabu size
            print(f"Tabu size increased at evaluation {evaluation} to {tabu_size}")"""

        # Output best individual when a new best is found
        if calculated_error < painting.current_error:
            painting.current_error = calculated_error
            painting.canvas_memory = calculated_canvas
            painting.strokes = mutated_strokes

            painting.current_best_error = calculated_error
            painting.current_best_canvas = calculated_canvas

            print(f"Evaluation {evaluation}: {painting.current_error}")
            logwriter(f, evaluation, painting.current_error, analyzeStrokes(painting)[0], analyzeStrokes(painting)[1])
            cv2.imwrite(f"{run_folder}/TabuSearch-best.png", painting.canvas_memory)
        
        # Output painting every 1000 evaluations and the final iteration
        if evaluation == 0 or evaluation == evaluations - 1 or (evaluation % 100 == 0 and evaluation != 0):
            cv2.imwrite(f"{run_folder}/TabuSearch-{evaluation}.png", painting.canvas_memory)

    # Output final image and pickle
    cv2.imwrite(f"{run_folder}/TabuSearch-final-{len(painting.strokes)}-{today}.png", painting.canvas_memory)
    pickle.dump(painting, open(f"{run_folder}/TabuSearch-final-{len(painting.strokes)}-{today}.pkl", "wb"))

    overall_end_time = time.time()
    print(f"Overall Time: {overall_end_time - overall_start_time} seconds")
    f.write(f"Overall Time: {overall_end_time - overall_start_time} seconds")
    # Close file handle
    f.close()


def logwriter(f, evaluations, current_error, countedStrokes, averageStrokeSize):
    # Add evaluations
    log = str(evaluations)
    log = log + "," + str(current_error)
    log = log + ", Brushes: " + str(countedStrokes[1]) + "," + str(countedStrokes[2]) + "," + str(countedStrokes[3]) + "," + str(countedStrokes[4])
    log = log + ", Average Stroke Size: " + str(averageStrokeSize)

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

    evaluations = 1000
    stroke_count = 25
    tabu_size = 50

    canvas = Painting(imagePath)
    canvas.init_strokes(stroke_count)

    tabu_search(canvas, evaluations, filename, tabu_size)