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

/**
 * Common signature for feature extractors which extract their features from the entire document or
 * from a given classification unit.
 * 
 */
public interface FeatureExtractor
{
	
//    /**
//     * Extract features from the classification target within the given view.
//     * 
//     * @param text
//     *            the text of the document
//     * @return a set of features generated by the extractor 
//     * @throws TextClassificationException
//     *             if feature extraction failed
//     */
//    Set<Feature> extract(String text)
//        throws LiftFeatureExtrationException;
    
    /**
     * Extract features from the classification target within the given view.
     * 
     * @param jcas
     *            the current view of the document.
     * @return a set of features generated by the extractor
     * @throws TextClassificationException
     *             if feature extraction failed
     */
    public Set<Feature> extract(JCas jcas)
        throws LiftFeatureExtrationException;

    public String getPublicName();
    public String getInternalName();
}
