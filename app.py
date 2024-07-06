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
