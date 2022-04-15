import streamlit as st
from utils import save_nieches, load_nieches, NoNiechesData
from typing import List, Dict, Type, Optional
from products import Product, Products

st.title('Amazon FBA')

if 'nieches' not in st.session_state:
    #Load the nieches information
    try:
        st.session_state['nieches'] = load_nieches("./data.json")
    except NoNiechesData:
        st.session_state['nieches'] = {}

BSR_ranges = {
            'baby':(100, 7500),
            'beauty':(100, 19000),
            'office':(100, 14000),
            'pet supplies':(100, 14000),
            'sports and outdoors':(100, 17000),
            'home and kitchen':(100, 24000),
            'kitchen and dining':(100, 17000),
            'patio, lawn and garden':(100, 8500),
            'toys and games':(100, 17000),
            }

with st.sidebar:
    st.header('Actual BSR Ranges')
    for cat_, range_ in BSR_ranges.items():            
        st.write(f"- **{cat_}**: {range_}")
    st.write("***")

st.write('***')
st.subheader('Delete Niech')
#Delete a niech from the data
with st.form('del-niech'):
    del_niech_name = st.selectbox('Niech Name:', 
                                  options=list(st.session_state['nieches'].keys()))
    del_niech = st.form_submit_button("Delete")
if del_niech:
    del st.session_state['nieches'][del_niech_name]

st.subheader('New Niech')
#Add a niech into the data
with st.form('new_niech'):
    niech_name = st.text_input(label='Name',)
    add_niech = st.form_submit_button("Add")
if add_niech:
    st.session_state['nieches'][niech_name] = Products(products=[])

st.header('Select Niech')
selected_niech = st.selectbox('Niech', 
                              options=st.session_state['nieches'].keys())
#Select a specific niech
if selected_niech:
    niech = st.session_state['nieches'][selected_niech]
    if niech.number_products > 0:
        #Display all the products in the niech in a tabular fashion
        st.subheader('Resume')
        st.dataframe(niech.dataframe())

    with st.sidebar:
        st.title('Niech Selecionado')
        st.header(f'Niech **{selected_niech}**')
        st.write('Add a New Product')
        new_product = st.checkbox('New Product')
    
    #Insert a new product
    if new_product:
        with st.form("product_form"):
            st.write("Add a new Product")
            url = st.text_input(label='URL',)
            keywords = st.text_input(label='Keywords',)
            keywords = keywords.split(" ")
            category = st.selectbox('Category', 
                                    options = BSR_ranges.keys())
            price = st.number_input(label='Price', 
                                    min_value=19.99, 
                                    max_value=50.0)
            BSR = st.number_input(label='BSR', 
                                  min_value=BSR_ranges[category][0], 
                                  max_value=BSR_ranges[category][1])
            reviews = st.number_input(label='Number Reviews', 
                                      min_value=0)
            monthly_sales = st.number_input(label='Monthly Sales', 
                                            min_value=0)
            estimated_sourcing_cost = st.number_input(label='Sourcing Cost', 
                                                      min_value=0.0, 
                                                      step=0.1)
            fba_fee = st.number_input(label='FBA Fee', 
                                      min_value=0.0, 
                                      step=0.1)
            referal_fee = st.number_input(label='Referal Fee', 
                                          min_value=0.0, 
                                          step=0.1)
            submitted = st.form_submit_button("Add")
        
        if submitted:
            #Instantiate a products.Product instance
            product = Product(
                              url=url,
                              keywords=keywords,
                              category=category,
                              price=price, 
                              BSR=BSR,
                              reviews=reviews,
                              monthly_sales=monthly_sales,
                              estimated_sourcing_cost=estimated_sourcing_cost,
                              fba_fee=fba_fee,
                              referal_fee=referal_fee,
                             )
            st.session_state['nieches'][selected_niech].add(product)
            st.subheader('- Product Profit Margin: ', product.profit_margin)
            st.session_state['prod_button'] = False
        
    with st.sidebar:
        if selected_niech in st.session_state['nieches']:
            st.write('**Info**')
            niech = st.session_state['nieches'][selected_niech]
            if niech.number_products > 0:
                niech_product = niech.hypothesis_product()
                st.write(f"Number of Products: `{niech.number_products}`")
                st.write(f"Expected Monthly Revenue: `{niech_product.monthly_revenue}`")
                st.write(f"Expected Monthly Sales: `{niech_product.monthly_sales}`")
                expected_unit_cost = niech_product.estimated_sourcing_cost + niech_product.fba_fee + niech_product.referal_fee
                st.write(f"Expected Unit Cost: `{expected_unit_cost}`")
                st.write(f"Expected Monthly Profit: `{niech_product.monthly_profit}`")
                st.write(f"Expected Profit Margin: `{niech_product.profit_margin}`")
                st.write('***')
            else:
                st.warning("No products added to this niech yet.")
        
    st.write(st.session_state['nieches'])
    #Save the nieches data into pickle
    save_nieches(path='./data.json',
                 nieches_data=st.session_state['nieches'])
        
        
