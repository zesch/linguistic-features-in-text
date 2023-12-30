package org.lift.io;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.component.NoOpAnnotator;
import org.apache.uima.jcas.JCas;
import org.apache.uima.resource.ResourceInitializationException;
import org.dkpro.core.matetools.MateLemmatizer;
import org.dkpro.core.opennlp.OpenNlpChunker;
import org.dkpro.core.opennlp.OpenNlpPosTagger;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.dkpro.core.treetagger.TreeTaggerChunker;

import de.tudarmstadt.ukp.dkpro.core.api.metadata.type.DocumentMetaData;

public class TextPreprocessor {

	public static JCas preprocess(String id, String text, String languageCode) throws AnalysisEngineProcessException, ResourceInitializationException {
		JCas cas = preprocessText(text, languageCode);
		createDocumentMetaData(cas, id);
		return cas;
	}
	
	private static JCas preprocessText(String text, String languageCode) throws AnalysisEngineProcessException, ResourceInitializationException {
		switch(languageCode) {
			case "de": return preprocessGerman(text);
			case "en": return preprocessEnglish(text);
			default: throw new IllegalArgumentException("languageCode could not be resolved");
		}		
	}
	
	
	private static void createDocumentMetaData(JCas cas, String id) {
		DocumentMetaData metaData = DocumentMetaData.create(cas);
		metaData.setDocumentId(id);
	}
	
	private static JCas preprocessEnglish(String text) throws ResourceInitializationException, AnalysisEngineProcessException {
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription chunker = createEngineDescription(OpenNlpChunker.class);
		AnalysisEngineDescription lemmatizer = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter, posTagger, chunker, lemmatizer);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("en");
        jcas.setDocumentText(text);
        engine.process(jcas);
        
        return jcas;
	}
	
	private static JCas preprocessGerman(String text) throws ResourceInitializationException, AnalysisEngineProcessException {
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription chunker = createEngineDescription(TreeTaggerChunker.class); //Problematisch, Alternativen?
		AnalysisEngineDescription lemmatizer = createEngineDescription(MateLemmatizer.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter, posTagger, chunker, lemmatizer);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("de");
		jcas.setDocumentText(text);
		engine.process(jcas);
		
		return jcas;
	}
}
