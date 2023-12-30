/*******************************************************************************
 * Copyright 2019
 * Ubiquitous Knowledge Processing (UKP) Lab
 * Technische Universität Darmstadt
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *   http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 ******************************************************************************/
package org.lift.api;


import java.util.Set;

import org.apache.uima.jcas.JCas;
import org.lift.type.FeatureAnnotationNumeric;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.component.JCasAnnotator_ImplBase;

/**
 * Common signature for feature extractors which extract their features from the entire document or
 * from a given classification unit.
 * 
 */
public abstract class FeatureExtractorAndAnnotator extends JCasAnnotator_ImplBase implements FeatureExtractor
{
	
	@Override
	public void process(JCas jcas) throws AnalysisEngineProcessException {
		try {
			Set<Feature> features = this.extract(jcas);
			for (Feature f : features) {
				String name = f.getName();
				FeatureType featureType = f.getType();
				Object value = f.getValue();
				FeatureAnnotationNumeric fa = new FeatureAnnotationNumeric(jcas, 0, 0);
				fa.setName(name);
				fa.setValue((double) value);
				fa.addToIndexes();
			}
		} catch (LiftFeatureExtrationException e) {
			throw new AnalysisEngineProcessException();
		}
	}
   
}
