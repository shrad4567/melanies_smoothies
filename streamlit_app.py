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
    .select(col("FRUIT_NAME"),col('SEARCH_ON'))

# CONVRT SNOWFLAKE DATAFRAME INTO PANDAS
pd_df=my_dataframe.to_pandas()
# st.dataframe(pd_df)


ingredient_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

if ingredient_list:

 
    ingredient_string=''
 
    for each_fruit in ingredient_list:
        ingredient_string+=each_fruit + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == each_fruit, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        st.subheader(each_fruit+ 'Nutrition_Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")  
        sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)
 
    st.write(ingredient_string)


    # Insert into Snowflake
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredient_string}', '{name_of_order}')
    """

    if st.button("Submit Button"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered! ✅")
