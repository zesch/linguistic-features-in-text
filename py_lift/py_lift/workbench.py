import streamlit as st
import inspect
from cassis import Cas
from py_lift.dkpro import T_ANOMALY, T_POS
from itertools import chain
from py_lift.preprocessing import Spacy_Preprocessor
from py_lift.util import get_all_subclasses, get_constructor_params, load_lift_typesystem, detect_language
import polars as pl
from cas_visualizer.visualizer import SpanVisualizer
import py_lift.annotators.misc as misc
import py_lift.annotators.frequency as frequency
import py_lift.extractors
import py_lift.readability
from py_lift.annotators.api import SEL_BaseAnnotator
from py_lift.extractors import FEL_AnnotationCounter, FEL_AnnotationRatio, FEL_Abstractness_min_max_avg
from py_lift.annotators.frequency import *
from py_lift.readability import FEL_TextstatReadabilityScore

st.set_page_config(layout='wide')
st.title('LiFT Workbench')

text = st.text_area('Enter text', value="Das ist ein einfacher Beispielsatz. Hier ist ein zweiter Satz mit einem Fehler: einfcher.")    
language_detected = detect_language(text)
st.write(f'Detected language: {language_detected}')

ts = load_lift_typesystem()
spacy = Spacy_Preprocessor(language=language_detected)
cas = spacy.run(text)

classes_SEL = get_all_subclasses(misc, SEL_BaseAnnotator)
classes_freq = get_all_subclasses(frequency, SEL_BaseAnnotator)
#print('All subclasses')
#print(classes_SEL)

#col_a, col_b = st.columns(2)

with st.sidebar:
#with col_a:

    name_to_class = {cls.__name__: cls for cls in chain(classes_SEL, classes_freq)}
    selected_class_name = st.selectbox("Choose an SE", name_to_class.keys())
    selected_SE = name_to_class[selected_class_name]

    try:
        params = get_constructor_params(selected_SE)
        #print('params')
        #print(params)

        user_inputs = {}
        for param in params:
            if param.annotation == int:
                user_inputs[param.name] = st.number_input(param.name, value=0)
            elif param.annotation == float:
                user_inputs[param.name] = st.number_input(param.name, value=0.0)
            else:  # Default to string
                user_inputs[param.name] = st.text_input(param.name)

        select_type = st.selectbox('Select type to highlight',
                                   ['Abstractness', 'Frequency', 'Spelling', 'POS', 'Token'], index=3)
        if st.button("Run SEs"):
            for s in name_to_class:
                obj = selected_SE(**user_inputs)
                st.session_state['cas'] = cas
            if not obj.process(cas):
                st.error("Processing of {obj.__class__.__name__} failed.")

    except Exception as e:
        st.error(f"Error: {e}")


#with col_b:
if "cas" in st.session_state:
    my_cas = st.session_state["cas"]

    classes_readability = get_all_subclasses(readability, FEL_TextstatReadabilityScore)
    classes_counters = get_all_subclasses(extractors, FEL_AnnotationCounter)
    classes_ratios = get_all_subclasses(extractors, FEL_AnnotationRatio)
    classes_abstractness = get_all_subclasses(extractors, FEL_Abstractness_min_max_avg)

    name_to_FEs = {cls.__name__: cls for cls in chain(classes_readability, classes_counters, classes_ratios, classes_abstractness)}
    selected_FE_names = st.multiselect("Choose one or more FEs", name_to_FEs.keys())
    selected_FEs = [name_to_FEs[name] for name in selected_FE_names]


    # run all selected FEs
    fe_params = {'language': 'de'}
    fe_params = {}
    try:
        if st.button("Run FEs"):
            for selected_FE in selected_FEs:
                # TODO how to configure that in streamlit, assuming language parameter for now
                obj = selected_FE(**fe_params)
                if not obj.extract(my_cas):
                    st.error("Processing of {obj.__class__.__name__} failed.")
    except Exception as e:
        st.error(f"Error: {e}")

col1, col2 = st.columns(2)

with col1:

    span_vis = SpanVisualizer(ts)
    span_vis.selected_span_type = SpanVisualizer.UNDERLINE
    span_vis.allow_highlight_overlap = True

    match select_type:
        case 'Abstractness':
            span_vis.add_type(type_name='org.lift.type.AbstractnessConcreteness', feature_name='value')
            print('abst')
        case 'Spelling':
            span_vis.add_type(T_ANOMALY)
        case 'Token':
            span_vis.add_type(T_TOKEN)
        case 'Frequency':
            span_vis.add_type(type_name='org.lift.type.Frequency', feature_name='frequencyBand')
        case 'POS':
            span_vis.add_type(type_name=T_POS, feature_name='PosValue')


    html = span_vis.visualize(my_cas)
    st.html(html)

with col2:
    rows = [{'name': anno.name, 'value': anno.value} for anno in my_cas.select('FeatureAnnotationNumeric')]
    df = pl.DataFrame(rows)
    st.dataframe(df)