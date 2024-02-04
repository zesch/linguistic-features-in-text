package org.lift.features.util;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.fit.component.NoOpAnnotator;
import org.apache.uima.resource.ResourceInitializationException;
import org.dkpro.core.corenlp.CoreNlpDependencyParser;
import org.dkpro.core.corenlp.CoreNlpLemmatizer;
import org.dkpro.core.corenlp.CoreNlpPosTagger;
import org.dkpro.core.corenlp.CoreNlpSegmenter;
import org.dkpro.core.matetools.MateLemmatizer;
import org.dkpro.core.opennlp.OpenNlpChunker;
import org.dkpro.core.stanfordnlp.StanfordParser;
import org.lift.api.Configuration.Language;

//import de.tudarmstadt.ukp.dkpro.core.matetools.MateLemmatizer;
//import de.tudarmstadt.ukp.dkpro.core.matetools.MateParser;


public class TestBase {

	public enum ParserType {
		noParser,
		constituentParser,
		dependencyParser
	}

	public static AnalysisEngine getPreprocessingEngine(String lang, ParserType parser)
			throws ResourceInitializationException
	{
		AnalysisEngineDescription segmenter = createEngineDescription(
				CoreNlpSegmenter.class,
				CoreNlpSegmenter.PARAM_LANGUAGE, lang
		);
		AnalysisEngineDescription posTagger = createEngineDescription(
				CoreNlpPosTagger.class,
				CoreNlpPosTagger.PARAM_LANGUAGE, lang
		);
		AnalysisEngineDescription chunker = createEngineDescription(OpenNlpChunker.class, CoreNlpPosTagger.PARAM_LANGUAGE, lang);
		AnalysisEngineDescription lemmatizer = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription constituentParser = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription dependencyParser = createEngineDescription(NoOpAnnotator.class);
		
		// overwrite defaults with language specific stuff if needed 
		if (lang.equals("en")){

			lemmatizer = createEngineDescription(
					CoreNlpLemmatizer.class
			);
		} 
		
		if (lang.equals("de")) {

			// TODO German chunker?
			
			lemmatizer = createEngineDescription(
					MateLemmatizer.class,
					MateLemmatizer.PARAM_LANGUAGE, Language.German.code);

		} 
		constituentParser = createEngineDescription(StanfordParser.class,
				StanfordParser.PARAM_LANGUAGE, lang,
				StanfordParser.PARAM_WRITE_PENN_TREE, true,
				StanfordParser.PARAM_WRITE_POS, false,
				StanfordParser.PARAM_PRINT_TAGSET,false,
				StanfordParser.PARAM_VARIANT, "pcfg");
		


		if (lang.equals("de")&&parser.equals(ParserType.noParser)){
			System.out.println("Build test engine WITHOUT parser for German...");
			AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger,lemmatizer);
			return createEngine(description);
		} else if(lang.equals("de")&&parser.equals(ParserType.constituentParser)){
			System.out.println("Build test engine WITH constituent parser for German...");
			AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger,lemmatizer,constituentParser);	
			return createEngine(description);
		} else if(lang.equals("de")&&parser.equals(ParserType.dependencyParser)){
			System.out.println("Build test engine WITH dependency parser for German...");
			AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger,lemmatizer,dependencyParser);	
			return createEngine(description);
		} else if(lang.equals("en")&&parser.equals(ParserType.noParser)){
			System.out.println("Build test engine WITHOUT parser for English...");
			AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger,chunker, lemmatizer);
			return createEngine(description);
		} else if(lang.equals("en")&&parser.equals(ParserType.constituentParser)){
			System.out.println("Build test engine WITH parser for English...");
			AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger,chunker,lemmatizer,constituentParser);	
			return createEngine(description);
		}else if(lang.equals("en")&&parser.equals(ParserType.dependencyParser)){
			System.out.println("Build test engine WITH dependency parser for English...");
			AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger,lemmatizer,dependencyParser);	
			return createEngine(description);
		}else {
			return null;
		}
	}

}
