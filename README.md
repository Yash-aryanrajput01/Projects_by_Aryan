# Projects_by_Aryan
Step 1: Setup the Project
We'll set up a web application using Flask for the backend and a simple frontend using HTML/CSS and JavaScript. The app will handle CSV file uploads, process the data, and manage the allocation logic.

Step 2: Define the CSV Data Structure
The application will read two CSV files with the following structures:

Group Information CSV:

Group ID, Members, Gender
101, 3, Boys
102, 4, Girls
103, 2, Boys
104, 5, Girls
105, 8, 5 Boys & 3 Girls

Hostel Information CSV:

Hostel Name, Room Number, Capacity, Gender
Boys Hostel A, 101, 3, Boys
Boys Hostel A, 102, 4, Boys
Girls Hostel B, 201, 2, Girls
Girls Hostel B, 202, 5, Girls

Step 3: Frontend for File Upload
Create an HTML form to allow users to upload the two CSV files. This will involve a simple form with file input fields and a submit button.

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Hostel Allocation</title>
</head>
<body>
    <h1>Upload Group and Hostel Information</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <label for="groupFile">Group Information CSV:</label>
        <input type="file" id="groupFile" name="groupFile" accept=".csv" required><br><br>
        <label for="hostelFile">Hostel Information CSV:</label>
        <input type="file" id="hostelFile" name="hostelFile" accept=".csv" required><br><br>
        <button type="submit">Upload and Allocate</button>
    </form>
</body>
</html>

Step 4: Backend for Processing CSV Files
Implement Flask routes to handle file uploads, process the CSV data, and perform room allocation.

from flask import Flask, request, render_template, send_file
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    group_file = request.files['groupFile']
    hostel_file = request.files['hostelFile']
    
    group_df = pd.read_csv(group_file)
    hostel_df = pd.read_csv(hostel_file)
    
    allocation = allocate_rooms(group_df, hostel_df)
    
    output_csv = 'allocation_result.csv'
    allocation.to_csv(output_csv, index=False)
    
    return send_file(output_csv, as_attachment=True)

def allocate_rooms(group_df, hostel_df):
    # Initialize an empty DataFrame for the allocation results
    allocation_results = pd.DataFrame(columns=['Group ID', 'Hostel Name', 'Room Number', 'Members Allocated'])

    # Process each group in the group_df
    for _, group in group_df.iterrows():
        group_id = group['Group ID']
        members = group['Members']
        gender = group['Gender']
        
        # Split mixed groups
        if '&' in gender:
            boys, girls = map(int, gender.split(' & '))
        else:
            boys, girls = (members, 0) if 'Boys' in gender else (0, members)

        # Allocate boys
        if boys > 0:
            boys_alloc = allocate_group_to_hostel(group_id, boys, 'Boys', hostel_df, allocation_results)
            allocation_results = pd.concat([allocation_results, boys_alloc], ignore_index=True)

        # Allocate girls
        if girls > 0:
            girls_alloc = allocate_group_to_hostel(group_id, girls, 'Girls', hostel_df, allocation_results)
            allocation_results = pd.concat([allocation_results, girls_alloc], ignore_index=True)

    return allocation_results

def allocate_group_to_hostel(group_id, members, gender, hostel_df, allocation_results):
    # Filter hostels based on gender
    available_rooms = hostel_df[(hostel_df['Gender'] == gender) & (hostel_df['Capacity'] >= members)]

    allocation = []
    
    while members > 0:
        if available_rooms.empty:
            raise ValueError(f"No available rooms for {gender} group ID {group_id} with {members} members")

        room = available_rooms.iloc[0]
        room_capacity = room['Capacity']
        hostel_name = room['Hostel Name']
        room_number = room['Room Number']

        if members <= room_capacity:
            allocation.append([group_id, hostel_name, room_number, members])
            members = 0
        else:
            allocation.append([group_id, hostel_name, room_number, room_capacity])
            members -= room_capacity
            available_rooms = available_rooms.iloc[1:]

    # Update the hostel DataFrame to remove the allocated room
    for _, row in allocation:
        hostel_df = hostel_df[(hostel_df['Hostel Name'] != row[1]) | (hostel_df['Room Number'] != row[2])]

    return pd.DataFrame(allocation, columns=['Group ID', 'Hostel Name', 'Room Number', 'Members Allocated'])

if __name__ == '__main__':
    app.run(debug=True)

Step 5: Running the Application
Install Flask and pandas:

pip install Flask pandas

Run the Flask application:

python app.py

Step 6: Testing
Upload the sample CSV files using the web interface and verify the allocation results.

Step 7: Enhancements
Add error handling for various edge cases.
Improve the UI for better user experience.
Implement user authentication if needed.
Deploy the application to a cloud platform for accessibility.
This plan outlines the basic structure of the web application to facilitate the digitalization of the hospitality process for group accommodations, ensuring the allocation meets the specified criteria.


