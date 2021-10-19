package org.lift.features;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.type.Structure;

public class FEL_AvgStructureRatio extends FeatureExtractor_ImplBase {
	
	private final String dividendStructurePath;
	private final String divisorStructurePath;

	public FEL_AvgStructureRatio(String dividendStructurePath, String divisorStructurePath) {
		super(dividendStructurePath + "_PER_" + divisorStructurePath, FEL_AvgStructureRatio.class.getName() + "__" + dividendStructurePath + "_PER_" + divisorStructurePath);
		this.dividendStructurePath = dividendStructurePath;
		this.divisorStructurePath = divisorStructurePath;
	}

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		Set<Feature> featureSet = new HashSet<Feature>();
		
		Collection<Structure> structures = JCasUtil.select(jcas, Structure.class);
		double numDividends = 0;
		double numDivisors = 0;
		
		for (Structure structure : structures) {
			String structureName = structure.getName();
			if(structureName.equals(dividendStructurePath)) {
				numDividends++;
			} else if(structureName.equals(divisorStructurePath)) {
				numDivisors++;
			}
		}
		
		double avgSize = numDividends / numDivisors;
		
		featureSet.add(new Feature("FN_" + dividendStructurePath + "_PER_" + divisorStructurePath, avgSize, FeatureType.NUMERIC));
		return featureSet;
	}

}
