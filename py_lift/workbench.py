import streamlit as st
from cassis import *
import spacy
import pandas as pd
from cas_visualizer.visualizer import SpanVisualiser
from extractors import FE_TokensPerSentence
from readability import FEL_ReadabilityScore
from annotators import SE_SpellErrorAnnotator
from frequency import SE_WordFrequency
from syntax import FE_CasToTree




st.set_page_config(layout='wide')
st.title('LiFT Workbench')

with st.expander('Enter text'):
    text = st.text_area('Enter text')

#######################
#                     #
# PREPROCESSING MAGIC #
#stub:                #
file = 'blub'         #
#                     #
#######################

#add lift stuff to cas
with open('data/TypeSystem.xml', 'rb') as f:
    typesys = load_typesystem(f)
cas = load_cas_from_xmi(file, typesystem=typesys)

#length
FE_TokensPerSentence().extract(cas.get_view('ctok'))

# readability
# Readability_Score_Flesch_Kincaid_Lang_de
FEL_ReadabilityScore('de').extract(cas.get_view('ctok'))


# spelling
# de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SpellingAnomaly
# de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SuggestedAction
# SpellingAnomaly_PER_Token
SE_SpellErrorAnnotator('de').process(cas.get_view('ctok'))

# frequency
SE_WordFrequency('de').process(cas.get_view('ctok'))

# syntax
# Average_Size_Of_Lexical_NP
# Proportion_of_Subj_Vfin_Inversions
# Average_Tree_Depth
# Average_Sentence_Length
# Average_Maximal_Dependency_Length
# Average_Dependency_Length_Left
# Average_Dependency_Length_Right
# Average_Dependency_Length_All
# Average_Number_Of_Finite_Verbs
# Average_Number_Of_Verbs
fe2cas1 = FE_CasToTree('ctok', typesys, 'de', False)
fe2cas1.extract(cas.get_view('ctok'))

#start visualization
all_features = []
all_feature_values = []
for anno in cas.select('FeatureAnnotationNumeric'):
    if anno.name not in all_features:
        all_features.append(anno.name)
        all_feature_values.append(anno.value)

col1, col2 = st.columns(2)

with col1:
    select_type = st.selectbox('Select type to highlight', ['Frequency', 'Spelling', 'POS'])
    span_vis = SpanVisualiser(typesys)
    span_vis.selected_span_type = SpanVisualiser.HIGHLIGHT
    span_vis.allow_highlight_overlap = True

    match select_type:
        case 'Spelling':
            span_vis.add_type(type_name='de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SpellingAnomaly')
        case 'Frequency':
            span_vis.add_type(type_name='org.lift.type.Frequency', feature_name='frequencyBand')
        case 'POS':
            span_vis.add_type(type_name='de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS',
                              feature_name='PosValue')


    html = span_vis.visualise(cas)
    st.html(html)

with col2:
    d = {'values': all_feature_values}
    df = pd.DataFrame(data=d, index=all_features)
    st.dataframe(df)