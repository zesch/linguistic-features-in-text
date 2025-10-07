import streamlit as st
import inspect
from cassis import Cas
from dkpro import T_ANOMALY
from preprocessing import Spacy_Preprocessor
from util import get_all_subclasses, get_constructor_params, load_lift_typesystem
import polars as pl
from cas_visualizer.visualizer import SpanVisualizer
import annotators
from readability import *
from annotators import *
from frequency import *

st.set_page_config(layout='wide')
st.title('LiFT Workbench')

text = st.text_area('Enter text', value="Das ist ein einfacher Beispielsatz. Hier ist ein zweiter Satz mit einem Fehler: einfcher.")    

ts = load_lift_typesystem()
spacy = Spacy_Preprocessor(language='de')
cas = spacy.run(text)

cls = get_all_subclasses(annotators, SEL_BaseAnnotator)[0]

try:
    params = get_constructor_params(cls)

    user_inputs = {}
    for param in params:
        if param.annotation == int:
            user_inputs[param.name] = st.number_input(param.name, value=0)
        elif param.annotation == float:
            user_inputs[param.name] = st.number_input(param.name, value=0.0)
        else:  # Default to string
            user_inputs[param.name] = st.text_input(param.name)

    if st.button("Instantiate"):
        obj = cls(**user_inputs)
        if not obj.process(cas):
            st.error("Processing of {obj.__class__.__name__} failed.")
except Exception as e:
    st.error(f"Error: {e}")

all_features = []
all_feature_values = []
for anno in cas.select('FeatureAnnotationNumeric'):
    if anno.name not in all_features:
        all_features.append(anno.name)
        all_feature_values.append(anno.value)

col1, col2 = st.columns(2)

with col1:
    select_type = st.selectbox('Select type to highlight', ['Frequency', 'Spelling', 'POS'])
    span_vis = SpanVisualizer(ts)
    span_vis.selected_span_type = SpanVisualizer.UNDERLINE
    span_vis.allow_highlight_overlap = True

    match select_type:
        case 'Spelling':
            span_vis.add_type(T_ANOMALY)
        case 'Frequency':
            span_vis.add_type(type_name='org.lift.type.Frequency', feature_name='frequencyBand')
        case 'POS':
            span_vis.add_type(type_name='de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS',
                              feature_name='PosValue')

    html = span_vis.visualize(cas)
    st.html(html)

with col2:
    d = {'values': all_feature_values}
    df = pl.DataFrame(data=d, schema={'values': pl.Float64})
    st.dataframe(df)