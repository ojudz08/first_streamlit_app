import streamlit
import pandas as pd
import requests
import snowflake.connector
from urllib.error import URLError

streamlit.title("My Mom's New Healthy Diner")

streamlit.header('Breakfast Favorites')
streamlit.text('🥣 Omega 3 & Blueberry Oatmeal')
streamlit.text('🥗 Kale, Spinach & Rocket Smoothie')
streamlit.text('🐔 Hard-Boiled Free-Range Egg')
streamlit.text('🥑🍞 Avocado Toast')

streamlit.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')


# Read the fruit_macros.txt from your AWS S3 bucket
my_fruit_list = pd.read_csv('https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt')
my_fruit_list = my_fruit_list.set_index('Fruit')

# Pick list to interact what fruit they want to include
fruits_selected = streamlit.multiselect('Pick some fruits: ', list(my_fruit_list.index), ['Avocado', 'Strawberries'])
fruits_to_show = my_fruit_list.loc[fruits_selected]

# Display the table on the page
streamlit.dataframe(fruits_to_show)

# Create function to get fruit_choice
def get_fruityvice_data(fruit_choice):
  fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_choice)  # requests
  fruityvice_normalized = pd.json_normalize(fruityvice_response.json())                   # Take the json version of the response and normalize it
  return fruityvice_normalized


# Display fruityvice api response
streamlit.header('Fruityvice Fruit Advice!')
try:
  fruit_choice = streamlit.text_input('What fruit would you like information about?', 'Kiwi')
  if not fruit_choice:
    streamlit.write('The user entered', fruit_choice)
  else:
    get_fruit = get_fruityvice_data(fruit_choice)
    streamlit.dataframe(get_fruit)

#except URLError as e:
  #streamlit.error()        # returns the error
except Exception as e:
  print(f'{e}')


streamlit.header("The fruit load list contains:")

# Snowflake function
def get_fruit_load_list():
  with my_cnx.cursor() as my_cur:
    my_cur.execute("SELECT * FROM PC_RIVERY_DB.PUBLIC.FRUIT_LOAD_LIST")
    return my_cur.fetchall()
 
# Add button to load the fruit
if streamlit.button('Get Fruit Load List'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  my_data_rows = get_fruit_load_list()
  my_cnx.close()
  streamlit.dataframe(my_data_rows)


# Allow the end user to add a fruit to the list
def insert_row_snowflake(new_fruit):
  with my_cnx.cursor() as my_cur:
    my_cur.execute("INSERT INTO PC_RIVERY_DB.PUBLIC.FRUIT_LOAD_LIST VALUES ('from streamlit')")
    return f'Thanks for adding {new_fruit}'

add_my_fruit = streamlit.text_input('What fruit would you like to add?', 'jackfruit')
if streamlit.button('Add a Fruit to the List'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  insert_fruits = insert_row_snowflake(add_my_fruit)
  streamlit.dataframe(insert_fruits)
