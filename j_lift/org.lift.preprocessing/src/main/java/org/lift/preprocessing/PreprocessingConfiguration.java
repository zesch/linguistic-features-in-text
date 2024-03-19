package org.lift.preprocessing;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;

import java.util.ArrayList;
import java.util.List;

import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.fit.component.NoOpAnnotator;
import org.apache.uima.resource.ResourceInitializationException;
import org.dkpro.core.corenlp.CoreNlpDependencyParser;
import org.dkpro.core.corenlp.CoreNlpLemmatizer;
import org.dkpro.core.corenlp.CoreNlpParser;
import org.dkpro.core.corenlp.CoreNlpPosTagger;
import org.dkpro.core.corenlp.CoreNlpSegmenter;
import org.dkpro.core.languagetool.LanguageToolChecker;
import org.dkpro.core.matetools.MateLemmatizer;
import org.dkpro.core.matetools.MateMorphTagger;
import org.dkpro.core.opennlp.OpenNlpChunker;
import org.dkpro.core.stanfordnlp.StanfordNamedEntityRecognizer;
import org.lift.api.Configuration.Language;

public class PreprocessingConfiguration {

	private List<AnalysisEngineDescription> components;
	private Language language;
	
	public PreprocessingConfiguration(Language language) 
			throws ResourceInitializationException
	{
		this.language = language;
		this.components = new ArrayList<>();
		
		AnalysisEngineDescription segmenter = getSegmenter_CoreNLP(language.code);		
		AnalysisEngineDescription tagger    = getTagger_CoreNLP(language.code);
		AnalysisEngineDescription checker   = getChecker_LanguageTool(language.code);
		AnalysisEngineDescription ner       = getNER_Stanford(language.code);
		
		AnalysisEngineDescription lemmatizer 	= createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription morphTagger   = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription chunker    	= createEngineDescription(NoOpAnnotator.class);
		
		AnalysisEngineDescription constituentParser = getParser_CoreNLP(language.code);
		AnalysisEngineDescription dependencyParser  = getDepParser_CoreNLP(language.code);

		// overwrite defaults with language specific stuff if needed 
		if (language.equals(Language.English)){

			lemmatizer = createEngineDescription(
					CoreNlpLemmatizer.class
			);
			chunker = createEngineDescription(
					OpenNlpChunker.class,
					OpenNlpChunker.PARAM_LANGUAGE, Language.English.code
			);
		} 
		
		if (language.equals(Language.German)) {

			// TODO German chunker?
			
			lemmatizer = createEngineDescription(
					MateLemmatizer.class,
					MateLemmatizer.PARAM_LANGUAGE, Language.German.code);
			morphTagger = createEngineDescription(
					MateMorphTagger.class,
					MateMorphTagger.PARAM_LANGUAGE, Language.German.code);

		} 
		
		// add components to list (careful, order matters!) 
		components.add(segmenter);
		components.add(tagger);
		components.add(checker);
		components.add(lemmatizer);
		components.add(morphTagger);
		components.add(chunker);
		components.add(ner);
		components.add(constituentParser);
		components.add(dependencyParser);
	}
	
	public AnalysisEngineDescription getUimaEngineDescription() 
			throws ResourceInitializationException
	{
		return createEngineDescription(components.toArray(new AnalysisEngineDescription[0]));
	}
	
	public Language getLanguage() {
		return language;
	}
	
	private AnalysisEngineDescription getSegmenter_CoreNLP(String languageCode) 
			throws ResourceInitializationException
	{
		return createEngineDescription(
				CoreNlpSegmenter.class,
				CoreNlpSegmenter.PARAM_LANGUAGE, languageCode
		);
	}
	
	private AnalysisEngineDescription getChecker_LanguageTool(String languageCode) 
			throws ResourceInitializationException
	{
		return createEngineDescription(
				LanguageToolChecker.class,
				LanguageToolChecker.PARAM_LANGUAGE, languageCode
		);
	}
	
	private AnalysisEngineDescription getTagger_CoreNLP(String languageCode) 
			throws ResourceInitializationException
	{
		return createEngineDescription(
				CoreNlpPosTagger.class,
				CoreNlpPosTagger.PARAM_LANGUAGE, languageCode
		);
	}
	
	private AnalysisEngineDescription getNER_Stanford(String languageCode) 
			throws ResourceInitializationException
	{
		return createEngineDescription(
				StanfordNamedEntityRecognizer.class,
				StanfordNamedEntityRecognizer.PARAM_LANGUAGE, languageCode
		);
	}
	
	private AnalysisEngineDescription getParser_CoreNLP(String languageCode) 
			throws ResourceInitializationException
	{
		return createEngineDescription(
				CoreNlpParser.class,
				CoreNlpParser.PARAM_LANGUAGE, languageCode,
				CoreNlpParser.PARAM_WRITE_PENN_TREE, true,
				CoreNlpParser.PARAM_WRITE_POS, false,
				CoreNlpParser.PARAM_PRINT_TAGSET, false,
				CoreNlpParser.PARAM_VARIANT, "pcfg"
		);
	}
	
	private AnalysisEngineDescription getDepParser_CoreNLP(String languageCode) 
			throws ResourceInitializationException
	{
		return createEngineDescription(
				CoreNlpDependencyParser.class,
				CoreNlpDependencyParser.PARAM_LANGUAGE, languageCode,
				CoreNlpDependencyParser.PARAM_PRINT_TAGSET, false,
				CoreNlpDependencyParser.PARAM_VARIANT, "ud"
		);
	}
}