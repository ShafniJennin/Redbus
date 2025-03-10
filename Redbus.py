import time
import sqlite3
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import streamlit as st

# Web Scraping Function
def scrape_redbus():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    url = "https://www.redbus.in/"
    driver.get(url)
    time.sleep(5)  # Wait for the page to load
    
    bus_data = []
    
    buses = driver.find_elements(By.CLASS_NAME, 'some-bus-class')  # Update with actual class
    for bus in buses:
        try:
            route_name = bus.find_element(By.CLASS_NAME, 'route-class').text
            route_link = bus.find_element(By.TAG_NAME, 'a').get_attribute('href')
            busname = bus.find_element(By.CLASS_NAME, 'bus-name-class').text
            bustype = bus.find_element(By.CLASS_NAME, 'bus-type-class').text
            departing_time = bus.find_element(By.CLASS_NAME, 'departure-class').text
            duration = bus.find_element(By.CLASS_NAME, 'duration-class').text
            reaching_time = bus.find_element(By.CLASS_NAME, 'arrival-class').text
            star_rating = bus.find_element(By.CLASS_NAME, 'rating-class').text
            price = bus.find_element(By.CLASS_NAME, 'price-class').text.replace('₹', '').strip()
            seats_available = bus.find_element(By.CLASS_NAME, 'seats-class').text
            
            bus_data.append((route_name, route_link, busname, bustype, departing_time, duration, reaching_time, float(star_rating), float(price), int(seats_available)))
        except:
            continue
    
    driver.quit()
    return bus_data

# Database Setup
def create_database():
    conn = sqlite3.connect('redbus.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bus_routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_name TEXT,
            route_link TEXT,
            busname TEXT,
            bustype TEXT,
            departing_time TEXT,
            duration TEXT,
            reaching_time TEXT,
            star_rating FLOAT,
            price DECIMAL,
            seats_available INT
        )
    ''')
    conn.commit()
    conn.close()

def insert_data(bus_data):
    conn = sqlite3.connect('redbus.db')
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO bus_routes (route_name, route_link, busname, bustype, departing_time, duration, reaching_time, star_rating, price, seats_available)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', bus_data)
    conn.commit()
    conn.close()

# Streamlit Application
def main():
    st.title("Redbus Data Filtering")
    conn = sqlite3.connect('redbus.db')
    df = pd.read_sql_query("SELECT * FROM bus_routes", conn)
    conn.close()
    
    bustype_filter = st.multiselect("Select Bus Type", df['bustype'].unique())
    price_range = st.slider("Select Price Range", int(df['price'].min()), int(df['price'].max()), (int(df['price'].min()), int(df['price'].max())))
    rating_filter = st.slider("Minimum Star Rating", float(df['star_rating'].min()), float(df['star_rating'].max()), float(df['star_rating'].min()))
    
    if bustype_filter:
        df = df[df['bustype'].isin(bustype_filter)]
    df = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]
    df = df[df['star_rating'] >= rating_filter]
    
    st.dataframe(df)

if __name__ == "__main__":
    create_database()
    bus_data = scrape_redbus()
    if bus_data:
        insert_data(bus_data)
    main()
