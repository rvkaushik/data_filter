import streamlit as st
import pandas as pd
import sqlite3
"""
# Data Filter
# 3   ----------   car,  8   ----------   truck,
# 10  ----------   traffic light,  18  ----------   dog
"""

def user_inputs():
    dog = st.sidebar.slider("Dog - ", min_value=1, max_value=10, value=10)
    car = st.sidebar.slider("Car - ", min_value=1, max_value=10, value=10)
    truck = st.sidebar.slider("truck - ", min_value=1, max_value=10, value=10)
    traffic_light = st.sidebar.slider("traffic_light - ", min_value=1, max_value=10, value=10)
    labels_count = [(3, car), (8, traffic_light), (10, truck), (18, dog)]
    return labels_count

def extract_from_db_OR(labels_count):
    conn = sqlite3.connect("/home/ec2-user/data_filter/test.db")
    filter_command = '''WITH SCORE_FILTERED AS (SELECT * 
                                                FROM CLASSIFICATION
                                                WHERE SCORE > 0.5)
                        SELECT FILEPATH, CLS, COUNT(CLS) AS label_count FROM SCORE_FILTERED
                        GROUP BY FILEPATH, CLS
                        HAVING (CLS = ? AND label_count >= ?) OR (CLS = ? AND label_count >= ?)
                        OR (CLS = ? AND label_count >= ?) OR (CLS = ? AND label_count >= ?)
                        '''
    car_id , car_count = labels_count[0]
    tl_id, tl_count = labels_count[1]
    truck_id, truck_count = labels_count[2]
    dog_id, dog_count = labels_count[3]
    values = (car_id, car_count, tl_id, tl_count, truck_id, truck_count, dog_id, dog_count)
    db = conn.execute(filter_command, values)
    for row in db:
        row
    conn.close()

def extract_from_db_AND(labels_count):
    conn = sqlite3.connect("test.db")
    filter_command = '''WITH SCORE_FILTERED AS (SELECT * 
                                            FROM CLASSIFICATION
                                            WHERE SCORE > 0.5)
                    SELECT  FILEPATH, (group_concat(CLS)) as GP
                    FROM SCORE_FILTERED
                    GROUP BY FILEPATH
                    HAVING ( ? IN GP) AND (? IN GP)
                    AND (? IN GP) AND (? IN GP)
                    '''
    car_id , car_count = labels_count[0]
    tl_id, tl_count = labels_count[1]
    truck_id, truck_count = labels_count[2]
    dog_id, dog_count = labels_count[3]
    values = (car_id, car_count, tl_id, tl_count, truck_id, truck_count, dog_id, dog_count)
    db = conn.execute(filter_command, values)
    for row in db:
        row
    conn.close()

if __name__ == "__main__":
    st.sidebar.header("User Input")
    labels_count = user_inputs()
    option = st.selectbox(
        'Select Condition',
        ["OR", "AND"])

    if option == "OR":
        extract_from_db_OR(labels_count)
    elif option == "AND":
        extract_from_db_AND(labels_count)
    else:
        "SELECT ONE OPTION"




