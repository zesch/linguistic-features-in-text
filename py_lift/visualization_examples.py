import streamlit as st
from cassis import Cas
from dkpro import T_ANOMALY, T_POS
from preprocessing import Spacy_Preprocessor
from util import load_lift_typesystem, detect_language
import polars as pl
from cas_visualizer.visualizer import SpanVisualizer
from annotators.frequency import SE_TokenZipfFrequency
from annotators.misc import SE_SpellErrorAnnotator
from annotators.lists import SE_FiniteVerbAnnotator


def get_preprocessed_cas(text: str, language: str) -> Cas:
    spacy = Spacy_Preprocessor(language=language)
    return spacy.run(text)

def vis_tr_pos(cas: Cas):
    span_vis = SpanVisualizer(ts)
    span_vis.selected_span_type = SpanVisualizer.HIGHLIGHT
    span_vis.add_type(
        name=T_POS,
        feature='PosValue',
        color="#C9DAF6"
    )
    html = span_vis.visualize(cas)
    st.html(html)

def vis_de_finite_verbs(cas: Cas):
    span_vis = SpanVisualizer(ts)
    span_vis.selected_span_type = SpanVisualizer.UNDERLINE
    span_vis.add_type(T_ANOMALY, default_label="SpellError", color="#F4C7C3")
    span_vis.add_type("org.lift.type.Structure", default_label="FiniteVerb", color="#C3F4C9")

    html = span_vis.visualize(cas)
    st.html(html)

def vis_fr_frequency(cas: Cas):
    span_vis = SpanVisualizer(ts)
    span_vis.selected_span_type = SpanVisualizer.HIGHLIGHT
    span_vis.add_feature("org.lift.type.Frequency", feature="frequencyBand", value="f1", color="#F60707")
    span_vis.add_feature("org.lift.type.Frequency", feature="frequencyBand", value="f2", color="#F87171")
    span_vis.add_feature("org.lift.type.Frequency", feature="frequencyBand", value="f3", color="#F99090")
    span_vis.add_feature("org.lift.type.Frequency", feature="frequencyBand", value="f4", color="#F9B0B0")
    span_vis.add_feature("org.lift.type.Frequency", feature="frequencyBand", value="f5", color="#F8C2C2")
    span_vis.add_feature("org.lift.type.Frequency", feature="frequencyBand", value="f6", color="#F8E2E2")
    span_vis.add_feature("org.lift.type.Frequency", feature="frequencyBand", value="f7", color="#F7F3F3")
    span_vis.add_feature("org.lift.type.Frequency", feature="frequencyBand", value="oov", color="#868FF0")

    html = span_vis.visualize(cas)
    st.html(html)

st.set_page_config(layout='wide')
st.title('Anon Lib Workbench')

ts = load_lift_typesystem()

## Turkish POS visualization example with input box
tr_example = st.text_area('Enter text', value="Okulda Türkçe öğrendim ama çok kötü konuşuyorum.")  
language_detected = detect_language(tr_example)
st.write(f'Detected language: {language_detected}')
tr_cas = get_preprocessed_cas(text=tr_example, language=language_detected)
vis_tr_pos(tr_cas)


## German finite verb example with spelling errors
#de_example = "Sehr geehrte Damen und Herren ich habe Ihre Anannse in der Zeitung gelesen. Von ihr Anzeige bin ich interesiert. Für diese Stelle bringe ich alle Voraussetzungen mit. Ich habe Linguistik studiert und spreche Deutsch, Russicsh und Armenisch. Zusätzlich habe ich Computerkenntnisse. Uber eine positive Antwort wurde ich mir sehr freuen und verbliebe mit freundlich Grüßen"
de_example = "Das Aufkommen des Buchdruckes fürte zu einer Umstrukturierung der Werkstätten. Im Laufe der Zeit entstehen Großbetriebe, wie der von Anton Koberger in Nürnberg. Dieser beschäftigte bis zu 100 Arbeiter an 24 Pressen. Nun wurden Facharbeiter verschiedener Berufe notwendig. Eine neue Art des intellektuellen Austausches wurde möglich. Der Drucker führte alle ausgefuhrten Arbeiten zusammen."
de_cas = get_preprocessed_cas(text=de_example, language='de')
SE_FiniteVerbAnnotator('de').process(de_cas)
SE_SpellErrorAnnotator('de').process(de_cas)
vis_de_finite_verbs(de_cas)

fr_example = """
La première émission de lumière par un semi-conducteur date de 1907 et est découverte par Henry Round, ingénieur chez Marconi. 
En 1927, le russe Oleg Lossev dépose le premier brevet de ce qui sera appelé plus tard une diode électroluminescente, mais les applications peinent à émerger, 
le carbure de silicium alors utilisé comme semi-conducteur ayant de piètres propriétés électroluminescentes.
"""
fr_cas = get_preprocessed_cas(text=fr_example, language='fr')
SE_TokenZipfFrequency('fr').process(fr_cas)
vis_fr_frequency(fr_cas)