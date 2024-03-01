package org.lift.structures;

import static org.lift.util.ResourceUtils.getSharedResourceAsStream;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;

import org.apache.commons.io.IOUtils;
import org.apache.uima.UimaContext;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.apache.uima.resource.ResourceInitializationException;
import org.lift.api.StructureExtractor;
import org.lift.type.CEFR;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

public class SE_FrequencyEVP 
	extends StructureExtractor
{
	
	private Map<Vocabulary, Integer> vocab;
	
	
	@Override
	public String getPublicStructureName() {
		return "FreqEVP";
	}
	
	@Override
	public void initialize(final UimaContext context) 
		throws ResourceInitializationException 
	{			
		try {
			vocab = readMapping(
				"evp/EVP.csv", 
				"evp/EVP_extension.csv"
			);
		} catch (IOException e) {
			throw new ResourceInitializationException(e);
		}
	}

	protected Map<Vocabulary, Integer> readMapping(String listFilePath1, String listFilePath2) 
		throws IOException, ResourceInitializationException
	{
		 
		// TODO the list also contains phrases, how to handle?
		
		 InputStream is1 = getSharedResourceAsStream(this.getClass(), listFilePath1);
		 Map<Vocabulary, Integer> map = new HashMap<Vocabulary, Integer>();
		 for (String line : IOUtils.readLines(is1, StandardCharsets.UTF_8)) {
				String[] parts = line.split(",");
				String wordName = parts[0].toLowerCase();
				String wordType = parts[1].toLowerCase();
				
				int level = 1;
				try {
					level = Integer.parseInt(parts[2]);
				}
				catch(NumberFormatException e) {
					throw new IOException(e);
				}
				
				Vocabulary vo = new Vocabulary(wordName, wordType);
				if (!map.containsKey(vo)) {
					map.put(new Vocabulary(wordName, wordType), level);
				}
		 }

		 
		 // TODO code duplication, consider wrapping in method
		 
		 InputStream is2 = getSharedResourceAsStream(this.getClass(), listFilePath2);
		 for (String line : IOUtils.readLines(is2, StandardCharsets.UTF_8)) {
				String[] parts = line.split(",");
				String wordName = parts[0].toLowerCase();
				String wordType = parts[1].toLowerCase();
				int level = Integer.parseInt(parts[2]);
				map.put(new Vocabulary(wordName, wordType), level);
		 }	
		 return map;
	 }

	@Override
	public void process(JCas aJCas) throws AnalysisEngineProcessException {
		
		// TODO do we need this?
		//This data needs to be written (Object[])
        Map<String, Object[]> data = new TreeMap<String, Object[]>();
		
		for (Token t : JCasUtil.select(aJCas, Token.class)){
			String lemma = t.getLemma().getValue().toLowerCase();
//			String pOS =   t.getPos().getPosValue();
			String wordType = "";

			// TODO consider switch statement for readability
			//change Tagset to compaire with types of words in the EVP-Wordlist
			if (t.getPos().getCoarseValue() != null) {
				if (t.getPos().getCoarseValue().equals("NOUN")){
					wordType = "noun";
				}
				else if(t.getPos().getCoarseValue().equals("VERB")) {
					wordType = "verb";
				}else if(t.getPos().getCoarseValue().equals("ADJ")) {
					wordType = "adjective";
				}else if(t.getPos().getCoarseValue().equals("DET")) {
					wordType = "determiner";
				}else if(t.getPos().getCoarseValue().equals("ADV")) {
					wordType = "adverb";
				}else if(t.getPos().getCoarseValue().equals("ADP")) {
					wordType = "preposition";
				}else if(t.getPos().getCoarseValue().equals("PRON")) {
					wordType = "pronoun";
				}else if(t.getPos().getCoarseValue().equals("NUM")) {
					wordType = "NUM";	
				}else {
					wordType = "none";
				}
			}
			Vocabulary vocabulary = new Vocabulary(lemma,wordType);
			
			if (vocab.containsKey(vocabulary)){ 
				CEFR f = new CEFR(aJCas); 
				f.setBegin(t.getBegin());
				f.setEnd(t.getEnd()); 
				f.setLevel(computeFrequencyBand(vocab.get(vocabulary)));
				f.addToIndexes(); 
			}
		}		
		
	}
	
	private String computeFrequencyBand(double frequencyValue) {
		String level="";
		
		// TODO consider switch for readability
		if (frequencyValue == 1.0) {
			level = "A1";
		}
		if (frequencyValue == 2.0) {
			level = "A2";
		}
		if (frequencyValue == 3.0) {
			level = "B1";
		}
		if (frequencyValue == 4.0) {
			level = "B2";
		}
		if (frequencyValue == 5.0) {
			level = "C1";
		}
		if (frequencyValue == 6.0) {
			level = "C2";
		}
		return level;
	}

	class Vocabulary{
		private String wordName;
		private String wordType ;
		public Vocabulary(String wordName, String wordType) {
			super();
			this.wordName = wordName;
			this.wordType = wordType;
		}
		public String getWordName() {
			return wordName;
		}
		public void setWordName(String name) {
			this.wordName = name;
		}
		public String getWordType() {
			return wordType;
		}
		public void setWordType(String pos) {
			this.wordType = pos;
		}
		@Override
		public int hashCode() {
		    final int prime = 31;
		    int result = 1;
		    result = prime * result + ((wordName == null) ? 0 : wordName.hashCode());
		    result = prime * result + ((wordType == null) ? 0 : wordType.hashCode());
		    return result;
		}
		
		@Override
	    public boolean equals(Object o) {
	        if (this == o) {
	            return true;
	        }
	        if (o == null || getClass() != o.getClass()) {
	            return false;
	        }
	        Vocabulary vocabulary = (Vocabulary) o;
	        return wordName.equals(vocabulary.wordName) &&
	               wordType.equals(vocabulary.wordType);
	    }
	}
}