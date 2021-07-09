package org.lift.preprocessing;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;

import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.fit.component.NoOpAnnotator;
import org.apache.uima.resource.ResourceInitializationException;
import org.dkpro.core.corenlp.CoreNlpDependencyParser;
import org.dkpro.core.corenlp.CoreNlpLemmatizer;
import org.dkpro.core.corenlp.CoreNlpNamedEntityRecognizer;
import org.dkpro.core.corenlp.CoreNlpParser;
import org.dkpro.core.corenlp.CoreNlpPosTagger;
import org.dkpro.core.corenlp.CoreNlpSegmenter;
import org.dkpro.core.languagetool.LanguageToolChecker;
import org.dkpro.core.matetools.MateLemmatizer;
import org.dkpro.core.opennlp.OpenNlpChunker;
import org.dkpro.core.opennlp.OpenNlpPosTagger;
import org.dkpro.core.opennlp.OpenNlpSegmenter;
import org.dkpro.core.stanfordnlp.StanfordNamedEntityRecognizer;



public class Utils {

	
	public static AnalysisEngineDescription getPreprocessing(String languageCode) throws ResourceInitializationException {
		AnalysisEngineDescription segmenter       = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription tagger       = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription checker   = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription lemmatizer   = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription chunker   = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription ner   = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription constituentParser       = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription dependencyParser       = createEngineDescription(NoOpAnnotator.class);


		if (languageCode.equals("en")){
			segmenter = createEngineDescription(CoreNlpSegmenter.class,
					CoreNlpSegmenter.PARAM_LANGUAGE, "en");
			checker = createEngineDescription(LanguageToolChecker.class,
					CoreNlpSegmenter.PARAM_LANGUAGE, "en");
			tagger = createEngineDescription(CoreNlpPosTagger.class,
					CoreNlpPosTagger.PARAM_LANGUAGE, "en");
			lemmatizer = createEngineDescription(CoreNlpLemmatizer.class);
			chunker = createEngineDescription(OpenNlpChunker.class,
					OpenNlpChunker.PARAM_LANGUAGE, "en");
			ner = createEngineDescription(StanfordNamedEntityRecognizer.class,
					StanfordNamedEntityRecognizer.PARAM_LANGUAGE,"en");
			constituentParser = createEngineDescription(CoreNlpParser.class,
					CoreNlpParser.PARAM_LANGUAGE, "en",
					CoreNlpParser.PARAM_WRITE_PENN_TREE,true,
					CoreNlpParser.PARAM_WRITE_POS,false,
					CoreNlpParser.PARAM_PRINT_TAGSET,false,
					CoreNlpParser.PARAM_VARIANT, "pcfg");
			dependencyParser = createEngineDescription(CoreNlpDependencyParser.class,
					CoreNlpDependencyParser.PARAM_LANGUAGE, "en",
					CoreNlpDependencyParser.PARAM_PRINT_TAGSET,false);
		} else if (languageCode.equals("de")){
			segmenter = createEngineDescription(CoreNlpSegmenter.class,
					CoreNlpSegmenter.PARAM_LANGUAGE, "de");
			checker = createEngineDescription(LanguageToolChecker.class,
					CoreNlpSegmenter.PARAM_LANGUAGE, "de");
			tagger = createEngineDescription(CoreNlpPosTagger.class,
					CoreNlpPosTagger.PARAM_LANGUAGE, "de");
			lemmatizer = createEngineDescription(MateLemmatizer.class);
			ner = createEngineDescription(StanfordNamedEntityRecognizer.class,
					StanfordNamedEntityRecognizer.PARAM_LANGUAGE,"de");
			constituentParser = createEngineDescription(CoreNlpParser.class,
					CoreNlpParser.PARAM_LANGUAGE, "de",
					CoreNlpParser.PARAM_WRITE_PENN_TREE,true,
					CoreNlpParser.PARAM_WRITE_POS,false,
					CoreNlpParser.PARAM_PRINT_TAGSET,false,
					CoreNlpParser.PARAM_VARIANT, "pcfg");
			dependencyParser = createEngineDescription(CoreNlpDependencyParser.class,
					CoreNlpDependencyParser.PARAM_LANGUAGE, "de",
					CoreNlpDependencyParser.PARAM_PRINT_TAGSET,false,
					CoreNlpDependencyParser.PARAM_VARIANT, "ud");
		} else {
			System.err.println("Unknown language code "+languageCode+". We currently support: en, de");
			System.exit(-1);
		}
		return createEngineDescription(
				segmenter,
				tagger,
				checker,
				lemmatizer,
				chunker,
				ner,
				constituentParser,
				dependencyParser
				);
	}
	
	
	
	
	
	
	
	
	
}
