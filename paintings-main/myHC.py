from Colour_Painting import *
from collections import Counter
import copy
import pickle
import cv2
import os
from datetime import datetime
import argparse

def hillclimber(painting, evaluations, filename):
    # Start overall timer
    overall_start_time = time.time()

    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    today = str(dt_string)

    # Create a folder for the current script run
    run_folder = f"output_dir/{filename}/{dt_string}"
    os.makedirs(run_folder, exist_ok=True)

    logger = f"{run_folder}/log-HC-{len(painting.strokes)}-{evaluations}-{today}"
    os.makedirs(os.path.dirname(logger), exist_ok=True)
    f = open(logger, "w")

    for evaluation in range(evaluations):
        mutatedStrokes = painting.mutate()

        current_error, current_canvas = painting.calcError(mutatedStrokes)
       
        if current_error < painting.current_error:
            painting.current_error = current_error
            painting.canvas_memory = current_canvas
            painting.strokes = mutatedStrokes

            print(f"Evaluation {evaluation}: {painting.current_error}")
            logwriter(f, evaluation, painting.current_error, analyzeStrokes(painting)[0], analyzeStrokes(painting)[1])
            cv2.imwrite(f"{run_folder}/HC-best.png", painting.canvas_memory)


        # Output painting every 1000 evaluations and the final evaluation
        if evaluation == 0 or evaluation == evaluations - 1 or (evaluation % 10 == 0 and evaluation != 0):
            cv2.imwrite(f"{run_folder}/HC-{evaluation}.png", painting.canvas_memory)
    
    # Output final image and pickle
    cv2.imwrite(f"{run_folder}/HC-final-{len(painting.strokes)}.png", painting.canvas_memory)
    pickle.dump(painting, open(f"{run_folder}/HC-{len(painting.strokes)}-final.p", "wb"))

    # End overall timer
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
        strokeTypes.append(stroke.brush_type+1)
    countedStrokes = Counter(strokeTypes)

    return countedStrokes, averageStrokeSize

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('argfilename', metavar='N', nargs='+', help='painting name')
    args = parser.parse_args()

    filename = str(args.argfilename[0])
    imagePath = f"imgs/{filename}"

    # Setup parameters
    evaluations = 100
    strokeCount = 25

    canvas = Painting(imagePath)
    canvas.init_strokes(strokeCount)

    hillclimber(canvas, evaluations, filename)