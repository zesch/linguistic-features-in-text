package org.lift.features;

import java.util.function.Predicate;

import org.apache.uima.fit.descriptor.LanguageCapability;
import org.apache.uima.fit.descriptor.TypeCapability;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * Counts the number of commas
 */
@TypeCapability(inputs = { "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"})
@LanguageCapability({ "de","en" })
public class NrOfCommasAlternative 
	extends CountFE
{

	// TODO better way to initialize this
	private static String name = "commaCount";
	private static String fp = Token.class.getName();
	private static Predicate<String> pred = feature -> feature.equals(",");
	
	public NrOfCommasAlternative() {
		this(name, fp, pred);
	}
	public NrOfCommasAlternative(String name, String featurePath, Predicate<String> isFeature) {
		super(name, featurePath, isFeature);
	}
}