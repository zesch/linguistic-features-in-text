import streamlit as st
import inspect
from cassis import Cas
from dkpro import T_ANOMALY
from itertools import chain
from preprocessing import Spacy_Preprocessor
from util import get_all_subclasses, get_constructor_params, load_lift_typesystem
import polars as pl
from cas_visualizer.visualizer import SpanVisualizer
import annotators.misc as misc
import extractors
import readability
from annotators.misc import SEL_BaseAnnotator
from extractors import FEL_AnnotationCounter, FEL_AnnotationRatio, FEL_Abstractness_min_max_avg
from annotators.frequency import *
from readability import FEL_TextstatReadabilityScore

st.set_page_config(layout='wide')
st.title('LiFT Workbench')

text = st.text_area('Enter text', value="Das ist ein einfacher Beispielsatz. Hier ist ein zweiter Satz mit einem Fehler: einfcher.")    

ts = load_lift_typesystem()
spacy = Spacy_Preprocessor(language='de')
cas = spacy.run(text)

classes_SEL = get_all_subclasses(misc, SEL_BaseAnnotator)
#print('All subclasses')
#print(classes_SEL)

#col_a, col_b = st.columns(2)

with st.sidebar:
#with col_a:

    name_to_class = {cls.__name__: cls for cls in classes_SEL}
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
                                   ['Abstractness', 'Frequency', 'Spelling', 'POS', 'Token'])
        if st.button("Run SEs"):
            for s in name_to_class:
                obj = selected_SE(**user_inputs)
            if not obj.process(cas):
                st.error("Processing of {obj.__class__.__name__} failed.")

    except Exception as e:
        st.error(f"Error: {e}")


#with col_b:

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
                if not obj.extract(cas):
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
            span_vis.add_type(type_name='de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS',
                              feature_name='PosValue')


    html = span_vis.visualize(cas)
    st.html(html)

with col2:
    rows = [{'name': anno.name, 'value': anno.value} for anno in cas.select('FeatureAnnotationNumeric')]
    df = pl.DataFrame(rows)
    st.dataframe(df)