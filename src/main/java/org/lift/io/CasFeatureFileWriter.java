package org.lift.io;

import java.io.FileNotFoundException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.uima.collection.CollectionReaderDescription;
import org.apache.uima.fit.pipeline.JCasIterable;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.LiftFeatureExtrationException;

import de.tudarmstadt.ukp.dkpro.core.api.metadata.type.DocumentMetaData;

public class CasFeatureFileWriter {

	public static void writeFeatureFile(String filePath, CollectionReaderDescription reader) throws LiftFeatureExtrationException, FileNotFoundException {
		Map<String, Set<Feature>> idFeatureMap = new HashMap<>();
		for (JCas jcas : new JCasIterable(reader)) {
			Set<Feature> featureSet = writeFeatureSet(jcas);
			String id = getDocumentId(jcas);
			idFeatureMap.put(id, featureSet);
		}
		writeCSVFile(filePath, idFeatureMap);
	}
	
	public static void writeFeatureFile(String filePath, List<JCas> casList) throws LiftFeatureExtrationException, FileNotFoundException {
		Map<String, Set<Feature>> idFeatureMap = new HashMap<>();
		for (JCas jcas : casList) {
			Set<Feature> featureSet = writeFeatureSet(jcas);
			String id = getDocumentId(jcas);
			idFeatureMap.put(id, featureSet);
		}
		writeCSVFile(filePath, idFeatureMap);
	}
	
	private static Set<Feature> writeFeatureSet(JCas jcas) throws LiftFeatureExtrationException {
		return FeatureSetBuilder.buildFeatureSet(jcas);
	}
	
	private static void writeCSVFile(String filePath, Map<String, Set<Feature>> idFeatureMap) throws FileNotFoundException {
		FeatureCSVFileWriter.writeCSVFile(filePath, idFeatureMap);
	}
	
	private static String getDocumentId(JCas jcas) {
		return DocumentMetaData.get(jcas).getDocumentId();
	}
	
}
