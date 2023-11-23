from flask import Flask, jsonify, request
import csv
from datetime import datetime

app = Flask(__name__)

file_name = 'AAPL.csv'

admin_key = "IAMADMIN123"

#FUNCTIONS

# This is taking doing the reading from the CSV file
def read_stock_csv(file_path):
    data = []
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    return data

# This is getting the data using a specific date
def get_data_using_date(data, date):
    for row in data:
        if row['Date'] == date:
            return row
    return None

# This is calulating the average close for the last 10 days
def calculate_10_day_average(data):
    total = 0
    for row in data[:10]:
        total += float(row['Close'])
    return total / 10

# This is taking data as an input and writing it to the CSV file
def adding_data(data):
    with open(file_name, 'w', newline='') as csv_file:
        entries = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        csv_writer = csv.DictWriter(csv_file, fieldnames=entries)

        csv_writer.writeheader()
        csv_writer.writerows(data)

#This is sorting data based on data
def sort_data_by_range(data, start, end):
    sorted_data = []
    for row in data:
        current = datetime.strptime(row['Date'], '%Y-%m-%d')
        if start <= current <= end:
            sorted_data.append(row)
    return sorted_data


# ROUTES
 
# This has the /getData route defined which will just return data read by the read_stock_csv function
@app.route('/getData', methods=['GET'])
def get_data():
    data = read_stock_csv(file_name)
    return jsonify(data)

# This has the /getData/<date> route defined which will just use the get_data_using_date function to get the row assigned to the date, if it is a valid date
@app.route('/getData/<date>', methods=['GET'])
def get_data_this_date(date):
    data = read_stock_csv(file_name)
    row = get_data_using_date(data, date)
    if row:
        return jsonify(row)
    else:
        return jsonify({'error': 'Data cannot be found'}), 404

# This has the /calculate10DayAverage route defined which will just return data read by the calculate_10_day_average function
@app.route('/calculate10DayAverage', methods=['GET'])
def calculate_10_day_average_data():
    data = read_stock_csv(file_name)
    average = calculate_10_day_average(data)
    return jsonify({'10 Day Average': average})

# This has the /addData route defined which will take the requested data and check to make sure it is a valid request and then write it to the file using the add_data function
@app.route('/addData', methods=['POST'])
def add_data():
    data = read_stock_csv(file_name)
    request_data = request.json

    if not all(key in request_data for key in ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']):
        return jsonify({'error': 'Invalid request. Provide Date, Open, High, Low, Close, Adj Close, and Volume.'}), 400
    
    data.append(request_data)
    adding_data(data)

    return jsonify({'message' : 'Added successfully!'})

# This has the /getData route defined which will take the start and end dates and using the sort_data_by_range function, it will give the requested data set, sorted, if it is a valid request
@app.route('/getData', methods=['POST'])
def get_data_from_range():
    data = read_stock_csv(file_name)
    request_data = request.json

    if 'start' not in request_data or 'end' not in request_data:
        return jsonify({'error': 'Invalid request. Provide start and end date.'}), 400

    start = datetime.strptime(request_data['start'], '%Y-%m-%d')
    end = datetime.strptime(request_data['end'], '%Y-%m-%d')

    result = sort_data_by_range(data, start, end)
    return jsonify(result)

# This has the /updateData route defined which will check to see if a requested date is given and if it is valid, then it will proceed to overwrite the existing data
@app.route('/updateData', methods=['PUT'])
def update_data():
    data = read_stock_csv(file_name)
    request_data = request.json

    if 'Date' not in request_data:
        return jsonify({'error': 'Invalid request. Provide a date.'}), 400
    
    #Following line is setting what the update target should be
    target_update = request_data['Date']
    #Following line is setting what to update from the original data set
    update_this = next((row for row in data if row['Date'] == target_update), None)

    if update_this: #if update_this is found, overwrite data; if not, give error
        update_this.update(request_data)
        adding_data(data)
        return jsonify({'message': f'Data for {target_update} updated successfully.'})
    else:
        return jsonify({'error': 'Data not found.'}), 404
    
# This has the /deleteData route defined which will check to see if a requested date is given and if it is valid, then it will proceed to delete the existing data
@app.route('/deleteData', methods=['DELETE'])
def delete_data():
    data = read_stock_csv(file_name)
    request_data = request.json

    if 'Date' not in request_data:
        return jsonify({'error': 'Invalid request. Provide a date.'}), 400
    
    #Following line is setting what the update target should be
    target_delete = request_data['Date']
    #Following line is setting what to update from the original data set
    delete_this = next((row for row in data if row['Date'] == target_delete), None)

    if delete_this: #if delete_this is found, delete data; if not, give error
        data.remove(delete_this)
        adding_data(data)
        return jsonify({'message': f'Data for {target_delete} deleted successfully.'})
    else:
        return jsonify({'error': 'Data not found.'}), 404
    
# This has the /deleteAll route defined which will check to see if a requested user has access to this route, then it will proceed to delete the existing data if so, or else give authentication error
@app.route('/deleteAll', methods=['DELETE'])
def delete_all_data():
    #Have user enter key through headers
    user_key = request.headers.get('User-Key')

    #Simply do comparison of strings and if it's equal, using the adding_data function, overwrite the data with an empty data set 
    if user_key != admin_key:
        return jsonify({'error': 'Access denied. Invalid key.'}), 401
    else:
        adding_data([])
        return jsonify({'message': 'Access granted. Successful deletion.'})


if __name__ == '__main__':
    app.run(debug=True)
