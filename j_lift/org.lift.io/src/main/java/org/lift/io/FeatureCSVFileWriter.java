package org.lift.io;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.util.Map;
import java.util.Set;

import org.lift.api.Feature;

public class FeatureCSVFileWriter {

	public static void writeCSVFile(String filePath, Map<String, Set<Feature>> idFeatureMap) throws FileNotFoundException {
		StringBuilder builder = new StringBuilder();
		
		idFeatureMap.values().stream()
			.findFirst()
			.map(feat -> writeColumnNames(feat))
			.map(builder::append)
			.orElseThrow(() -> new IllegalArgumentException("FeatureSet is Empty, therefore there is no point in writing the CSV-File"));
		builder.append("\n");
		
		idFeatureMap.keySet().stream()
			.map(key -> writeRow(key, idFeatureMap.get(key)))
			.map(builder::append);
		
		PrintWriter pw = new PrintWriter(new File(filePath));
		pw.write(builder.toString());
		pw.close();
	}
	
	private static String writeColumnNames(Set<Feature> features) {
		StringBuilder builder = new StringBuilder();
		builder.append("textId");
		for (Feature feature : features) {
			builder.append(",");
			builder.append(feature.getName());
		}
		return builder.toString();
	}
	
	private static String writeRow(String id, Set<Feature> features) {
		StringBuilder builder = new StringBuilder();
		builder.append(id);
		for (Feature feature : features) {
			builder.append(",");
			builder.append(feature.getValue().toString());
		}
		builder.append("\n");
		return builder.toString();
	}
}
