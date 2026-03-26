# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests  

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_of_order = st.text_input("Name Of Smoothie:")
st.write("The Name of Your Smoothie will be:", name_of_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME"))

ingredient_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

if ingredient_list:
    st.write(ingredient_list)

    ingredient_string = ""

    # ✅ Loop ONLY for building ingredient string
    for x in ingredient_list:
        ingredient_string += x + " "

    # ✅ API call OUTSIDE the loop
    smoothiefroot_response = requests.get(
        "https://my.smoothiefroot.com/api/fruit/watermelon"
    )

    if smoothiefroot_response.status_code == 200:
        st.subheader("SmoothieFroot API Response")
        st.json(smoothiefroot_response.json(), use_container_width=True)
    else:
        st.error("Failed to fetch data from SmoothieFroot API")

    # Insert into Snowflake
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredient_string}', '{name_of_order}')
    """

    if st.button("Submit Button"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered! ✅")
