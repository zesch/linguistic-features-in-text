package org.lift.preprocessing;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;

import java.io.IOException;

import org.apache.uima.UIMAException;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.collection.CollectionReaderDescription;
import org.apache.uima.fit.factory.CollectionReaderFactory;
import org.apache.uima.fit.pipeline.SimplePipeline;
import org.apache.uima.resource.ResourceInitializationException;
import org.dkpro.core.io.text.TextReader;
import org.dkpro.core.io.xmi.XmiWriter;



public class BaseExperiment {

	public static void main(String[] args) throws ResourceInitializationException, UIMAException, IOException{
		runGermanTextExample();
		runEnglishTextExample();
	}
	
	private static void runEnglishTextExample() throws ResourceInitializationException, UIMAException, IOException {
		runTextExample("src/test/resources/txt/essay_en.txt", "en");
	}

	
	private static void runGermanTextExample() throws ResourceInitializationException, UIMAException, IOException {
		runTextExample("src/test/resources/txt/news_de.txt", "de");
	}
	
	private static void runTextExample(String sourceDir, String languageCode) throws ResourceInitializationException, UIMAException, IOException {
		CollectionReaderDescription reader = CollectionReaderFactory.createReaderDescription(
				TextReader.class,
				TextReader.PARAM_LANGUAGE, languageCode,
				TextReader.PARAM_SOURCE_LOCATION, sourceDir);

		AnalysisEngineDescription prepro = Utils.getPreprocessing(languageCode);
		AnalysisEngineDescription analyzer = createEngineDescription(Analyzer.class);
		AnalysisEngineDescription xmiWriter = createEngineDescription(
				XmiWriter.class, 
				XmiWriter.PARAM_OVERWRITE, true,
				XmiWriter.PARAM_TARGET_LOCATION, "target/cas"
				);
		SimplePipeline.runPipeline(reader, 
				prepro,
				analyzer,
				xmiWriter
				);
	}
	
	
	
}
