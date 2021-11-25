package org.lift.features.util;

import java.util.ArrayList;
import java.util.List;
import java.util.Map.Entry;
import java.util.Set;

import org.apache.commons.lang3.StringUtils;
import org.apache.uima.cas.text.AnnotationFS;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.apache.uima.jcas.tcas.Annotation;
import org.dkpro.core.api.featurepath.FeaturePathException;
import org.dkpro.core.api.featurepath.FeaturePathFactory;
import org.dkpro.core.api.frequency.util.FrequencyDistribution;
import org.dkpro.core.ngrams.util.NGramStringListIterable;
import org.lift.api.LiftFeatureExtrationException;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence;

public class NGramUtils {

	public static FrequencyDistribution<String> getDocumentNgrams(JCas jcas,
            boolean lowerCaseNGrams, boolean filterPartialMatches, int minN, int maxN,
            Set<String> stopwords, Class<? extends Annotation> annotationClass) throws LiftFeatureExtrationException {
        FrequencyDistribution<String> documentNgrams = new FrequencyDistribution<String>();
        for (Sentence s : JCasUtil.select(jcas, Sentence.class)) {
            List<String> strings = valuesToText(jcas, s, annotationClass.getName());
            for (List<String> ngram : new NGramStringListIterable(strings, minN, maxN)) {
                if (lowerCaseNGrams) {
                    ngram = lower(ngram);
                }

                if (passesNgramFilter(ngram, stopwords, filterPartialMatches)) {
                    String ngramString = StringUtils.join(ngram, "_");
                    documentNgrams.inc(ngramString);
                }
            }
        }
        return documentNgrams;
    }
	
	public static boolean passesNgramFilter(List<String> tokenList, Set<String> stopwords,
            boolean filterPartialMatches) {
        List<String> filteredList = new ArrayList<String>();
        for (String ngram : tokenList) {
            if (!stopwords.contains(ngram)) {
                filteredList.add(ngram);
            }
        }

        if (filterPartialMatches) {
            return filteredList.size() == tokenList.size();
        }
        else {
            return filteredList.size() != 0;
        }
    }
	
	public static List<String> lower(List<String> ngram) {
        List<String> newNgram = new ArrayList<String>();
        for (String token : ngram) {
            newNgram.add(token.toLowerCase());
        }
        return newNgram;
    }
	
	public static <T extends Annotation> List<String> valuesToText(JCas jcas, Sentence s,
            String annotationClassName) throws LiftFeatureExtrationException {
        List<String> texts = new ArrayList<String>();

        try {
            for (Entry<AnnotationFS, String> entry : FeaturePathFactory.select(jcas.getCas(),
                    annotationClassName)) {
                if (entry.getKey().getBegin() >= s.getBegin()
                        && entry.getKey().getEnd() <= s.getEnd()) {
                    texts.add(entry.getValue());
                }
            }
        }
        catch (FeaturePathException e) {
            throw new LiftFeatureExtrationException(e);
        }
        return texts;
    }
    
}
