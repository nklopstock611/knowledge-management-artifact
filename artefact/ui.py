import streamlit as st
import pandas as pd
import rdflib
import queries as qs

def consolidate_properties(results):
    prop_dict = {}
    for prop, val in results:
        val_str = str(val)
        if prop in prop_dict:
            prop_dict[prop].append(val_str)
        else:
            prop_dict[prop] = [val_str]

    # Converts lists of values into HTML lists if there are more than one value of a property
    for prop in prop_dict:
        if len(prop_dict[prop]) > 1:
            prop_dict[prop] = '<ul>' + ''.join(f'<li>{value}</li>' for value in prop_dict[prop]) + '</ul>'
        else:
            prop_dict[prop] = prop_dict[prop][0]

    return prop_dict

def get_class_name(results):
    for prop, value in results:
        if str(prop) == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
            return str(value).split('/')[-1]

    return None

def handle_click(instance_name):
    st.session_state.instance_uri = instance_name

def load_data(instance_uri):
    results = qs.get_properties_and_values_of_instance(f"http://example.org/{instance_uri}")
    if results:
        prop_dict = consolidate_properties(results)
        print(prop_dict)
        data = [{"Property": prop.replace('http://example.org/', ''), "Value": values.replace('http://example.org/', '')} for prop, values in prop_dict.items()]
        df = pd.DataFrame(data)

        # Render HTML in dataframe cells without index
        class_of_instance = qs.get_class_of_instance(f"http://example.org/{instance_uri}")
        class_of_instance = get_class_name(class_of_instance)
        st.subheader(f"Type: {class_of_instance}")

        html = df.to_html(escape=False, index=False)
        html = html.replace('<th>', '<th style="text-align: left;">')
        html = html.replace('<table border="1" class="dataframe">', '<table style="width: 100%;">')
        st.markdown(html, unsafe_allow_html=True)                      

    else:
        st.write("No results found for the given URI.")

    return prop_dict, results

# ============ #
# Streamlit UI #
# ============ #

st.title('RDF Instance Property Viewer')

instance_uri = st.text_input('Enter the name of the RDF instance:', key='instance_uri')

if instance_uri:
    st.session_state['current_uri'] = instance_uri
    prop_dict, results = load_data(instance_uri)

    # Instances of classes in properties section
    if qs.has_instances(results):
        st.write("")
        st.subheader("Instances of classes in properties")
        for prop, value in prop_dict.items():
            if qs.is_instance_uri(value):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    col1.text(f"{prop}: ")
                    instance = value.split('/')[-1]
                    col2.button(instance, on_click=handle_click, args=(instance,))  
else:
    st.write("Please enter a valid URI.")
