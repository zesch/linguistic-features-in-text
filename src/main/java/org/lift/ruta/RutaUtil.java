package org.lift.ruta;

import java.io.IOException;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.List;

import org.antlr.runtime.RecognitionException;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.apache.uima.UIMAFramework;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.fit.factory.TypeSystemDescriptionFactory;
import org.apache.uima.resource.ResourceInitializationException;
import org.apache.uima.resource.metadata.TypeSystemDescription;
import org.apache.uima.ruta.descriptor.RutaBuildOptions;
import org.apache.uima.ruta.descriptor.RutaDescriptorFactory;
import org.apache.uima.ruta.descriptor.RutaDescriptorInformation;
import org.apache.uima.ruta.engine.RutaEngine;
import org.apache.uima.util.CasCreationUtils;
import org.apache.uima.util.InvalidXMLException;

public class RutaUtil {

	public static Pair<AnalysisEngineDescription, TypeSystemDescription> initRutaFE(String rutaScript) 
			throws IOException, RecognitionException, InvalidXMLException, ResourceInitializationException, URISyntaxException
	{
		RutaDescriptorFactory descriptorFactory = new RutaDescriptorFactory();
		
		RutaBuildOptions options = new RutaBuildOptions();
		options.setResolveImports(true);
		options.setImportByName(true);
		
		RutaDescriptorInformation descriptorInformation = descriptorFactory.parseDescriptorInformation(rutaScript, options);
		// replace null values for build environment if necessary (e.g., location in classpath)
		Pair<AnalysisEngineDescription, TypeSystemDescription> descs = descriptorFactory.createDescriptions(null, null, descriptorInformation, options, null, null, null);
		
		AnalysisEngineDescription rutaAED = descs.getKey();
		TypeSystemDescription rutaTSD = descs.getValue();

		rutaAED.getAnalysisEngineMetaData().getConfigurationParameterSettings().setParameterValue(RutaEngine.PARAM_RULES, rutaScript);
		rutaAED.getAnalysisEngineMetaData().setTypeSystem(rutaTSD);
		
		TypeSystemDescription scannedTSD = TypeSystemDescriptionFactory.createTypeSystemDescription();
		List<TypeSystemDescription> tsds = new ArrayList<>();
		tsds.add(scannedTSD);
		tsds.add(rutaTSD);
		TypeSystemDescription mergeTypeSystemDescription = CasCreationUtils.mergeTypeSystems(tsds, UIMAFramework.newDefaultResourceManager());

	    return new ImmutablePair<AnalysisEngineDescription, TypeSystemDescription>(
	            rutaAED, mergeTypeSystemDescription);
	}
}
