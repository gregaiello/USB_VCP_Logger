USB VCP Logger:

Requirements:
- pip install pyserial matplotlib

Logger:
- CSV Integration: A CSV file (sensor_data.csv) is opened and written.
- CSV Header: The header ['DataA', 'DataB', 'DataC', 'DataD'] is written at the start of the CSV.
- Writing Data: Each parsed packet is written to the CSV as a new row with the values for DataA, DataB, DataC, and DataD.
