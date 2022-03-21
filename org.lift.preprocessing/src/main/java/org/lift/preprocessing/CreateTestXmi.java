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
import org.lift.api.Configuration.Language;



public class CreateTestXmi {

	public static void main(String[] args) 
			throws Exception
	{
//		runTextExample("src/test/resources/txt/essay_en.txt", Language.English);
		runTextExample("src/test/resources/txt/active_passive_en.txt", Language.English);
//		runTextExample("src/test/resources/txt/news_de.txt", Language.German);
	}
		
	private static void runTextExample(String sourceDir, Language language) throws ResourceInitializationException, UIMAException, IOException {
		PreprocessingConfiguration config = new PreprocessingConfiguration(language);
				
		CollectionReaderDescription reader = CollectionReaderFactory.createReaderDescription(
				TextReader.class,
				TextReader.PARAM_LANGUAGE, language.code,
				TextReader.PARAM_SOURCE_LOCATION, sourceDir
		);

		AnalysisEngineDescription prepro = config.getUimaEngineDescription();
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