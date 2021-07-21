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
public class FE_CommaRatioAlternative 
	extends FE_GenericCounter
{

	// TODO better way to initialize this
	private static String fp = Token.class.getName();
	private static Predicate<String> pred = feature -> feature.equals(",");
	
	public FE_CommaRatioAlternative() {
		super(fp, pred);
	}
}