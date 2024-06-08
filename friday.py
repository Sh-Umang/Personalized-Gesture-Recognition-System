import csv

def updateKeypoints(input_file, id):
        output_file = input_file  # Use the same name for output file

        with open(input_file, 'r', newline='') as input_csv:
            reader = csv.reader(input_csv)

            # Filter rows based on the condition (first value equals 1)
            filtered_rows = [row for row in reader if row and row[0] != str(id)]

        with open(output_file, 'w', newline='') as output_csv:
            writer = csv.writer(output_csv)

            # Write the filtered rows
            writer.writerows(filtered_rows)

input_file = 'model/keypoints/google_keypoints.csv'
id = 1
updateKeypoints(input_file, id)